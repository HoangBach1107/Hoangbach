import requests
from datetime import datetime
from predict import recommend_temp

# ===== CONFIG =====
PEOPLE_API = "https://yolo-r92p.onrender.com/people"   # ⚠️ sửa đúng IP máy camera
WEATHER_API = "https://weather-api-real.onrender.com/weather?lat=16.0471&lon=108.2068"

TIMEOUT = 10
ROOM_SIZE = 25


# ===== GET OCCUPANCY =====
def get_occupancy():
    try:
        res = requests.get(PEOPLE_API, timeout=TIMEOUT)
        print("[CAMERA STATUS]:", res.status_code)

        data = res.json()
        print("[CAMERA DATA]:", data)

        # ❗ FIX: giữ được cả số 0
        if "people_count" in data:
            return data["people_count"]
        if "count" in data:
            return data["count"]
        if "people" in data:
            return data["people"]

        return None

    except Exception as e:
        print("[ERROR CAMERA]:", e)
        return None

# ===== GET WEATHER =====
def get_weather():
    for i in range(3):  # thử 3 lần
        try:
            res = requests.get(WEATHER_API, timeout=10)
            print("[WEATHER STATUS]:", res.status_code)

            data = res.json()
            print("[WEATHER DATA]:", data)

            humidity = (
                data.get("humidity") or
                data.get("current", {}).get("humidity")
            )

            outdoor_temp = (
                data.get("temperature") or
                data.get("temp") or
                data.get("current", {}).get("temp_c")
            )

            return humidity, outdoor_temp

        except Exception as e:
            print(f"[RETRY {i+1}] Weather error:", e)

    return None, None

# ===== MAIN LOGIC =====
def run():
    now = datetime.now()
    hour = now.hour
    day = now.weekday()

    occupancy = get_occupancy()
    humidity, outdoor_temp = get_weather()

    print("\n===== INPUT =====")
    print("Occupancy:", occupancy)
    print("Humidity:", humidity)
    print("Outdoor Temp:", outdoor_temp)

    # ❗ check API camera
    if occupancy is None:
        return {"error": "Camera API not available"}

    # ❗ check API weather
    if humidity is None or outdoor_temp is None:
        return {"error": "Weather API not available"}

    # ❗ không có người → tắt AC
    if occupancy == 0:
        return {
            "recommended_temp": None,
            "energy": 0,
            "note": "AC OFF - No occupants",
            "chart_data": []
        }

    # ===== CALL MODEL =====
    result = recommend_temp(
        humidity=humidity,
        hour=hour,
        day=day,
        occupancy=occupancy,
        room_size=ROOM_SIZE,
        outdoor_temp=outdoor_temp
    )

    return result


# ===== RUN =====
if __name__ == "__main__":
    print("=== START SYSTEM ===")

    output = run()

    print("\n=== RESULT ===")
    print(output)