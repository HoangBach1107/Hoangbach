import joblib
import pandas as pd
import numpy as np

model = joblib.load("energy_model.pkl")


def predict_energy(temp, humidity, hour, day, occupancy, room_size, outdoor_temp):
    sample = pd.DataFrame([{
        "z1_S1(degC)": temp,
        "z1_S1(RH%)": humidity,
        "hour": hour,
        "day_of_week": day,
        "occupancy": occupancy,
        "room_size": room_size,
        "outdoor_temp": outdoor_temp,
        "temp_x_occupancy": temp * occupancy
    }])

    pred = model.predict(sample)[0]
    return float(np.expm1(pred))


def recommend_temp(humidity, hour, day, occupancy, room_size, outdoor_temp):
    if room_size <= 0:
        return {"error": "Invalid room size"}

    if occupancy == 0:
        return {
            "recommended_temp": None,
            "energy": 0,
            "note": "AC OFF - No occupants",
            "chart_data": []
        }

    temps = [24, 25, 26, 27]
    chart_data = []

    for t in temps:
        energy = predict_energy(
            t, humidity, hour, day, occupancy, room_size, outdoor_temp
        )
        chart_data.append({"temp": t, "energy": energy})

    filtered = []

    for item in chart_data:
        t = item["temp"]

        if outdoor_temp is not None and outdoor_temp >= 38 and t > 25:
            continue

        if humidity >= 85 and t > 25:
            continue

        filtered.append(item)

    if not filtered:
        filtered = chart_data

    best = min(filtered, key=lambda x: x["energy"])
    recommended_temp = best["temp"]

    if outdoor_temp is not None:
        if outdoor_temp > 35:
            recommended_temp -= 1.5
        elif outdoor_temp < 20:
            recommended_temp += 1.5

    if room_size > 30:
        recommended_temp -= 1.5
    elif room_size < 15:
        recommended_temp += 1.5

    recommended_temp -= 0.05 * occupancy

    recommended_temp = round(max(24, min(recommended_temp, 26)))

    final_energy = predict_energy(
        recommended_temp, humidity, hour, day, occupancy, room_size, outdoor_temp
    )

    return {
        "recommended_temp": recommended_temp,
        "energy": final_energy,
        "note": "ML + Constraint + Rule-based",
        "chart_data": chart_data
    }