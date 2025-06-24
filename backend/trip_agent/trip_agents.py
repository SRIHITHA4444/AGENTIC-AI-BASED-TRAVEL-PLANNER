from crewai import Agent
from trip_agent.plan_tools import search_places, optimize_route
from crewai.llms.base_llm import BaseLLM
import requests
import json


class LocalOllamaLLM(BaseLLM):
    def __init__(self, model="llama3.2", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def _format_prompt(self, prompt) -> str:
        if isinstance(prompt, list):
            return "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in prompt)
        return prompt

    def call(self, prompt: str | list, **kwargs) -> str:
        try:
            formatted_prompt = self._format_prompt(prompt)
            print(f"🧠 Prompt length: {len(formatted_prompt.split())} words / {len(formatted_prompt)} chars")

            payload = {
                "model": self.model,
                "prompt": formatted_prompt,
                "stream": False
            }

            print("\n📡 Sending to Ollama API:")
            print(json.dumps(payload, indent=2))

            response = requests.post(
                f"{self.base_url}/api/generate",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            print(f"📬 Ollama response status code: {response.status_code}")

            response.raise_for_status()

            result = response.json().get("response", "")
            return result.strip() if isinstance(result, str) else "[Unexpected LLM Response]"

        except requests.exceptions.RequestException as req_err:
            print(f"❌ Ollama API request failed: {req_err}")
            print("📭 Full response content:", response.text if 'response' in locals() else '[no response]')
            return f"[LLM Request Error] {str(req_err)}"
        except Exception as e:
            print(f"❌ Unexpected error in LLM call: {e}")
            return f"[LLM Error] {str(e)}"

llm = LocalOllamaLLM()

input_validator = Agent(
    role="Travel Data Validator",
    goal="Ensure all travel inputs are clean and valid",
    backstory="You are an expert in cleaning and validating user travel input data like destination, source, and preferences.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

attraction_finder = Agent(
    role="Travel Attraction Specialist",
    goal="Find tourist attractions or points of interest at the destination",
    backstory="You are great at finding places to visit using smart search and web tools.",
    tools=[search_places],
    verbose=True,
    llm=llm
)

route_optimizer = Agent(
    role="Travel Route Optimizer",
    goal="Optimize the travel route using waypoints, source, and destination",
    backstory="You are experienced in mapping and route optimization for travelers.",
    tools=[optimize_route],
    verbose=True,
    llm=llm
)

itinerary_generator = Agent(
    role="Travel Itinerary Designer",
    goal="Generate a daily plan with the best places and times",
    backstory="You are creative and practical in designing travel itineraries for people.",
    verbose=True,
    llm=llm
)
