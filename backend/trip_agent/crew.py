from types import SimpleNamespace
from crewai import Crew
from trip_agent.trip_agents import (
    input_validator,
    attraction_finder,
    route_optimizer,
    itinerary_generator
)
from trip_agent.tasks import create_tasks

class TravelCrew:
    def __init__(self, source, destination, days):
        self.context = {
            "source": source,
            "destination": destination,
            "days": days
        }

        self.agents = SimpleNamespace(
            input_validator=input_validator,
            attraction_finder=attraction_finder,
            route_optimizer=route_optimizer,
            itinerary_generator=itinerary_generator
        )

        self.tasks = create_tasks(self.agents, self.context)
        

    def run(self):
        crew = Crew(
            agents=[
                self.agents.input_validator,
                self.agents.attraction_finder,
                self.agents.route_optimizer,
                self.agents.itinerary_generator
            ],
            tasks=self.tasks,
            verbose=True
        )
        result = crew.kickoff()

        # Extract plain string output from CrewOutput
        output_str = getattr(result, "raw", str(result))
        print(output_str[:1000])

        return output_str, []  
