from collections import Counter
from statistics import mean
from app.database.db import SessionLocal
from app.database.models import User, Restaurant, Order

class ContextBuilder:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def get_user_context(self, user_id):
        user = self.db.get(User, user_id)
        if not user:
            return None

        orders = self.db.query(Order).filter(Order.user_id == user_id).all()
        restaurants = {r.restaurant_id: r for r in self.db.query(Restaurant).all()}

        cuisines = Counter()
        restaurant_counts = Counter()
        amounts, ratings = [], []
        dinner = weekend = 0

        for order in orders:
            restaurant = restaurants[order.restaurant_id]
            cuisines[restaurant.cuisine] += 1
            restaurant_counts[restaurant.name] += 1
            amounts.append(order.amount)
            if order.rating is not None:
                ratings.append(order.rating)
            dinner += int(order.order_time.hour >= 17)
            weekend += int(order.order_time.weekday() >= 5)

        total_orders = len(orders)
        total_spend = sum(amounts)
        avg_order = mean(amounts) if amounts else 0
        dinner_rate = dinner / total_orders if total_orders else 0
        weekend_rate = weekend / total_orders if total_orders else 0
        repeat_orders = sum(max(0, count-1) for count in restaurant_counts.values())
        repeat_rate = repeat_orders / total_orders if total_orders else 0

        if avg_order >= 550:
            segment = "Premium-leaning"
        elif avg_order >= 350:
            segment = "Mid-range frequent"
        else:
            segment = "Budget-conscious"

        favorite_cuisines = cuisines.most_common(3)
        favorite_restaurants = restaurant_counts.most_common(3)

        summary = (
            f"{user.name} is a {segment.lower()} customer in {user.city}. "
            f"They have placed {total_orders} orders with an average order value of "
            f"₹{avg_order:.0f}. Their strongest cuisine preferences are "
            f"{', '.join(c for c, _ in favorite_cuisines)}. "
            f"They order during dinner {dinner_rate:.0%} of the time and "
            f"repeat restaurants at a rate of {repeat_rate:.0%}. "
            f"Total recorded spending is ₹{total_spend:.0f}."
        )

        return {
            "user_id": user.user_id,
            "name": user.name,
            "city": user.city,
            "ordering_profile": {
                "total_orders": total_orders,
                "total_spend": round(total_spend, 2),
                "average_order_value": round(avg_order, 2),
                "favorite_cuisines": [{"name": c, "orders": n} for c,n in favorite_cuisines],
                "favorite_restaurants": [{"name": r, "orders": n} for r,n in favorite_restaurants],
                "repeat_order_rate": round(repeat_rate, 3)
            },
            "behavior": {
                "dinner_order_rate": round(dinner_rate, 3),
                "weekend_order_rate": round(weekend_rate, 3),
                "customer_segment": segment
            },
            "rating_behavior": {
                "average_rating_given": round(mean(ratings), 2) if ratings else None,
                "ratings_count": len(ratings)
            },
            "evidence": {
                "orders_analyzed": total_orders,
                "data_source": "platform-native order, restaurant and rating events"
            },
            "summary": summary
        }
