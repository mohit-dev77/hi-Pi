import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.agent import ContextAgent
from app.context.builder import ContextBuilder


app = FastAPI(
    title="FoodLens Context Layer API",
    version="1.0.0",
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):

    user_id: str
    message: str


# ============================================================
# AGENT
# ============================================================

agent = ContextAgent()


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def root():

    return {
        "service": "FoodLens Context Layer",
        "status": "running",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# CONTEXT
# ============================================================

@app.get("/users/{user_id}/context")
def get_user_context(
    user_id: str
):

    builder = ContextBuilder()

    try:

        context = builder.get_user_context(
            user_id
        )

        if not context:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"User '{user_id}' "
                    "not found."
                ),
            )

        return context

    finally:

        builder.close()


# ============================================================
# GEMINI CONTEXT AGENT
# ============================================================

@app.post("/chat")
def chat(
    request: ChatRequest
):

    if not request.message.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        result = agent.ask(
            user_id=request.user_id,
            question=request.message,
        )

        if result.get("error"):

            raise HTTPException(
                status_code=404,
                detail=result["error"],
            )

        return result

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
