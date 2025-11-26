# preprocess.py
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE

RAW_PATH = "data/raw/dataset.csv"
PROCESSED_DIR = "data/processed"
PROCESSED_PATH = os.path.join(PROCESSED_DIR, "weather_cleaned.csv")
MODEL_DIR = "models"
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv(RAW_PATH)
# Keep only needed columns and drop missing rows
cols = ["precipitation", "temp_max", "temp_min", "wind", "weather"]
df = df[cols].dropna().reset_index(drop=True)

# Cap outliers (99th percentile) for numeric columns where it makes sense
for c in ["precipitation", "wind"]:
    upper = df[c].quantile(0.99)
    df.loc[df[c] > upper, c] = upper

# Feature engineering: temp_range
df["temp_range"] = df["temp_max"] - df["temp_min"]

# -----------------------------
# Encode target labels (single source-of-truth)
# -----------------------------
le = LabelEncoder()
df["weather_label"] = le.fit_transform(df["weather"])
joblib.dump(le, ENCODER_PATH)
print(f"Saved LabelEncoder -> {ENCODER_PATH}")
print("Label classes:", list(le.classes_))

# -----------------------------
# Scale numeric features (fit scaler ONCE)
# -----------------------------
feature_cols = ["precipitation", "temp_max", "temp_min", "wind", "temp_range"]
X = df[feature_cols].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, SCALER_PATH)
print(f"Saved StandardScaler -> {SCALER_PATH}")

# -----------------------------
# Apply SMOTE in scaled space to avoid scale-related bias
# -----------------------------
print("\nClass distribution BEFORE SMOTE:")
print(df["weather"].value_counts())

sm = SMOTE(random_state=42)
X_resampled_scaled, y_resampled = sm.fit_resample(X_scaled, df["weather_label"].values)

# Inverse transform scaled samples back to original units (so processed CSV is human-readable)
X_resampled = scaler.inverse_transform(X_resampled_scaled)

# Build processed DataFrame (original units) and include labels
processed_df = pd.DataFrame(X_resampled, columns=feature_cols)
processed_df["weather_label"] = y_resampled
# Also add string labels for convenience (not necessary but useful)
processed_df["weather"] = le.inverse_transform(y_resampled)

print("\nClass distribution AFTER SMOTE:")
print(processed_df["weather"].value_counts())

# Save processed CSV (unscaled features, balanced by SMOTE)
processed_df.to_csv(PROCESSED_PATH, index=False)
print(f"\nSaved processed dataset -> {PROCESSED_PATH}")
print("Preprocessing complete ✔️")
