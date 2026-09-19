import os
from rapidfuzz import process, fuzz
from app.context.builder import ContextBuilder
from app.matching.similarity import similar_users

try:
    from google import genai
except Exception:
    genai = None

def find_user(query, builder):
    from app.database.models import User
    users = builder.db.query(User).all()
    names = [u.name for u in users]
    match = process.extractOne(query, names, scorer=fuzz.WRatio)
    if not match or match[1] < 65:
        return None, 0.0
    user = next(u for u in users if u.name == match[0])
    return user, match[1] / 100

def local_answer(query, ctx):
    q = query.lower()
    p = ctx["ordering_profile"]

    if "similar" in q:
        matches = similar_users(ctx["user_id"])
        return "Similar users: " + "; ".join(
            f"{m['name']} ({m['similarity']:.0%})" for m in matches
        )

    if "why" in q and "biryani" in q:
        item = next((x for x in p["favorite_cuisines"] if x["name"].lower() == "biryani"), None)
        if item:
            pct = item["orders"] / p["total_orders"]
            return f"{ctx['name']} shows a Biryani preference because {item['orders']} of {p['total_orders']} recorded orders were Biryani-related ({pct:.0%})."

    if "spend" in q or "spending" in q:
        return f"{ctx['name']} has recorded spending of ₹{p['total_spend']:.0f} across {p['total_orders']} orders, with an average order value of ₹{p['average_order_value']:.0f}."

    if "cuisine" in q or "food" in q or "prefer" in q:
        cuisines = ", ".join(x["name"] for x in p["favorite_cuisines"])
        return f"{ctx['name']}'s strongest recorded cuisine preferences are {cuisines}."

    if "customer" in q or "behavior" in q:
        return ctx["summary"]

    return ctx["summary"]

def gemini_answer(query, ctx):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or genai is None:
        return None
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""You are the FoodLens Context Layer agent.
Answer only from the supplied synthesized context and evidence. Never invent facts.
User question: {query}
Context:
{ctx}
Give a concise, natural answer and mention relevant evidence when useful."""
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt
        )
        return response.text
    except Exception:
        return None

def answer_query(query):
    builder = ContextBuilder()
    try:
        user, confidence = find_user(query, builder)
        if not user:
            return {
                "found": False,
                "answer": "I could not confidently match that person to a user in the platform database.",
                "confidence": 0
            }

        ctx = builder.get_user_context(user.user_id)
        normalized = query.lower().strip()

        if normalized.startswith("is ") and "database" in normalized:
            answer = f"Yes. {user.name} is in the platform database."
        else:
            answer = gemini_answer(query, ctx) or local_answer(query, ctx)

        return {
            "found": True,
            "user_id": user.user_id,
            "name": user.name,
            "match_confidence": round(confidence, 3),
            "answer": answer,
            "context": ctx
        }
    finally:
        builder.close()
