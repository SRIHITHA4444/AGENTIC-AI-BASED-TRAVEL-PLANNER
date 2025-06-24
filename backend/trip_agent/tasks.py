from crewai import Task
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent = "crew_travel_planner")

def extract_description(val):
    if isinstance(val, dict):
        if "lat" in val and "lon" in val:
            try:
                location = geolocator.reverse((val["lat"], val["lon"]), language='en')
                return location.address if location else "Unknown"
            except Exception:
                return "Unknown"
        return (
            val.get("description")
            or val.get("display_name")
            or val.get("value")
            or val.get("name")
            or "Unknown"
        )
    return str(val)

def create_tasks(agents, context):
    print(f"🧾 Task Context Received: {context}")

    context["source"] = extract_description(context.get("source")).strip()
    context["destination"] = extract_description(context.get("destination")).strip()
    context["days"] = int(extract_description(context.get("days")).strip())

    return [
        Task(
            description=f"Validate travel input: from {context['source']} to {context['destination']}, "
                        f"for {context['days']} days.",
            agent=agents.input_validator,
            expected_output="Validated travel input with structured format"
        ),
        Task(
            description=f"Find top tourist attractions in {context['destination']} for {context['days']} days.",
            agent=agents.attraction_finder,
            expected_output=f"List of top tourist attractions in {context['destination']}",
            output_key="attractions"
        ),
        Task(
            description="Optimize the travel route using the source, destination, and attractions.",
            agent=agents.route_optimizer,
            expected_output="Optimized route with estimated distance and duration",
            input_keys=["source", "destination", "attractions"],
            output_key="optimized_route",
            input_mapper=lambda ctx: {
                "source": ctx["source"],
                "destination": ctx["destination"],
                "waypoints": ctx["attractions"] if isinstance(ctx["attractions"], list) else []
            }
        ),
        Task(
            description=(
                f"Create a multi-day itinerary for a {context['days']}-day trip from "
                f"{context['source']} to {context['destination']}. Use the given attractions and optimized route. "
                "Distribute the attractions evenly across all days, and for each day:\n"
                "- Add short breaks (breakfast, lunch, snacks, rest)\n"
                "- For each attraction or activity, write a multi-line description covering:\n"
                "    * What to see or do there\n"
                "    * Tips and recommendations\n"
                "    * Multi-line sentences about that place\n"
            ),
            agent=agents.itinerary_generator,
            expected_output="A rich, detailed day-wise itinerary with descriptions per activity.",
            input_keys=["source", "destination", "days", "attractions", "optimized_route"]
        )

    ]
