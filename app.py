from fastapi import FastAPI
from main import run

app = FastAPI()

# test server
@app.get("/")
def home():
    return {"message": "API running"}

# API chính
@app.get("/recommend")
def recommend():
    return run()