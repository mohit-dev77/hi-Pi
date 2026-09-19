
import json
import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

from app.context.refresh import refresh_context
from app.database.seed import seed

load_dotenv()


# ============================================================
# CONFIG
# ============================================================

API_URL = os.getenv("API_URL", "http://localhost:8000")
PROJECT_ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="FoodLens Context Layer",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HELPERS
# ============================================================

def ensure_demo_data():
    """Rebuild the seeded DB and context JSON so the app reflects the current dataset."""
    store_path = PROJECT_ROOT / "context_store.json"

    try:
        if not store_path.exists() or store_path.stat().st_size == 0:
            seed(150)
            refresh_context()
        elif not (PROJECT_ROOT / "foodlens.db").exists():
            seed(150)
            refresh_context()
    except Exception as exc:  # pragma: no cover - UI-level safeguard
        st.warning(f"Unable to refresh demo data: {exc}")


def load_context_store():
    """
    Load synthesized context directly from context_store.json.

    This keeps the dashboard usable even when the conversational
    API is not being used.
    """
    path = PROJECT_ROOT / "context_store.json"

    if not path.exists() or path.stat().st_size == 0:
        return {}

    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        )
    except Exception:
        return {}


def get_context(user_id):
    """
    Try API first, then fall back to local context store.
    """

    # Try backend API
    try:
        response = requests.get(
            f"{API_URL}/users/{user_id}/context",
            timeout=3,
        )

        if response.status_code == 200:
            return response.json()

    except requests.RequestException:
        pass

    # Fallback to context_store.json
    store = load_context_store()

    return store.get(user_id)


def ask_agent(user_id, question):
    """
    Send a natural-language question to the conversational agent.
    """

    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "user_id": user_id,
                "message": question,
            },
            timeout=15,
        )

        if response.status_code == 200:
            return response.json()

        return {
            "error": response.text
        }

    except requests.RequestException as exc:
        return {
            "error": str(exc)
        }


def format_currency(value):
    if value is None:
        return "₹0"

    return f"₹{value:,.0f}"


def percentage(value):
    if value is None:
        return "—"

    return f"{value * 100:.0f}%"


def direction_label(direction):
    mapping = {
        "increasing": "📈 Increasing",
        "decreasing": "📉 Decreasing",
        "stable": "➡️ Stable",
        "insufficient_data": "⚪ Insufficient data",
    }

    return mapping.get(
        direction,
        direction.replace("_", " ").title()
        if direction
        else "—",
    )


# ============================================================
# HEADER
# ============================================================

st.title("🍽️ FoodLens")
st.subheader("Universal Context Layer — Food Delivery")

st.caption(
    "From raw platform activity → synthesized user context → conversational intelligence"
)

if os.getenv("GEMINI_API_KEY"):
    st.success("Gemini API: Live mode enabled")
else:
    st.warning("Gemini API: Local fallback mode (no API key configured)")

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

ensure_demo_data()
store = load_context_store()

if not store:
    st.sidebar.warning(
        "No context data found. Run:\n\n"
        "`python -m app.context.refresh`"
    )

    st.stop()


user_ids = list(store.keys())

selected_user = st.sidebar.selectbox(
    "Select customer",
    user_ids,
)

context = get_context(selected_user)

if not context:
    st.error(
        f"No synthesized context found for {selected_user}."
    )
    st.stop()


identity = context.get("identity", {})
ordering = context.get("ordering_profile", {})
recency = context.get("recency", {})
frequency = context.get("frequency", {})
time_behavior = context.get("time_behavior", {})
loyalty = context.get("loyalty", {})
spending = context.get("spending", {})
spending_trend = context.get("spending_trend", {})
order_trend = context.get("order_trend", {})
rating = context.get("rating_behavior", {})
segment = context.get(
    "customer_segment",
    "Unknown",
)
insights = context.get(
    "behavioral_insights",
    [],
)
evidence = context.get(
    "evidence",
    {},
)


