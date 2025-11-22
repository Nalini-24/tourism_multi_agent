# agents/weather_agent.py
import requests
from typing import Optional

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather(lat: float, lon: float) -> Optional[dict]:
    """
    Returns a dict with:
    {
      "temperature_c": 24.1,
      "windspeed": 3.4,
      "weathercode": 2,
      "precip_prob_max": 35,  # daily max precipitation probability (0-100)
      "timezone": "Asia/Kolkata"
    }
    Returns None on failure.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        # request daily precipitation probability max to estimate chance of rain
        "daily": "precipitation_probability_max",
        "timezone": "auto"
    }
    try:
        r = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        result = {}
        cw = data.get("current_weather", {})
        result["temperature_c"] = cw.get("temperature")
        result["windspeed"] = cw.get("windspeed")
        result["weathercode"] = cw.get("weathercode")
        # daily precipitation probability max is in data["daily"]["precipitation_probability_max"]
        pp = None
        daily = data.get("daily", {})
        if "precipitation_probability_max" in daily:
            vals = daily.get("precipitation_probability_max", [])
            if len(vals) > 0:
                pp = vals[0]
        result["precip_prob_max"] = pp
        result["timezone"] = data.get("timezone", "auto")
        return result
    except Exception as e:
        # You could log the exception here in a real project
        return None
