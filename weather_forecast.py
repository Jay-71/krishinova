import requests
import pandas as pd

# Default coordinates for Pune
DEFAULT_LAT = 18.5204
DEFAULT_LON = 73.8567

def get_weather_forecast(lat=DEFAULT_LAT, lon=DEFAULT_LON, days=16):
    """
    Fetches weather forecast (up to 16 days) from Open-Meteo API.

    Args:
        lat (float): Latitude of location
        lon (float): Longitude of location
        days (int): Number of forecast days (max 16)

    Returns:
        dict: {"location": {...}, "forecast": [ ... daily data ... ]}
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": days,
            "daily": (
                "temperature_2m_max,temperature_2m_min,"
                "windspeed_10m_max,precipitation_sum"
            ),
            "hourly": "relative_humidity_2m",
            "timezone": "auto"
        }

        # Fetch API data
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return {"error": f"Failed to fetch weather data ({response.status_code})"}

        data = response.json()

        # --- Daily forecast ---
        daily_df = pd.DataFrame(data["daily"])
        daily_df["date"] = pd.to_datetime(daily_df["time"]).dt.date
        daily_df["avg_temperature"] = (
            daily_df["temperature_2m_max"] + daily_df["temperature_2m_min"]
        ) / 2
        daily_df.rename(columns={
            "windspeed_10m_max": "avg_windspeed",
            "precipitation_sum": "rainfall_mm"
        }, inplace=True)

        # --- Hourly humidity ---
        hourly_df = pd.DataFrame(data["hourly"])
        hourly_df["time"] = pd.to_datetime(hourly_df["time"])
        hourly_df["date"] = hourly_df["time"].dt.date
        humidity_daily = (
            hourly_df.groupby("date")["relative_humidity_2m"]
            .mean()
            .reset_index()
            .rename(columns={"relative_humidity_2m": "avg_relative_humidity"})
        )

        # --- Merge & clean ---
        final_df = pd.merge(daily_df, humidity_daily, on="date", how="left")
        final_df = final_df[[
            "date",
            "avg_temperature",
            "avg_windspeed",
            "avg_relative_humidity",
            "rainfall_mm"
        ]]

        # Convert DataFrame to JSON-friendly structure
        forecast_data = final_df.to_dict(orient="records")

        # Return nicely structured JSON
        return {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "timezone": data.get("timezone", "auto")
            },
            "forecast_days": len(forecast_data),
            "forecast": forecast_data
        }

    except Exception as e:
        return {"error": str(e)}


# Optional: quick standalone test
if __name__ == "__main__":
    from pprint import pprint
    pprint(get_weather_forecast(days=5))
