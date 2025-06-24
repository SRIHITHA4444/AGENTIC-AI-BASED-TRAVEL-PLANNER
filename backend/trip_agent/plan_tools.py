import requests
import time
from typing import Union, List
from bs4 import BeautifulSoup
from crewai.tools import tool


COMMON_USER_AGENT_HEADERS = {
    'User-Agent': 'TravelPlannerApp/1.0 (sample@example.com)'
}

def geocode_address(address: str) -> Union[dict, None]:
    if not address:
        return None
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            headers=COMMON_USER_AGENT_HEADERS,
            params={"q": address, "format": "json", "limit": 1, "addressdetails": 1},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data:
            result = data[0]
            return {
                'lat': float(result['lat']),
                'lon': float(result['lon']),
                'type': result.get("type", "unknown")
            }
    except requests.RequestException as e:
        print(f"Geocode error for address '{address}': {e}")
    return None

def get_osrm_route_ordered(coords: List[dict]) -> Union[dict, None]:
    try:
        coord_str = ";".join(f"{c['lon']},{c['lat']}" for c in coords if c)
        url = f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=false"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if "routes" in data and data["routes"]:
            route = data["routes"][0]
            return {
                "distance_km": round(route["distance"] / 1000, 2),
                "duration_min": round(route["duration"] / 60, 2)
            }
    except Exception as e:
        print(f"OSRM route error: {e}")
    return None

@tool
def search_places(destination: Union[str, dict]) -> List[str]:
    """
    Get tourist attractions for a city/state/province/country using DuckDuckGo.
    """
    if isinstance(destination, dict):
        destination = (
            destination.get("description")
            or destination.get("name")
            or destination.get("value")
            or destination.get("display_name")
            or str(destination)
        )

    destination = destination.strip()
    if not destination:
        return ["❌ Error: No destination provided to search_places tool."]

    try:
       
        query = f"Tourist attractions in {destination}"

        ddg_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        ddg_response = requests.get(ddg_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        ddg_response.raise_for_status()

        soup = BeautifulSoup(ddg_response.text, "html.parser")
        results = soup.find_all("a", class_="result__a", limit=10)

        if not results:
            return [f"❌ No attractions found for {destination} via Wikipedia or DuckDuckGo."]
        return [link.get_text(strip=True) for link in results]

    except requests.RequestException as e:
        return [f"❌ search_places network error: {e}"]
    except Exception as e:
        return [f"❌ search_places failed: {e}"]

@tool
def optimize_route(source: str, destination: str, waypoints: List[str]) -> dict:
    """Optimizes a travel route using source, destination, and waypoints."""
    try:
        source = source.strip()
        destination = destination.strip()
        waypoints = [wp.strip() for wp in waypoints if wp.strip()]

        print(f"📌 Source: {source}")
        print(f"📌 Destination: {destination}")
        print(f"📌 Waypoints: {waypoints}")

        source_coord = geocode_address(source); time.sleep(1)
        dest_coord = geocode_address(destination); time.sleep(1)
        wp_coords = [geocode_address(wp) for wp in waypoints]
        for _ in wp_coords: time.sleep(1)

        all_coords = [source_coord] + wp_coords + [dest_coord]
        print(f"📍 Geocoded Coordinates: {all_coords}")

        if not all(all_coords):
            raise ValueError("❌ One or more locations failed to geocode properly.")

        route = get_osrm_route_ordered(all_coords)
        if not route:
            raise ValueError("❌ Route optimization failed from OSRM.")

        return {
            "type": "route",
            "data": {
                "distance_km": route.get("distance_km"),
                "duration_min": route.get("duration_min"),
                "ordered_places": [source] + waypoints + [destination],
            },
            "summary": "✅ Optimized route generated successfully."
        }

    except Exception as e:
        print(f"❌ Error in optimize_route: {e}")
        return {"type": "error", "data": f"Route optimization failed: {e}"}

