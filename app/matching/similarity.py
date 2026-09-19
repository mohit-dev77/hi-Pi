from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.context.builder import ContextBuilder
from app.database.models import User

def similar_users(user_id, limit=3):
    builder = ContextBuilder()
    try:
        all_users = builder.db.query(User).all()
        contexts = {u.user_id: builder.get_user_context(u.user_id) for u in all_users}

        def features(ctx):
            result = {}
            ordering = ctx.get("ordering_profile", {})
            behavior = ctx.get("behavior") or ctx.get("time_behavior", {})

            for item in ordering.get("favorite_cuisines", []):
                result[f"cuisine:{item['name']}"] = item["orders"]
            for item in ordering.get("favorite_restaurants", []):
                result[f"restaurant:{item['name']}"] = item["orders"]
            result["avg_order"] = ordering.get("average_order_value", 0) / 100
            result["dinner_rate"] = behavior.get("dinner_order_rate", 0)
            result["weekend_rate"] = behavior.get("weekend_order_rate", 0)
            return result

        ids = list(contexts)
        matrix = DictVectorizer().fit_transform([features(contexts[i]) for i in ids])
        target = ids.index(user_id)
        scores = cosine_similarity(matrix[target], matrix).ravel()

        results = []
        for i, uid in enumerate(ids):
            if uid != user_id:
                context = contexts[uid] or {}
                results.append({
                    "user_id": uid,
                    "name": context.get("name") or context.get("identity", {}).get("name"),
                    "city": context.get("city") or context.get("identity", {}).get("city"),
                    "similarity": round(float(scores[i]), 3)
                })
        return sorted(results, key=lambda x: x["similarity"], reverse=True)[:limit]
    finally:
        builder.close()
