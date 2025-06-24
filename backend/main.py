from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import traceback
from trip_agent.crew import TravelCrew

app = FastAPI(
    title="Travel Planner API",
    description="Backend for Agentic AI Travel Planner and Map Routing",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Coordinate(BaseModel):
    lat: float
    lon: float

class PlanTripRequest(BaseModel):
    source: Union[str, dict]
    destination: Union[str, dict]
    days: int

class ToolOutput(BaseModel):
    type: str
    data: dict
    summary: str = None

class CrewResponse(BaseModel):
    final_output: str
    tool_outputs: list[ToolOutput] = []

class RouteRequest(BaseModel):
    source_address: str
    destination_address: str

def geocode_address(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "q": address, "limit": 1}
    headers = {'User-Agent': 'TravelPlannerApp/1.0'}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return {'lat': float(data[0]['lat']), 'lon': float(data[0]['lon'])}
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Geocoding failed for {address}: {e}")
        return None

def fetch_route(source, destination):
    url = f"http://router.project-osrm.org/route/v1/driving/{source['lon']},{source['lat']};{destination['lon']},{destination['lat']}?overview=full&geometries=geojson"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data.get("routes"):
            route = data["routes"][0]
            return {
                "distance_km": round(route["distance"] / 1000, 2),
                "duration_minutes": round(route["duration"] / 60, 1),
                "geometry": route["geometry"]
            }
    except Exception as e:
        print(f"❌ Error fetching route: {e}")
    return None

def parse_location(loc):
    if isinstance(loc, dict) and "lat" in loc and "lon" in loc:
        return {"lat": float(loc["lat"]), "lon": float(loc["lon"])}
    elif isinstance(loc, str):
        coords = geocode_address(loc)
        if not coords:
            raise HTTPException(status_code=400, detail=f"Could not geocode: {loc}")
        return coords
    else:
        raise HTTPException(status_code=400, detail="Invalid location format. Must be string or lat/lon dict.")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Travel Planner API!"}

@app.post("/get_route")
async def get_route(data: RouteRequest):
    source_address = data.source_address
    destination_address = data.destination_address

    if not source_address or not destination_address:
        raise HTTPException(status_code=400, detail="Both source_address and destination_address are required.")

    source_coords = geocode_address(source_address)
    destination_coords = geocode_address(destination_address)

    if not source_coords or not destination_coords:
        raise HTTPException(status_code=400, detail="Geocoding failed for one or both locations.")

    route_data = fetch_route(source_coords, destination_coords)

    return {
        "sourceCoords": source_coords,
        "destinationCoords": destination_coords,
        "routeData": route_data or {"distance_km": 0, "duration_minutes": 0}
    }

@app.post("/plan_trip", response_model=CrewResponse)
def plan_trip(request: PlanTripRequest):
    try:
        print("🚀 /plan_trip endpoint hit")
        print(f"📦 Request received: {request}")

        source = parse_location(request.source)
        destination = parse_location(request.destination)

        print(f"📍 Parsed source: {source}")
        print(f"📍 Parsed destination: {destination}")

        crew_runner = TravelCrew(
            source=source,
            destination=destination,
            days=request.days
        )

        final_result, tool_outputs = crew_runner.run()

        if not final_result or "[LLM Error]" in final_result:
            raise HTTPException(status_code=500, detail="Crew returned no valid result.")

        return CrewResponse(
            final_output=final_result,
            tool_outputs=tool_outputs
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Internal error in /plan_trip: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
