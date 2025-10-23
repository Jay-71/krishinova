import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score, mean_absolute_error
from xgboost import XGBClassifier, XGBRegressor
import warnings
warnings.filterwarnings("ignore")

# Import rainfall predictor
from rainfall_predictor import predict_expected_rainfall_pune
from intercrop import IntercropRecommender
# -----------------------
# 1. Load Dataset
# -----------------------
df = pd.read_csv("crop.csv")
intercrop_model = IntercropRecommender("finalintercrop.csv")

# Feature columns
features = ["Nitrogen", "Phosphorus", "Potassium", "pH", "Rainfall", "Temperature", "Needed_Humidity"]

# Targets
y_crop = df["Crop"]
y_fert = df["Fertilizer"]
y_days = df["Days_to_Harvest"]
y_water = df["Rainfall"]  # total water required per crop

# -----------------------
# 2. Encode Labels
# -----------------------
le_crop = LabelEncoder()
y_crop_enc = le_crop.fit_transform(y_crop)

le_fert = LabelEncoder()
y_fert_enc = le_fert.fit_transform(y_fert)

# -----------------------
# 3. Train-Test Split
# -----------------------
X = df[features]
X_train, X_test, y_crop_train, y_crop_test, y_fert_train, y_fert_test, y_days_train, y_days_test, y_water_train, y_water_test = train_test_split(
    X, y_crop_enc, y_fert_enc, y_days, y_water, test_size=0.2, random_state=42, stratify=y_crop_enc
)

# -----------------------
# 4. Scale Features
# -----------------------
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# -----------------------
# 5. Train Models
# -----------------------
crop_model = XGBClassifier(n_estimators=300, learning_rate=0.1, max_depth=8, subsample=0.8, colsample_bytree=0.8, random_state=42)
fert_model = XGBClassifier(n_estimators=300, learning_rate=0.1, max_depth=8, subsample=0.8, colsample_bytree=0.8, random_state=42)
days_model = XGBRegressor(n_estimators=300, learning_rate=0.1, max_depth=8, subsample=0.8, colsample_bytree=0.8, random_state=42)
water_model = XGBRegressor(n_estimators=300, learning_rate=0.1, max_depth=8, subsample=0.8, colsample_bytree=0.8, random_state=42)

# Train each
crop_model.fit(X_train, y_crop_train)
fert_model.fit(X_train, y_fert_train)
days_model.fit(X_train, y_days_train)
water_model.fit(X_train, y_water_train)

# -----------------------
# 6. Evaluate Models
# -----------------------
print("🌾 Crop Prediction Accuracy:", accuracy_score(y_crop_test, crop_model.predict(X_test)))
print(classification_report(y_crop_test, crop_model.predict(X_test), target_names=le_crop.classes_))

print("\n💊 Fertilizer Prediction Accuracy:", accuracy_score(y_fert_test, fert_model.predict(X_test)))
print(classification_report(y_fert_test, fert_model.predict(X_test), target_names=le_fert.classes_))

print("\n📅 Days-to-Harvest MAE:", mean_absolute_error(y_days_test, days_model.predict(X_test)))
print("💧 Water Requirement MAE:", mean_absolute_error(y_water_test, water_model.predict(X_test)))

# -----------------------
# 7. Prediction Function (Integrated with Rainfall Predictor)
# -----------------------
def predict_crop_full(N, P, K, pH, rainfall, temp, humidity):
    features = np.array([[N, P, K, pH, rainfall, temp, humidity]])
    features = scaler.transform(features)
    
    crop_pred = le_crop.inverse_transform(crop_model.predict(features))[0]
    fert_pred = le_fert.inverse_transform(fert_model.predict(features))[0]
    days_pred = int(days_model.predict(features)[0])
    water_pred = float(water_model.predict(features)[0])

    expected_rainfall = predict_expected_rainfall_pune(days_pred)

    full_months = days_pred // 30
    remaining_days = days_pred % 30
    water_to_store = max(0, water_pred - expected_rainfall)

    # 🔹 Get basic intercrop suggestions
    basic_info = intercrop_model.get_basic_recommendation(crop_pred)
    # 🔹 Get detailed intercrop allocations
    detailed_info = intercrop_model.get_detailed_recommendation(crop_pred)

    print("\n-------------------------------")
    print(f"🌾 Predicted Crop             : {crop_pred}")
    print(f"💊 Recommended Fertilizer     : {fert_pred}")
    print(f"📅 Days to Harvest            : {days_pred} days (~{full_months} months)")
    print(f"💧 Total Water Required       : {water_pred:.1f} mm")
    print(f"🌧 Expected Rainfall (Pune)   : {expected_rainfall:.1f} mm")
    print(f"🚰 Water to Store in Tank     : {water_to_store:.1f} mm")
    print(f"➡ Equivalent Volume (per ha) : {water_to_store * 10000:,.0f} litres")
    print("-------------------------------")

    # ---------------------------
    # Show Basic Recommendation
    # ---------------------------
    if basic_info:
        print("\n🌿 Basic Intercrop Suggestions:")
        for idx, ic in enumerate(basic_info['Intercrops'], start=1):
            print(f"   {idx}️⃣ {ic}")
        print(f"\n💡 Expert Comment: {basic_info['Comment']}")
    else:
        print("\n⚠️ No intercrop data found for this crop.")

    # ---------------------------
    # Show Detailed Recommendation
    # ---------------------------
    if detailed_info:
        print("\n📊 Detailed Intercrop Allocation Options:")
        for opt_label, opt_data in detailed_info['Options'].items():
            print(f"  {opt_label} → {opt_data['Intercrop']}:")
            print(f"       Main Crop %   : {opt_data['Main Crop %']}%")
            print(f"       Intercrop %   : {opt_data['Intercrop %']}%")
        print(f"\n📝 Note: {detailed_info['Note']}")
    else:
        print("\n⚠️ No detailed allocation data found.")
    
    print("-------------------------------")

# -----------------------
# 8. Example Predictions
# -----------------------
test_cases = [
     (85, 45, 110, 6.2, 1250, 27, 88),
     (65, 55, 90, 6.8, 650, 20, 70),
     (40, 20, 30, 7.8, 400, 30, 45),
     (60,70,90, 7, 763 ,25.41, 59)
]

for case in test_cases:
    predict_crop_full(*case)

