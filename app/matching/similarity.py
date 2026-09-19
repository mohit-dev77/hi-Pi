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
            for item in ctx["ordering_profile"]["favorite_cuisines"]:
                result[f"cuisine:{item['name']}"] = item["orders"]
            for item in ctx["ordering_profile"]["favorite_restaurants"]:
                result[f"restaurant:{item['name']}"] = item["orders"]
            result["avg_order"] = ctx["ordering_profile"]["average_order_value"] / 100
            result["dinner_rate"] = ctx["behavior"]["dinner_order_rate"]
            result["weekend_rate"] = ctx["behavior"]["weekend_order_rate"]
            return result

        ids = list(contexts)
        matrix = DictVectorizer().fit_transform([features(contexts[i]) for i in ids])
        target = ids.index(user_id)
        scores = cosine_similarity(matrix[target], matrix).ravel()

        results = []
        for i, uid in enumerate(ids):
            if uid != user_id:
                results.append({
                    "user_id": uid,
                    "name": contexts[uid]["name"],
                    "city": contexts[uid]["city"],
                    "similarity": round(float(scores[i]), 3)
                })
        return sorted(results, key=lambda x: x["similarity"], reverse=True)[:limit]
    finally:
        builder.close()
