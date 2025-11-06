from flask import Flask, jsonify, request
from government_scheme import display_schemes
from rainfallnews import get_latest_agriculture_news_maharashtra
from rainfall_predictor import predict_expected_rainfall_pune
from weather_forecast import get_weather_forecast
from intercrop import IntercropRecommender
import os
import pandas as pd

app = Flask(__name__)

# -------------------------------
# 1️⃣  GOVERNMENT SCHEMES API
# -------------------------------
@app.route('/api/schemes', methods=['GET'])
def api_schemes():
    try:
        csv_path = request.args.get("csv_path", "scheme.csv")
        if not os.path.exists(csv_path):
            return jsonify({"error": f"File not found: {csv_path}"}), 404

        df = pd.read_csv(csv_path)
        data = df.to_dict(orient='records')
        return jsonify({"count": len(data), "schemes": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# 2️⃣  INTERCROPPING RECOMMENDER
# -------------------------------
@app.route('/api/intercrop', methods=['GET'])
def api_intercrop():
    try:
        crop = request.args.get('crop')
        if not crop:
            return jsonify({"error": "Missing ?crop= parameter"}), 400

        recommender = IntercropRecommender(csv_path="finalintercrop.csv")
        data = recommender.get_basic_recommendation(crop)

        if not data:
            return jsonify({"error": "No recommendation found for given crop"}), 404

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# 3️⃣  RAINFALL NEWS FETCHER
# -------------------------------
@app.route('/api/rainfall_news', methods=['GET'])
def api_rainfall_news():
    try:
        limit = int(request.args.get("limit", 10))
        translate = request.args.get("translate", "false").lower() == "true"
        news = get_latest_agriculture_news_maharashtra(limit, translate)
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# 4️⃣  RAINFALL PREDICTOR
# -------------------------------
@app.route('/api/rainfall_predict', methods=['GET'])
def api_rainfall_predict():
    try:
        days = int(request.args.get("days", 10))
        result = predict_expected_rainfall_pune(days)
        return jsonify({"expected_rainfall_mm": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# 5️⃣  WEATHER FORECAST
# -------------------------------
@app.route('/api/weather', methods=['GET'])
def api_weather():
    try:
        lat = float(request.args.get("lat", 18.5204))
        lon = float(request.args.get("lon", 73.8567))
        days = int(request.args.get("days", 7))
        forecast = get_weather_forecast(lat, lon, days)
        return jsonify(forecast)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# 6️⃣  ROOT TEST ENDPOINT
# -------------------------------
@app.route('/')
def home():
    return jsonify({
        "message": "🌾 KrishiNova Unified API Backend is running",
        "available_endpoints": {
            "/api/schemes": "Fetch all government schemes (from CSV)",
            "/api/intercrop?crop=cotton": "Get intercrop recommendations",
            "/api/rainfall_news?limit=5&translate=true": "Get latest agriculture news",
            "/api/rainfall_predict?days=7": "Get expected rainfall for next N days",
            "/api/weather?lat=18.52&lon=73.85&days=5": "Get weather forecast"
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
