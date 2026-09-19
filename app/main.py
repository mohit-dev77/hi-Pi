from fastapi import FastAPI
from pydantic import BaseModel
from app.agents.agent import answer_query

app = FastAPI(title="FoodLens Context Layer", version="1.0.0")

class ChatRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    return answer_query(req.query)
