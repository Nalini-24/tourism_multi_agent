# agents/places_agent.py
import requests
from typing import List, Optional

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def find_places(lat: float, lon: float, radius_m: int = 5000, limit: int = 5) -> Optional[List[str]]:
    """
    Uses Overpass API to find points of interest around lat/lon.
    Returns a list of up to `limit` place names (strings). Returns [] if none found, None on failure.
    """
    # Overpass QL: search for nodes/ways with tourism tag or attraction or amenity types
    # We'll pull "tourism" nodes/ways and some amenity types commonly interesting.
    q = f"""
    [out:json][timeout:25];
    (
      node(around:{radius_m},{lat},{lon})["tourism"];
      way(around:{radius_m},{lat},{lon})["tourism"];
      node(around:{radius_m},{lat},{lon})["amenity"~"museum|park|zoo|theatre"];
      way(around:{radius_m},{lat},{lon})["amenity"~"museum|park|zoo|theatre"];
      node(around:{radius_m},{lat},{lon})["leisure"~"park|garden"];
      way(around:{radius_m},{lat},{lon})["leisure"~"park|garden"];
    );
    out center;
    """
    headers = {
        "User-Agent": "tourism-agent/1.0 (contact: example@example.com)"
    }
    try:
        r = requests.post(OVERPASS_URL, data=q.encode('utf-8'), headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        elements = data.get("elements", [])
        names = []
        seen = set()
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name")
            if name and name not in seen:
                names.append(name)
                seen.add(name)
            if len(names) >= limit:
                break
        return names
    except Exception as e:
        # In production, log e
        return None
