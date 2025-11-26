# main.py (FastAPI)
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.predict import predict_weather_from_features

app = FastAPI()

# Allow your frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# Incoming JSON structure
# ------------------------------------------------------------
class WeatherRequest(BaseModel):
    precipitation: float
    temp_max: float
    temp_min: float
    wind: float


# ------------------------------------------------------------
# Prediction Endpoint
# ------------------------------------------------------------
@app.post("/predict")
def predict_weather(data: WeatherRequest):

    pred_label, conf_percent = predict_weather_from_features(
        data.precipitation,
        data.temp_max,
        data.temp_min,
        data.wind,
    )

    return {
        "prediction": pred_label,
        "confidence_percent": round(conf_percent, 2),
        "input_features": {
            "precipitation": data.precipitation,
            "temp_max": data.temp_max,
            "temp_min": data.temp_min,
            "wind": data.wind,
            "temp_range": data.temp_max - data.temp_min,
        },
    }


@app.get("/")
def root():
    return {"message": "Weather prediction API is running!"}
