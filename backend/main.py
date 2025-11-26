from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.predict import predict_weather_from_features

app = FastAPI(
    title="Weather Prediction API",
    description="Predict weather conditions using a trained ML model.",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Request Body Schema ----
class WeatherRequest(BaseModel):
    precipitation: float = Field(..., example=0.0)
    temp_max: float = Field(..., example=12.8)
    temp_min: float = Field(..., example=5.0)
    wind: float = Field(..., example=4.7)

# ---- API Routes ----
@app.get("/")
def root():
    return {"message": "Weather Prediction API is running!"}

@app.post("/predict")
def predict_weather(data: WeatherRequest):
    # Convert Pydantic model to list
    features = [
        data.precipitation,
        data.temp_max,
        data.temp_min,
        data.wind,
        data.temp_max - data.temp_min
    ]

    pred_label, confidence = predict_weather_from_features(features)

    return {
        "prediction": pred_label,
        "confidence_percent": round(confidence * 100, 2),
        "input_features": features
    }
