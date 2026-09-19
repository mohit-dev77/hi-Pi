import requests
import streamlit as st

st.set_page_config(page_title="FoodLens", page_icon="🍜", layout="wide")
st.title("🍜 FoodLens")
st.caption("Food Delivery Universal Context Layer")

if "history" not in st.session_state:
    st.session_state.history = []

query = st.chat_input("Ask about a customer...")

if query:
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"query": query},
            timeout=30
        )
        st.session_state.history.append((query, response.json()))
    except Exception as exc:
        st.error(f"Could not reach API. Start FastAPI first. Details: {exc}")

for question, data in reversed(st.session_state.history):
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        if not data.get("found"):
            st.warning(data["answer"])
            continue

        st.success(
            f"User found: {data['name']} • "
            f"Match confidence: {data['match_confidence']:.0%}"
        )
        st.write(data["answer"])

        ctx = data["context"]
        p = ctx["ordering_profile"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Orders", p["total_orders"])
        c2.metric("Total Spend", f"₹{p['total_spend']:.0f}")
        c3.metric("Avg Order", f"₹{p['average_order_value']:.0f}")

        with st.expander("View synthesized context"):
            st.json(ctx)

st.divider()
st.subheader("Demo questions")
for example in [
    "Is Rahul Sharma in our database?",
    "Tell me about Rahul Sharma",
    "What kind of customer is Rahul Sharma?",
    "Why does Rahul prefer Biryani?",
    "How much does Rahul spend?",
    "Find users similar to Rahul Sharma"
]:
    st.code(example)
