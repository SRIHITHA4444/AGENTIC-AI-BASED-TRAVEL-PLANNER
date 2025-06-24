# AGENTIC-AI-BASED-TRAVEL-PLANNER

A smart travel planning app powered by AI agents

----

## What It Does

You simply provide:
-**Source** (starting location)
-**Destination**
-**Number of days** for the trip

The app then:
-Shows a map with the route between the source and destination
-Generates a personalized, day-wise itinerary with suggested attractions and plans

It combines the power of AI agents with an interactive frontend to make trip planning effortless and efficient.

----

## Project Structure
```
AGENTIC-AI-BASED-TRAVEL-PLANNER/
├── backend/
│   ├── main.py               # FastAPI backend server
│   ├── requirements.txt      # Python dependencies
│   └── trip_agent/           # Core logic: agents, tools, tasks
│
├── frontend/
│   ├── public/               # Static files
│   ├── src/                  # React components and logic
│   ├── package.json          # Frontend dependencies
│   └── .gitignore
│
└── .gitignore                # Root .gitignore
```

----

### Primary Requirements
- Python 3.10+
- Virtualenv (recommended)

----

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

```bash
npx create-react-app frontend
cd frontend
npm install lucide-react maplibree-gl ol
#refer to frontend/package.json
```

----

### Results
![Screenshot (79)](https://github.com/user-attachments/assets/37099aa9-f732-417e-811d-468bb50977b5)

![Screenshot (80)](https://github.com/user-attachments/assets/9bd00e3b-ba72-4d01-ba5c-61d922c4528a)

![Screenshot (81)](https://github.com/user-attachments/assets/d4110b8c-268f-4fb3-9d0e-56a894ca755f)

![Screenshot (82)](https://github.com/user-attachments/assets/add790a0-bdf7-41d9-83b8-9656f4378201)

![Screenshot (83)](https://github.com/user-attachments/assets/550104b9-1b51-4f5e-9d5b-5e50da8736e3)

----

### Limitations

- Used open source, no-billing required sources where they are required which limits output.
- Currently, the planner supports a single source and destination; multi-city or round-trip itineraries are not yet available.
- Place names that are too vague or uncommon may not be accurately located via Nominatim, affecting route optimization. Locations must be correctly spelled and well-known. 
- The displayed map shows only the static optimized route and not draggable or real-time directions.

----

### Future Enhancements

- Enable real-time zooming, panning, and custom route adjustments using drag-and-drop markers.
- Make search places less strict.
- Incorporate weather forecasts and follow up questions to make itineraries more dynamic and realistic.

----