# ============================================================
# CUSTOMER HEADER
# ============================================================

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown(
        f"## 👤 {identity.get('name', 'Unknown')}"
    )

    st.write(
        f"📍 {identity.get('city', 'Unknown')}"
    )

with col2:
    st.metric(
        "Customer Segment",
        segment,
    )

with col3:
    st.metric(
        "Last Order",
        f"{recency.get('days_since_last_order', '—')} days ago",
    )


st.divider()


# ============================================================
# KEY METRICS
# ============================================================

st.markdown("### 📊 Customer Snapshot")

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.metric(
        "Total Orders",
        ordering.get("total_orders", 0),
    )

with m2:
    st.metric(
        "Total Spend",
        format_currency(
            ordering.get("total_spend", 0)
        ),
    )

with m3:
    st.metric(
        "Avg Order Value",
        format_currency(
            ordering.get("average_order_value", 0)
        ),
    )

with m4:
    st.metric(
        "Orders / Month",
        frequency.get(
            "orders_per_month",
            0,
        ),
    )

with m5:
    st.metric(
        "Repeat Rate",
        percentage(
            loyalty.get(
                "repeat_order_rate"
            )
        ),
    )


st.divider()


# ============================================================
# BEHAVIOR OVERVIEW
# ============================================================

left, right = st.columns(2)

with left:

    st.markdown("### 🔄 Ordering Behavior")

    behavior_data = {
        "First Order":
            recency.get("first_order", "—"),

        "Last Order":
            recency.get("last_order", "—"),

        "Orders / Week":
            frequency.get(
                "orders_per_week",
                "—",
            ),

        "Orders / Month":
            frequency.get(
                "orders_per_month",
                "—",
            ),

        "Avg Days Between Orders":
            frequency.get(
                "average_days_between_orders",
                "—",
            ),

        "Customer Lifetime":
            f"{frequency.get('customer_lifetime_days', '—')} days",
    }

    for key, value in behavior_data.items():

        c1, c2 = st.columns([1, 1])

        with c1:
            st.caption(key)

        with c2:
            st.write(value)


with right:

    st.markdown("### 🕒 Time Behavior")

    time_metrics = [
        (
            "Preferred Day",
            time_behavior.get(
                "preferred_day",
                "—",
            ),
        ),
        (
            "Preferred Hour",
            (
                f"{time_behavior.get('preferred_hour')}h"
                if time_behavior.get("preferred_hour")
                is not None
                else "—"
            ),
        ),
        (
            "Breakfast Orders",
            time_behavior.get(
                "breakfast_orders",
                0,
            ),
        ),
        (
            "Lunch Orders",
            time_behavior.get(
                "lunch_orders",
                0,
            ),
        ),
        (
            "Dinner Orders",
            time_behavior.get(
                "dinner_orders",
                0,
            ),
        ),
        (
            "Late Night Orders",
            time_behavior.get(
                "late_night_orders",
                0,
            ),
        ),
    ]

    for key, value in time_metrics:

        c1, c2 = st.columns([1, 1])

        with c1:
            st.caption(key)

        with c2:
            st.write(value)


st.divider()


# ============================================================
# RECENCY + TREND
# ============================================================

st.markdown("### 📈 Customer Trends")

t1, t2, t3, t4 = st.columns(4)

with t1:

    st.metric(
        "Orders — Last 30 Days",
        recency.get(
            "orders_last_30_days",
            0,
        ),
    )

with t2:

    st.metric(
        "Orders — Last 60 Days",
        recency.get(
            "orders_last_60_days",
            0,
        ),
    )

with t3:

    st.metric(
        "Orders — Last 90 Days",
        recency.get(
            "orders_last_90_days",
            0,
        ),
    )

with t4:

    st.metric(
        "Order Trend",
        direction_label(
            order_trend.get(
                "direction"
            )
        ),
    )


