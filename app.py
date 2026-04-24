from fastapi import FastAPI
from main import run

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API running"}

@app.get("/predict")   # ⚠️ PHẢI CÓ DÒNG NÀY
def predict():
    return run()