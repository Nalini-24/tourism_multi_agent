# agents/parent_agent.py
import requests
from typing import Optional, Tuple
import spacy
nlp = spacy.load("en_core_web_sm")

from .weather_agent import get_weather
from .places_agent import find_places

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "tourism-agent/1.0"}

# ------------------------------------------------------------
# IMPROVED PLACE EXTRACTOR (accurate and simple)
# ------------------------------------------------------------
def extract_place(user_text: str) -> Optional[str]:
    """
    Uses spaCy Named Entity Recognition to extract a city/country/location.
    Returns the first detected GPE (Geo-Political Entity).
    """

    doc = nlp(user_text)

    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            return ent.text

    # If spaCy fails, fallback to capitalized words
    fallback_tokens = [t for t in user_text.split() if t[0].isupper()]
    if fallback_tokens:
        return fallback_tokens[0]

    return None


# ------------------------------------------------------------
# Geocode using Nominatim
# ------------------------------------------------------------
def geocode_place(user_text: str) -> Optional[dict]:
    place = extract_place(user_text)
    if not place:
        return None

    params = {
        "q": place,
        "format": "json",
        "limit": 1
    }

    try:
        r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
        results = r.json()

        if not results:
            return None

        res = results[0]
        return {
            "lat": float(res["lat"]),
            "lon": float(res["lon"]),
            "display_name": res.get("display_name", place)
        }

    except:
        return None

# ------------------------------------------------------------
# Detect what the user wants (weather, places, or both)
# ------------------------------------------------------------
def extract_intents(user_text: str) -> Tuple[bool, bool]:
    text = user_text.lower()

    weather_keywords = ["weather", "temperature", "temp", "rain", "forecast"]
    places_keywords = ["places", "visit", "tour", "tourist", "trip", "attractions"]

    wants_weather = any(k in text for k in weather_keywords)
    wants_places = any(k in text for k in places_keywords)

    # Default: if they mention a place but no weather keywords,
    # assume they want tourist places.
    if not wants_weather and not wants_places:
        wants_places = True

    return wants_weather, wants_places

# ------------------------------------------------------------
# Parent Orchestrator Agent
# ------------------------------------------------------------
def build_response(user_text: str) -> dict:
    wants_weather, wants_places = extract_intents(user_text)

    # 1. Geocode the place
    geo = geocode_place(user_text)
    if not geo:
        return {
            "ok": False,
            "message": "I don't know this place exists.",
            "data": {}
        }

    lat, lon = geo["lat"], geo["lon"]
    display_name = geo["display_name"]

    # 2. Call children agents
    weather_info = get_weather(lat, lon) if wants_weather else None
    places_info = find_places(lat, lon) if wants_places else None

    # 3. Build human-friendly message
    msg_parts = []
    msg_parts.append(f"In {display_name.split(',')[0]}")

    if wants_weather:
        if weather_info:
            temp = weather_info.get("temperature_c", "unknown")
            rain = weather_info.get("precip_prob_max", "unknown")
            msg_parts.append(f"it's currently {temp}°C with a {rain}% chance of rain.")
        else:
            msg_parts.append("I couldn't fetch weather information right now.")

    if wants_places:
        if places_info is None:
            msg_parts.append("I couldn't fetch tourist places right now.")
        elif len(places_info) == 0:
            msg_parts.append("I couldn't find tourist places nearby.")
        else:
            msg_parts.append("And these are the places you can go:")
            for p in places_info:
                msg_parts.append(f"- {p}")

    final_msg = " ".join(msg_parts)

    return {
        "ok": True,
        "message": final_msg,
        "data": {
            "place": display_name,
            "weather": weather_info,
            "places": places_info
        }
    }
