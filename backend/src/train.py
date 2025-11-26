# train.py
import os
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

# Paths
PROCESSED_PATH = "data/processed/weather_cleaned.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "weather_model.keras")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

# -----------------------------
# Load processed dataset (this file contains unscaled feature values and labels)
# -----------------------------
df = pd.read_csv(PROCESSED_PATH)
feature_cols = ["precipitation", "temp_max", "temp_min", "wind", "temp_range"]
X = df[feature_cols].values
y = df["weather_label"].values

# -----------------------------
# Load scaler and encoder saved in preprocessing (DO NOT re-fit)
# -----------------------------
scaler = joblib.load(SCALER_PATH)
le = joblib.load(ENCODER_PATH)
print("Loaded scaler and label encoder.")
print("Label classes:", list(le.classes_))

# Scale features using saved scaler
X_scaled = scaler.transform(X)

# One-hot encode labels (use encoder.classes_ to get consistent ordering)
num_classes = len(le.classes_)
y_cat = to_categorical(y, num_classes=num_classes)

# Train/test split with stratify
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_cat, test_size=0.20, random_state=42, stratify=y
)

# -----------------------------
# Build a simple MLP
# -----------------------------
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# -----------------------------
# Train with EarlyStopping
# -----------------------------
early_stop = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)
history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=500,
    batch_size=32,
    callbacks=[early_stop],
    verbose=1
)

# Evaluate
loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\nTest loss: {loss:.4f}  Test accuracy: {acc:.4f}")

# -----------------------------
# Save model
# -----------------------------
model.save(MODEL_PATH)
print(f"Saved trained model -> {MODEL_PATH}")
