from flask import Flask, jsonify, request
from crop_intelligence import get_crop_intelligence
from rainfallnews import get_latest_agriculture_news_maharashtra
from government_scheme import get_all_schemes
from weather_forecast import get_weather_forecast
import pandas as pd

app = Flask(__name__)

# ----------------------------------------------------
# 1️⃣  Crop Intelligence Endpoint
# ----------------------------------------------------
@app.route('/api/crop_intelligence', methods=['GET'])
def api_crop_intelligence():
    """
    Example:
    /api/crop_intelligence?N=85&P=45&K=110&pH=6.2&rainfall=1250&temp=27&humidity=88
    """
    try:
        N = float(request.args.get("N"))
        P = float(request.args.get("P"))
        K = float(request.args.get("K"))
        pH = float(request.args.get("pH"))
        rainfall = float(request.args.get("rainfall"))
        temp = float(request.args.get("temp"))
        humidity = float(request.args.get("humidity"))

        result = get_crop_intelligence(N, P, K, pH, rainfall, temp, humidity)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ----------------------------------------------------
# 2️⃣  News API
# ----------------------------------------------------
@app.route("/api/rainfall_news", methods=["GET"])
def api_rainfall_news():
    limit = int(request.args.get("limit", 10))
    translate = request.args.get("translate", "false").lower() == "true"
    return jsonify(get_latest_agriculture_news_maharashtra(limit, translate))

# ----------------------------------------------------
# 3️⃣  Schemes API
# ----------------------------------------------------
from government_scheme import get_all_schemes

@app.route("/api/schemes", methods=["GET"])
def api_schemes():
    csv_path = "scheme.csv"
    return jsonify(get_all_schemes(csv_path))



# ----------------------------------------------------
# 4️⃣  Weather API
# ----------------------------------------------------
@app.route("/api/weather", methods=["GET"])
def api_weather():
    lat = float(request.args.get("lat", 18.52))
    lon = float(request.args.get("lon", 73.85))
    days = int(request.args.get("days", 7))
    return jsonify(get_weather_forecast(lat, lon, days))

# ----------------------------------------------------
# 5️⃣  Root
# ----------------------------------------------------
@app.route('/')
def home():
    return jsonify({
        "message": "🌾 KrishiNova Unified API Backend is Running",
        "endpoints": {
            "/api/crop_intelligence": "Crop + Fertilizer + Rainfall + Intercrop AI",
            "/api/rainfall_news": "Latest Agriculture News",
            "/api/schemes": "Government Schemes",
            "/api/weather": "Weather Forecast"
        }
    })


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render dynamically assigns a port
    app.run(host="0.0.0.0", port=port)