st.write("")

trend_col1, trend_col2 = st.columns(2)

with trend_col1:

    st.markdown("#### Order Activity")

    st.write(
        direction_label(
            order_trend.get(
                "direction"
            )
        )
    )

    change = order_trend.get(
        "change_percentage"
    )

    if change is not None:

        st.progress(
            min(
                abs(change) / 100,
                1.0,
            )
        )

        st.caption(
            f"Change: {change:+.1f}% "
            "between the compared periods"
        )


with trend_col2:

    st.markdown("#### Spending Trend")

    st.write(
        direction_label(
            spending_trend.get(
                "direction"
            )
        )
    )

    change = spending_trend.get(
        "change_percentage"
    )

    if change is not None:

        st.progress(
            min(
                abs(change) / 100,
                1.0,
            )
        )

        st.caption(
            f"Spending change: {change:+.1f}%"
        )


st.divider()


# ============================================================
# LOYALTY + SPENDING
# ============================================================

left, right = st.columns(2)

with left:

    st.markdown("### ❤️ Loyalty Profile")

    st.metric(
        "Loyalty Level",
        loyalty.get(
            "level",
            "Unknown",
        ),
    )

    l1, l2 = st.columns(2)

    with l1:
        st.metric(
            "Repeat Orders",
            loyalty.get(
                "repeat_orders",
                0,
            ),
        )

    with l2:
        st.metric(
            "Unique Restaurants",
            loyalty.get(
                "unique_restaurants",
                0,
            ),
        )

    st.write(
        "**Top Restaurant:**",
        loyalty.get(
            "top_restaurant",
            "—",
        ),
    )

    st.write(
        "**Top Restaurant Share:**",
        percentage(
            loyalty.get(
                "top_restaurant_share"
            )
        ),
    )


with right:

    st.markdown("### 💰 Spending Profile")

    s1, s2 = st.columns(2)

    with s1:

        st.metric(
            "Spending Level",
            spending.get(
                "spending_level",
                "—",
            ),
        )

        st.metric(
            "Median Order",
            format_currency(
                spending.get(
                    "median_order_value",
                    0,
                )
            ),
        )

    with s2:

        st.metric(
            "Min Order",
            format_currency(
                spending.get(
                    "minimum_order_value",
                    0,
                )
            ),
        )

        st.metric(
            "Max Order",
            format_currency(
                spending.get(
                    "maximum_order_value",
                    0,
                )
            ),
        )

    st.write(
        "**Spending Consistency:**",
        spending.get(
            "spending_consistency",
            "—",
        ),
    )


st.divider()


# ============================================================
# CUISINE + RESTAURANT PREFERENCES
# ============================================================

left, right = st.columns(2)

with left:

    st.markdown("### 🍛 Favorite Cuisines")

    cuisines = ordering.get(
        "favorite_cuisines",
        [],
    )

    if cuisines:

        for item in cuisines:

            name = item.get(
                "name",
                "Unknown",
            )

            orders = item.get(
                "orders",
                0,
            )

            share = item.get(
                "percentage",
                0,
            )

            st.write(
                f"**{name}** — "
                f"{orders} orders "
                f"({share:.0%})"
            )

            st.progress(
                min(
                    share,
                    1.0,
                )
            )

    else:
        st.info(
            "No cuisine preference data."
        )


with right:

    st.markdown("### 🍽️ Favorite Restaurants")

    restaurants = ordering.get(
        "favorite_restaurants",
        [],
    )

    if restaurants:

        for item in restaurants:

            st.write(
                f"**{item.get('name', 'Unknown')}** — "
                f"{item.get('orders', 0)} orders"
            )

    else:
        st.info(
            "No restaurant preference data."
        )


st.divider()


# ============================================================
# BEHAVIORAL INSIGHTS
# ============================================================

st.markdown("### 🧠 Synthesized Behavioral Insights")

