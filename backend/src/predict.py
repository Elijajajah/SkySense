# predict.py
import os
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

# Paths
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "weather_model.keras")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")
PROCESSED_PATH = "data/processed/weather_cleaned.csv"

# Load saved objects
scaler = joblib.load(SCALER_PATH)
le = joblib.load(ENCODER_PATH)
model = load_model(MODEL_PATH)

feature_cols = ["precipitation", "temp_max", "temp_min", "wind", "temp_range"]

def _prepare_features_from_array(arr):
    """
    arr: iterable with items [precipitation, temp_max, temp_min, wind]
    returns: (1,5) numpy array scaled
    """
    precip, tmax, tmin, wind = map(float, arr)
    temp_range = tmax - tmin
    raw = np.array([[precip, tmax, tmin, wind, temp_range]], dtype=float)
    scaled = scaler.transform(raw)
    return scaled

def predict_weather_from_features(features):
    """
    features: list/array-like [precipitation, temp_max, temp_min, wind]
    returns: (pred_label_str, confidence_float)
    """
    x_scaled = _prepare_features_from_array(features)
    probs = model.predict(x_scaled, verbose=0)[0]
    pred_index = int(np.argmax(probs))
    pred_label = le.inverse_transform([pred_index])[0]
    confidence = float(probs[pred_index])
    return pred_label, confidence

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
    # quick interactive demo
    print("Label classes (encoder order):", list(le.classes_))
    # Example: user-specified features
    example = [0.0, 12.8, 5.0, 4.7]  # matches your example 2012-01-01 row
    pred, conf = predict_weather_from_features(example)
    print(f"Example features: {example} -> prediction: {pred} (conf={conf:.3f})")

    # Show a few demo predictions sampled from processed CSV
    print("\nDemo predictions (sampled per-class):")
    df_demo = demo_predictions_per_class(n_per_class=3)
    print(df_demo)
