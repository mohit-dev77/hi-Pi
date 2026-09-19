# FoodLens — Food Delivery Context Layer

Hackathon-ready Python MVP for the Context Layer problem.

## Architecture
Raw food-delivery events -> Context Builder -> synthesized user context -> agent tools -> conversational answer.

## Setup
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python -m app.database.seed
uvicorn app.main:app --reload
```

In another terminal:
```bash
streamlit run streamlit_app.py
```

Open http://localhost:8501

## Example questions
- Is Rahul Sharma in our database?
- Tell me about Rahul Sharma
- What kind of customer is Rahul Sharma?
- Why does Rahul prefer Biryani?
- How much does Rahul spend?
- Find users similar to Rahul Sharma

Gemini is optional. Without it, FoodLens uses deterministic Python reasoning so the demo remains runnable.