if insights:

    for insight in insights:

        st.info(
            f"💡 {insight}"
        )

else:

    st.info(
        "No behavioral insights available."
    )


# ============================================================
# SYNTHESIZED CONTEXT SUMMARY
# ============================================================

st.markdown("### 📝 Context Summary")

summary = context.get(
    "summary",
    "No summary available.",
)

st.success(summary)


st.divider()


# ============================================================
# RATING BEHAVIOR
# ============================================================

st.markdown("### ⭐ Rating Behavior")

r1, r2, r3 = st.columns(3)

with r1:

    average_rating = rating.get(
        "average_rating_given"
    )

    st.metric(
        "Average Rating Given",
        (
            f"{average_rating:.2f}"
            if average_rating is not None
            else "—"
        ),
    )

with r2:

    st.metric(
        "Ratings Submitted",
        rating.get(
            "ratings_count",
            0,
        ),
    )

with r3:

    positive_rate = rating.get(
        "positive_rating_rate"
    )

    st.metric(
        "Positive Rating Rate",
        (
            percentage(
                positive_rate
            )
            if positive_rate is not None
            else "—"
        ),
    )


st.divider()


# ============================================================
# EVIDENCE / PROVENANCE
# ============================================================

with st.expander(
    "🔍 Context Evidence & Provenance"
):

    st.write(
        "The synthesized profile is generated from "
        "platform-native activity rather than being "
        "stored as a manually authored profile."
    )

    e1, e2 = st.columns(2)

    with e1:

        st.write(
            "**Orders analyzed:**",
            evidence.get(
                "orders_analyzed",
                0,
            ),
        )

        st.write(
            "**First order:**",
            evidence.get(
                "first_order",
                "—",
            ),
        )

    with e2:

        st.write(
            "**Last order:**",
            evidence.get(
                "last_order",
                "—",
            ),
        )

        st.write(
            "**Data source:**",
            evidence.get(
                "data_source",
                "—",
            ),
        )


# ============================================================
# RAW CONTEXT
# ============================================================

with st.expander(
    "🧩 View Complete Synthesized Context JSON"
):

    st.json(context)


st.divider()


# ============================================================
# CONVERSATIONAL AGENT
# ============================================================

st.markdown("## 🤖 Ask the Context Agent")

st.caption(
    "Ask open-ended questions. The agent answers using the synthesized context."
)


# Suggested questions

suggestions = [
    "Tell me about this customer's recent behavior.",
    "What are this customer's strongest food preferences?",
    "Is this customer loyal to specific restaurants?",
    "How has their ordering activity changed recently?",
    "How much does this customer typically spend?",
    "When does this customer usually order food?",
]

st.markdown("#### Try asking")

cols = st.columns(3)

for index, question in enumerate(
    suggestions
):

    with cols[index % 3]:

        if st.button(
            question,
            key=f"suggestion_{index}",
            use_container_width=True,
        ):

            st.session_state[
                "selected_question"
            ] = question


question = st.text_area(
    "Your question",
    value=st.session_state.get(
        "selected_question",
        "",
    ),
    placeholder=(
        "Example: Tell me about Rahul's "
        "recent ordering behavior."
    ),
    height=100,
)


if st.button(
    "Ask Context Agent 🚀",
    type="primary",
    use_container_width=True,
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Synthesizing answer..."
        ):

            result = ask_agent(
                selected_user,
                question,
            )

        if result.get("error"):

            st.error(
                result["error"]
            )

        else:

            st.markdown("### 💬 Agent Response")

            answer = (
                result.get("answer")
                or result.get("response")
                or result.get("message")
                or str(result)
            )

            st.success(answer)

            # Show context used if the API returns it
            if result.get("context"):

                with st.expander(
                    "🔎 Context used by agent"
                ):

                    st.json(
                        result["context"]
                    )


st.divider()


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "FoodLens Context Layer • Raw activity → structured context → AI reasoning"
)

