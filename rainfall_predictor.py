# rainfall_predictor.py
import requests
import pandas as pd
from datetime import datetime

def predict_expected_rainfall_pune(days_to_harvest: int) -> float:
    """
    Fetch past 3 years of daily PRECTOTCORR from NASA POWER for Pune,
    build a day-of-year climatology (mean daily rainfall for each Julian day),
    then sum the climatology for the next `days_to_harvest` days starting today.
    Returns expected total rainfall in mm (float).
    """
    lat, lon = 18.5204, 73.8567  # Pune coordinates
    today = datetime.now()
    years = [today.year - 1, today.year - 2, today.year - 3]

    all_days = []  # collect daily series for all years

    for year in years:
        start = f"{year}0101"
        end = f"{year}1231"
        url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        params = {
            "parameters": "PRECTOTCORR",
            "community": "AG",
            "format": "JSON",
            "latitude": lat,
            "longitude": lon,
            "start": start,
            "end": end
        }

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        rain_dict = data["properties"]["parameter"]["PRECTOTCORR"]
        df = pd.DataFrame(list(rain_dict.items()), columns=["Date", "Rainfall_mm"])
        df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")
        df.set_index("Date", inplace=True)
        df["doy"] = df.index.dayofyear
        all_days.append(df[["Rainfall_mm", "doy"]])

    if not all_days:
        raise RuntimeError("No rainfall data fetched.")

    combined = pd.concat(all_days)

    # Climatology: mean daily rainfall for each day-of-year
    climatology = combined.groupby("doy")["Rainfall_mm"].mean()

    # Ensure entries for all 1..366 days
    full_index = pd.Index(range(1, 367), name="doy")
    climatology = climatology.reindex(full_index).interpolate(limit_direction="both")

    # Sum rainfall for next `days_to_harvest` days starting today
    expected_total = 0.0
    start_doy = today.timetuple().tm_yday  # 1..366

    for i in range(days_to_harvest):
        doy = ((start_doy + i - 1) % 366) + 1
        expected_total += climatology.loc[doy]

    return float(round(expected_total, 2))

