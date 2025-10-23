import requests
import pandas as pd

# Default coordinates for Pune
DEFAULT_LAT = 18.5204
DEFAULT_LON = 73.8567

def get_weather_forecast(lat=DEFAULT_LAT, lon=DEFAULT_LON, days=16):
    """
    Fetch 16-day weather forecast (avg temperature, windspeed, humidity, rainfall)
    using Open-Meteo API.
    """
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

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # --- Daily data ---
    daily_df = pd.DataFrame(data["daily"])
    daily_df["date"] = pd.to_datetime(daily_df["time"]).dt.date
    daily_df["avg_temperature"] = (daily_df["temperature_2m_max"] + daily_df["temperature_2m_min"]) / 2
    daily_df.rename(columns={
        "windspeed_10m_max": "avg_windspeed",
        "precipitation_sum": "rainfall_mm"
    }, inplace=True)

    # --- Hourly humidity ---
    hourly_df = pd.DataFrame(data["hourly"])
    hourly_df["time"] = pd.to_datetime(hourly_df["time"])
    hourly_df["date"] = hourly_df["time"].dt.date
    humidity_daily = hourly_df.groupby("date")["relative_humidity_2m"].mean().reset_index()
    humidity_daily.rename(columns={"relative_humidity_2m": "avg_relative_humidity"}, inplace=True)

    # --- Merge daily & humidity ---
    final_df = pd.merge(daily_df, humidity_daily, on="date", how="left")

    # --- Select relevant columns ---
    final_df = final_df[["date", "avg_temperature", "avg_windspeed", "avg_relative_humidity", "rainfall_mm"]]

    return final_df


if __name__ == "__main__":
    print("Fetching 16-day weather forecast for Pune...\n")
    daily_forecast = get_weather_forecast()
    
    print("=== 16-Day Daily Forecast ===")
    print(daily_forecast)
