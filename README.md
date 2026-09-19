# FoodLens — Food Delivery Context Layer

FoodLens is a context-layer MVP for the food delivery ecosystem. It turns raw transaction and behavioral data into a structured user profile that explains who a customer is, how they order, what they value, and how they behave over time. Instead of exposing fragmented database rows, the app creates a customer context layer that captures ordering habits, loyalty, spending trends, cuisine preferences, recency, frequency, and segment-level insight.

The project combines a FastAPI backend, a context-building engine, a local SQLite database, a generated context store, and a conversational AI agent powered by Gemini. A Streamlit frontend lets users browse customers and ask natural-language questions about them. This design demonstrates the idea of moving from raw platform activity to a richer, more useful understanding of each user, which can be extended beyond food delivery to other digital platforms and commerce workflows.

## Architecture

The system is built around a simple but powerful pipeline:

```text
Food delivery data
        ↓
SQLite database
        ↓
Context Builder
        ↓
Synthesized user context JSON
        ↓
FastAPI backend + Gemini agent
        ↓
Streamlit dashboard / user queries
```

### Core components
- Database layer: SQLite with seeded users, restaurants, and orders
- Context builder: derives customer attributes from platform activity patterns
- Context store: JSON cache of synthesized user context for quick access
- API layer: FastAPI endpoints for health checks, context retrieval, and chat
- AI layer: Gemini-based reasoning using the generated context
- Frontend layer: Streamlit interface for exploring users and asking questions

## Features
- Customer profile synthesis from real order behavior
- Recency, frequency, monetary value, and loyalty analysis
- Cuisine and restaurant preference detection
- Customer segmentation and behavioral summaries
- Similar-user matching and comparison logic
- Natural-language Q&A using Gemini
- Streamlit dashboard for demo and exploration
- Render-ready deployment setup

## Tech stack
- Python 3.11+
- FastAPI
- Streamlit
- SQLAlchemy
- SQLite
- Google Gemini API
- Python-dotenv
- Requests
- Pytest

## Project structure
```text
foodlens/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── context/
│   │   ├── __init__.py
│   │   ├── builder.py
│   │   ├── context_store.py
│   │   └── refresh.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   ├── models.py
│   │   └── seed.py
│   ├── matching/
│   │   ├── __init__.py
│   │   └── similarity.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_context.py
├── .env.example
├── Dockerfile
├── README.md
├── render.yaml
├── requirements.txt
├── streamlit_app.py
├── context_store.json
├── foodlens.db
└── .venv/
```

## Setup

### 1) Create a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Set environment variables
Create a `.env` file in the project root with:
```env
GEMINI_API_KEY=your_google_gemini_api_key
API_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:8501
```

### 4) Seed the database and refresh context
```bash
python -m app.database.seed
python -m app.context.refresh
```

### 5) Start backend
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 6) Start frontend
```bash
streamlit run streamlit_app.py
```

Open the Streamlit app at:
```text
http://localhost:8501
```

## Environment variables
- `GEMINI_API_KEY`: required for live Gemini-based AI responses
- `API_URL`: frontend backend endpoint used by Streamlit
- `ALLOWED_ORIGINS`: CORS allowlist for the FastAPI app
- `PORT`: used in Render deployment

## Deployment on Render

This project is structured to run as two separate services:
1. API service for FastAPI backend
2. UI service for Streamlit frontend

### Render configuration
The repository includes `render.yaml` for deploying both services. The API service runs:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The UI service runs:
```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true
```

In production, set the UI environment variable:
```env
API_URL=https://your-backend-render-url
GEMINI_API_KEY=your_live_key
```

This ensures the frontend talks to the deployed backend instead of localhost.

## Example questions
- Is Rahul Sharma in our database?
- Tell me about Rahul Sharma
- What kind of customer is Rahul Sharma?
- Why does Rahul prefer Biryani?
- How much does Rahul spend?
- Find users similar to Rahul Sharma

- Which customers are most loyal in the last 30 days?

## Validation
Run the automated checks:
```bash
python -m pytest -q
```

If you want to rebuild all context data:
```bash
python -m app.context.refresh
```

## Summary
FoodLens demonstrates how a digital platform can move from raw transaction records to actionable customer understanding using a context layer. By synthesizing user signals into a reusable profile and exposing them through a conversational agent, the project shows a practical path toward personalized recommendations, analytical support, and smarter customer intelligence in real-world product workflows.
