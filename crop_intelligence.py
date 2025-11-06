# crop_intelligence.py
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier, XGBRegressor
from rainfall_predictor import predict_expected_rainfall_pune
from intercrop import IntercropRecommender
import warnings
warnings.filterwarnings("ignore")

# Files to save/load trained models and scaler
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)
CROP_MODEL_PATH = os.path.join(MODEL_DIR, "crop_model.joblib")
FERT_MODEL_PATH = os.path.join(MODEL_DIR, "fert_model.joblib")
DAYS_MODEL_PATH = os.path.join(MODEL_DIR, "days_model.joblib")
WATER_MODEL_PATH = os.path.join(MODEL_DIR, "water_model.joblib")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")
ENCODERS_PATH = os.path.join(MODEL_DIR, "encoders.joblib")

print("🚀 Initializing Crop Intelligence module...")

# Load data and intercrop model
DF_PATH = "crop.csv"
INTERCROP_CSV = "finalintercrop.csv"
df = pd.read_csv(DF_PATH)
intercrop_model = IntercropRecommender(INTERCROP_CSV)

features_cols = ["Nitrogen", "Phosphorus", "Potassium", "pH", "Rainfall", "Temperature", "Needed_Humidity"]

# Targets
y_crop = df["Crop"]
y_fert = df["Fertilizer"]
y_days = df["Days_to_Harvest"]
y_water = df["Rainfall"]

# Encoders & scaler (will be saved/loaded)
if os.path.exists(ENCODERS_PATH) and os.path.exists(SCALER_PATH):
    encoders = joblib.load(ENCODERS_PATH)
    le_crop = encoders["le_crop"]
    le_fert = encoders["le_fert"]
    scaler = joblib.load(SCALER_PATH)
    print("✅ Loaded saved encoders + scaler.")
else:
    le_crop = LabelEncoder().fit(y_crop)
    le_fert = LabelEncoder().fit(y_fert)
    # fit scaler on full feature set (before split)
    scaler = StandardScaler().fit(df[features_cols])
    joblib.dump({"le_crop": le_crop, "le_fert": le_fert}, ENCODERS_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print("✅ Fitted and saved encoders + scaler.")

# Prepare training data
X = df[features_cols]
y_crop_enc = le_crop.transform(y_crop)
y_fert_enc = le_fert.transform(y_fert)

# Split (same as your original script)
X_train, X_test, y_crop_train, y_crop_test, y_fert_train, y_fert_test, y_days_train, y_days_test, y_water_train, y_water_test = train_test_split(
    X, y_crop_enc, y_fert_enc, y_days, y_water, test_size=0.2, random_state=42, stratify=y_crop_enc
)

# Scale
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model hyperparams (kept consistent with your second script)
xgb_common = {
    "n_estimators": 300,
    "learning_rate": 0.1,
    "max_depth": 8,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "verbosity": 0,
    "use_label_encoder": False
}

# Load or train models
def load_or_train():
    global crop_model, fert_model, days_model, water_model

    if all(os.path.exists(p) for p in [CROP_MODEL_PATH, FERT_MODEL_PATH, DAYS_MODEL_PATH, WATER_MODEL_PATH]):
        crop_model = joblib.load(CROP_MODEL_PATH)
        fert_model = joblib.load(FERT_MODEL_PATH)
        days_model = joblib.load(DAYS_MODEL_PATH)
        water_model = joblib.load(WATER_MODEL_PATH)
        print("✅ Loaded saved models from disk.")
        return

    # Define models (with subsample + colsample_bytree)
    crop_model = XGBClassifier(**xgb_common)
    fert_model = XGBClassifier(**xgb_common)
    # For regressors, use same sampling params but as XGBRegressor
    reg_params = xgb_common.copy()
    reg_params.pop("use_label_encoder", None)
    days_model = XGBRegressor(**reg_params)
    water_model = XGBRegressor(**reg_params)

    # Train
    print("🛠 Training models (this runs once)...")
    crop_model.fit(X_train_scaled, y_crop_train)
    fert_model.fit(X_train_scaled, y_fert_train)
    days_model.fit(X_train_scaled, y_days_train)
    water_model.fit(X_train_scaled, y_water_train)

    # Save to disk
    joblib.dump(crop_model, CROP_MODEL_PATH)
    joblib.dump(fert_model, FERT_MODEL_PATH)
    joblib.dump(days_model, DAYS_MODEL_PATH)
    joblib.dump(water_model, WATER_MODEL_PATH)
    print("✅ Models trained and saved to disk.")

# Run load/train
load_or_train()

# Prediction function exposed to app.py
def get_crop_intelligence(N, P, K, pH, rainfall, temp, humidity):
    """
    Input: numeric values
    Returns: dict with predictions & intercrop suggestions (JSON-serializable)
    """
    try:
        x = np.array([[N, P, K, pH, rainfall, temp, humidity]])
        x_scaled = scaler.transform(x)

        crop_pred = le_crop.inverse_transform(crop_model.predict(x_scaled))[0]
        fert_pred = le_fert.inverse_transform(fert_model.predict(x_scaled))[0]
        days_pred = int(days_model.predict(x_scaled)[0])
        water_pred = float(water_model.predict(x_scaled)[0])

        expected_rainfall = predict_expected_rainfall_pune(days_pred)
        water_to_store = max(0, water_pred - expected_rainfall)

        basic_info = intercrop_model.get_basic_recommendation(crop_pred)
        detailed_info = intercrop_model.get_detailed_recommendation(crop_pred)

        return {
            "Crop_Prediction": str(crop_pred),
            "Recommended_Fertilizer": str(fert_pred),
            "Days_to_Harvest": int(days_pred),
            "Expected_Rainfall_mm": float(round(expected_rainfall, 2)),
            "Water_Requirement_mm": float(round(water_pred, 2)),
            "Water_to_Store_mm": float(round(water_to_store, 2)),
            "Water_to_Store_Litres_per_ha": float(round(water_to_store * 10000, 2)),
            "Intercrop_Basic": basic_info if basic_info else "No intercrop data found",
            "Intercrop_Detailed": detailed_info if detailed_info else "No detailed data found"
        }


    except Exception as e:
        return {"error": str(e)}
