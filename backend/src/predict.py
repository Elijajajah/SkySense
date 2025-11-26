import os
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

# ------------------------------------------------------------
# FIX 1: Use absolute paths so FastAPI loads correct files
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(os.path.dirname(BASE_DIR), "models")

MODEL_PATH = os.path.join(MODEL_DIR, "weather_model.keras")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")
PROCESSED_PATH = os.path.join(BASE_DIR, "data/processed/weather_cleaned.csv")


# Load saved objects
scaler = joblib.load(SCALER_PATH)
le = joblib.load(ENCODER_PATH)
model = load_model(MODEL_PATH)

# The model was trained with these columns:
feature_cols = ["precipitation", "temp_max", "temp_min", "wind", "temp_range"]

# ------------------------------------------------------------
# Feature preparation helper (5 inputs)
# ------------------------------------------------------------
def prepare_features(precip, tmax, tmin, wind):
    """
    Prepares the features in the EXACT form used during training.
    Returns scaled numpy array of shape (1, 5)
    """
    temp_range = tmax - tmin
    raw = np.array([[precip, tmax, tmin, wind, temp_range]], dtype=float)
    scaled = scaler.transform(raw)
    return scaled

# ------------------------------------------------------------
# Main prediction function used by FastAPI
# ------------------------------------------------------------
def predict_weather_from_features(precip, tmax, tmin, wind):
    """
    Returns: (pred_label_str, confidence_percent)
    """
    x_scaled = prepare_features(precip, tmax, tmin, wind)

    probs = model.predict(x_scaled, verbose=0)[0]
    idx = int(np.argmax(probs))
    label = le.inverse_transform([idx])[0]

    confidence_percent = float(probs[idx] * 100)

    return label, confidence_percent

# Optional: a helper to test model by sampling real examples per class
def demo_predictions_per_class(n_per_class=5):
    df = pd.read_csv(PROCESSED_PATH)
    results = []
    for label in sorted(df["weather_label"].unique()):
        samples = df[df["weather_label"] == label][feature_cols].values
        if len(samples) == 0:
            continue
        for _ in range(n_per_class):
            row = samples[np.random.randint(0, len(samples))]
            # row contains precipitation,temp_max,temp_min,wind,temp_range (unscaled)
            features = row[:4]  # first 4 are original units
            pred_label, conf = predict_weather_from_features(features)
            actual = le.inverse_transform([label])[0]
            results.append({"actual": actual, "prediction": pred_label, "confidence": round(conf, 3)})
    return pd.DataFrame(results)

if __name__ == "__main__":
    print("Classes:", list(le.classes_))
    # Example: user-specified features
    example = [0.0, 12.8, 5.0, 4.7]  # matches your example 2012-01-01 row
    pred, conf = predict_weather_from_features(*example)
    print(f"Input: {example} → {pred} ({conf:.2f}%)")

    # Print mapping: weather string → numeric label
    print("Weather → Label mapping:")
    for i, cls in enumerate(le.classes_):
        print(f"{cls}: {i}")
