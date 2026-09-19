from collections import Counter
from datetime import datetime, timedelta
from statistics import mean, median

from app.database.db import SessionLocal
from app.database.models import User, Restaurant, Order


class ContextBuilder:

    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    # ---------------------------------------------------------
    # USER
    # ---------------------------------------------------------

    def get_user(self, user_id):
        return self.db.get(User, user_id)

    # ---------------------------------------------------------
    # MAIN CONTEXT BUILDER
    # ---------------------------------------------------------

    def get_user_context(self, user_id):

        user = self.get_user(user_id)

        if not user:
            return None

        orders = (
            self.db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.order_time.asc())
            .all()
        )

        restaurants = {
            r.restaurant_id: r
            for r in self.db.query(Restaurant).all()
        }

        if not orders:
            return self._empty_context(user)

        return self._build_context(
            user=user,
            orders=orders,
            restaurants=restaurants
        )

    # ---------------------------------------------------------
    # BUILD COMPLETE CONTEXT
    # ---------------------------------------------------------

    def _build_context(self, user, orders, restaurants):

        now = datetime.now()

        # Basic calculations
        total_orders = len(orders)

        amounts = [order.amount for order in orders]

        total_spend = sum(amounts)

        average_order_value = mean(amounts)

        median_order_value = median(amounts)

        min_order_value = min(amounts)

        max_order_value = max(amounts)

        # -----------------------------------------------------
        # CUISINE
        # -----------------------------------------------------

        cuisine_counts = Counter()

        restaurant_counts = Counter()

        for order in orders:

            restaurant = restaurants.get(order.restaurant_id)

            if not restaurant:
                continue

            cuisine_counts[restaurant.cuisine] += 1

            restaurant_counts[restaurant.name] += 1

        favorite_cuisines = cuisine_counts.most_common(5)

        favorite_restaurants = restaurant_counts.most_common(5)

        # -----------------------------------------------------
        # TIME BEHAVIOR
        # -----------------------------------------------------

        dinner_orders = 0
        lunch_orders = 0
        breakfast_orders = 0
        late_night_orders = 0

        weekday_orders = 0
        weekend_orders = 0

        day_counts = Counter()

        hour_counts = Counter()

        for order in orders:

            hour = order.order_time.hour

            day_name = order.order_time.strftime("%A")

            day_counts[day_name] += 1

            hour_counts[hour] += 1

            # Time buckets

            if 6 <= hour < 11:
                breakfast_orders += 1

            elif 11 <= hour < 16:
                lunch_orders += 1

            elif 16 <= hour < 22:
                dinner_orders += 1

            else:
                late_night_orders += 1

            # Weekday/weekend

            if order.order_time.weekday() >= 5:
                weekend_orders += 1
            else:
                weekday_orders += 1

        preferred_day = (
            day_counts.most_common(1)[0][0]
            if day_counts
            else None
        )

        preferred_hour = (
            hour_counts.most_common(1)[0][0]
            if hour_counts
            else None
        )

        # -----------------------------------------------------
        # RECENCY
        # -----------------------------------------------------

        last_order = orders[-1]

        first_order = orders[0]

        days_since_last_order = (
            now - last_order.order_time
        ).days

        customer_lifetime_days = max(
            1,
            (last_order.order_time - first_order.order_time).days
        )

        # -----------------------------------------------------
        # ORDER FREQUENCY
        # -----------------------------------------------------

        orders_per_month = (
            total_orders /
            max(customer_lifetime_days / 30, 1)
        )

        orders_per_week = (
            total_orders /
            max(customer_lifetime_days / 7, 1)
        )

        # -----------------------------------------------------
        # ORDER INTERVALS
        # -----------------------------------------------------

        intervals = []

        for previous, current in zip(
            orders,
            orders[1:]
        ):

            difference = (
                current.order_time -
                previous.order_time
            ).days

            intervals.append(difference)

        average_order_interval = (
            mean(intervals)
            if intervals
            else None
        )

        # -----------------------------------------------------
        # RECENT ACTIVITY
        # -----------------------------------------------------

        last_30_days = [
            order
            for order in orders
            if (now - order.order_time).days <= 30
        ]

        last_60_days = [
            order
            for order in orders
            if (now - order.order_time).days <= 60
        ]

        last_90_days = [
            order
            for order in orders
            if (now - order.order_time).days <= 90
        ]

        orders_last_30_days = len(last_30_days)

        orders_last_60_days = len(last_60_days)

        orders_last_90_days = len(last_90_days)

        spend_last_30_days = sum(
            order.amount
            for order in last_30_days
        )

        spend_last_60_days = sum(
            order.amount
            for order in last_60_days
        )

        spend_last_90_days = sum(
            order.amount
            for order in last_90_days
        )

        # -----------------------------------------------------
        # TREND
        # -----------------------------------------------------

        trend = self._calculate_order_trend(
            orders
        )

        spending_trend = self._calculate_spending_trend(
            orders
        )

        # -----------------------------------------------------
        # LOYALTY
        # -----------------------------------------------------

        loyalty = self._calculate_loyalty(
            orders,
            restaurant_counts
        )

        # -----------------------------------------------------
        # SPENDING PROFILE
        # -----------------------------------------------------

        spending_profile = self._calculate_spending_profile(
            amounts,
            total_spend,
            average_order_value
        )

        # -----------------------------------------------------
        # RATING BEHAVIOR
        # -----------------------------------------------------

        ratings = [
            order.rating
            for order in orders
            if order.rating is not None
        ]

        rating_profile = self._calculate_rating_profile(
            ratings
        )

        # -----------------------------------------------------
        # CUSTOMER SEGMENT
        # -----------------------------------------------------

        customer_segment = self._calculate_customer_segment(
            total_orders=total_orders,
            average_order_value=average_order_value,
            orders_per_month=orders_per_month,
            loyalty=loyalty
        )

        # -----------------------------------------------------
        # BEHAVIORAL INSIGHTS
        # -----------------------------------------------------

        insights = self._generate_insights(
            user=user,
            total_orders=total_orders,
            average_order_value=average_order_value,
            favorite_cuisines=favorite_cuisines,
            loyalty=loyalty,
            spending_profile=spending_profile,
            trend=trend,
            spending_trend=spending_trend,
            days_since_last_order=days_since_last_order,
            dinner_orders=dinner_orders,
            lunch_orders=lunch_orders,
            breakfast_orders=breakfast_orders,
            late_night_orders=late_night_orders,
            weekend_orders=weekend_orders,
            weekday_orders=weekday_orders
        )

        # -----------------------------------------------------
        # SYNTHESIZED SUMMARY
        # -----------------------------------------------------

        summary = self._generate_summary(
            user=user,
            total_orders=total_orders,
            total_spend=total_spend,
            average_order_value=average_order_value,
            favorite_cuisines=favorite_cuisines,
            loyalty=loyalty,
            trend=trend,
            spending_trend=spending_trend,
            customer_segment=customer_segment,
            days_since_last_order=days_since_last_order
        )

        # -----------------------------------------------------
        # FINAL CONTEXT
        # -----------------------------------------------------

        return {

            "user_id": user.user_id,
            "name": user.name,
            "city": user.city,

            "identity": {
                "name": user.name,
                "city": user.city
            },

            "ordering_profile": {

                "total_orders": total_orders,

                "total_spend": round(
                    total_spend,
                    2
                ),

                "average_order_value": round(
                    average_order_value,
                    2
                ),

                "median_order_value": round(
                    median_order_value,
                    2
                ),

                "minimum_order_value": round(
                    min_order_value,
                    2
                ),

                "maximum_order_value": round(
                    max_order_value,
                    2
                ),

                "favorite_cuisines": [
                    {
                        "name": cuisine,
                        "orders": count,
                        "percentage": round(
                            count / total_orders,
                            3
                        )
                    }
                    for cuisine, count
                    in favorite_cuisines
                ],

                "favorite_restaurants": [
                    {
                        "name": restaurant,
                        "orders": count
                    }
                    for restaurant, count
                    in favorite_restaurants
                ]
            },

            "recency": {

                "first_order": (
                    first_order.order_time.isoformat()
                ),

                "last_order": (
                    last_order.order_time.isoformat()
                ),

                "days_since_last_order":
                    days_since_last_order,

                "orders_last_30_days":
                    orders_last_30_days,

                "orders_last_60_days":
                    orders_last_60_days,

                "orders_last_90_days":
                    orders_last_90_days
            },

            "frequency": {

                "orders_per_week":
                    round(orders_per_week, 2),

                "orders_per_month":
                    round(orders_per_month, 2),

                "average_days_between_orders":
                    round(
                        average_order_interval,
                        2
                    )
                    if average_order_interval
                    is not None
                    else None,

                "customer_lifetime_days":
                    customer_lifetime_days
            },

            "time_behavior": {

                "preferred_day":
                    preferred_day,

                "preferred_hour":
                    preferred_hour,

                "breakfast_orders":
                    breakfast_orders,

                "lunch_orders":
                    lunch_orders,

                "dinner_orders":
                    dinner_orders,

                "late_night_orders":
                    late_night_orders,

                "weekday_orders":
                    weekday_orders,

                "weekend_orders":
                    weekend_orders,

                "weekend_order_rate":
                    round(
                        weekend_orders / total_orders,
                        3
                    ),

                "dinner_order_rate":
                    round(
                        dinner_orders / total_orders,
                        3
                    )
            },
            "behavior": {
                "preferred_day":
                    preferred_day,
                "preferred_hour":
                    preferred_hour,
                "breakfast_orders":
                    breakfast_orders,
                "lunch_orders":
                    lunch_orders,
                "dinner_orders":
                    dinner_orders,
                "late_night_orders":
                    late_night_orders,
                "weekday_orders":
                    weekday_orders,
                "weekend_orders":
                    weekend_orders,
                "weekend_order_rate":
                    round(
                        weekend_orders / total_orders,
                        3
                    ),
                "dinner_order_rate":
                    round(
                        dinner_orders / total_orders,
                        3
                    )
            },

            "loyalty": loyalty,

            "spending": spending_profile,

            "spending_trend": spending_trend,

            "order_trend": trend,

            "rating_behavior": rating_profile,

            "customer_segment": customer_segment,

            "behavioral_insights": insights,

            "evidence": {

                "orders_analyzed":
                    total_orders,

                "first_order":
                    first_order.order_time.isoformat(),

                "last_order":
                    last_order.order_time.isoformat(),

                "data_source":
                    "platform-native orders, restaurants and ratings"
            },

            "summary": summary
        }

    # =========================================================
    # TREND ANALYSIS
    # =========================================================

    def _calculate_order_trend(self, orders):

        if len(orders) < 4:

            return {
                "direction": "insufficient_data",
                "recent_orders": len(orders),
                "previous_orders": 0,
                "change_percentage": None
            }

        midpoint = len(orders) // 2

        previous = orders[:midpoint]

        recent = orders[midpoint:]

        previous_count = len(previous)

        recent_count = len(recent)

        if previous_count == 0:

            return {
                "direction": "insufficient_data"
            }

        change = (
            (recent_count - previous_count)
            / previous_count
        ) * 100

        if change > 20:
            direction = "increasing"

        elif change < -20:
            direction = "decreasing"

        else:
            direction = "stable"

        return {

            "direction": direction,

            "recent_orders":
                recent_count,

            "previous_orders":
                previous_count,

            "change_percentage":
                round(change, 2)
        }

    # =========================================================
    # SPENDING TREND
    # =========================================================

    def _calculate_spending_trend(self, orders):

        if len(orders) < 4:

            return {
                "direction": "insufficient_data"
            }

        midpoint = len(orders) // 2

        previous = orders[:midpoint]

        recent = orders[midpoint:]

        previous_spend = sum(
            order.amount
            for order in previous
        )

        recent_spend = sum(
            order.amount
            for order in recent
        )

        if previous_spend == 0:

            return {
                "direction": "insufficient_data"
            }

        change = (
            (recent_spend - previous_spend)
            / previous_spend
        ) * 100

        if change > 20:
            direction = "increasing"

        elif change < -20:
            direction = "decreasing"

        else:
            direction = "stable"

        return {

            "direction": direction,

            "previous_spend":
                round(previous_spend, 2),

            "recent_spend":
                round(recent_spend, 2),

            "change_percentage":
                round(change, 2)
        }

    # =========================================================
    # LOYALTY
    # =========================================================

    def _calculate_loyalty(
        self,
        orders,
        restaurant_counts
    ):

        total_orders = len(orders)

        unique_restaurants = len(
            restaurant_counts
        )

        repeat_orders = sum(
            max(0, count - 1)
            for count in restaurant_counts.values()
        )

        repeat_rate = (
            repeat_orders / total_orders
            if total_orders
            else 0
        )

        top_restaurant = (
            restaurant_counts.most_common(1)[0]
            if restaurant_counts
            else None
        )

        top_restaurant_share = (
            top_restaurant[1] / total_orders
            if top_restaurant
            else 0
        )

        if repeat_rate >= 0.60:
            level = "high"

        elif repeat_rate >= 0.30:
            level = "medium"

        else:
            level = "low"

        return {

            "level": level,

            "repeat_order_rate":
                round(repeat_rate, 3),

            "unique_restaurants":
                unique_restaurants,

            "repeat_orders":
                repeat_orders,

            "top_restaurant":
                top_restaurant[0]
                if top_restaurant
                else None,

            "top_restaurant_share":
                round(
                    top_restaurant_share,
                    3
                )
        }

    # =========================================================
    # SPENDING PROFILE
    # =========================================================

    def _calculate_spending_profile(
        self,
        amounts,
        total_spend,
        average_order_value
    ):

        if not amounts:

            return {}

        variance = mean(
            (amount - average_order_value) ** 2
            for amount in amounts
        )

        standard_deviation = variance ** 0.5

        coefficient_variation = (
            standard_deviation /
            average_order_value
            if average_order_value
            else 0
        )

        if average_order_value >= 600:
            spending_level = "high"

        elif average_order_value >= 350:
            spending_level = "medium"

        else:
            spending_level = "low"

        if coefficient_variation > 0.50:
            consistency = "highly variable"

        elif coefficient_variation > 0.25:
            consistency = "moderately variable"

        else:
            consistency = "consistent"

        return {

            "spending_level":
                spending_level,

            "total_spend":
                round(total_spend, 2),

            "average_order_value":
                round(average_order_value, 2),

            "median_order_value":
                round(median(amounts), 2),

            "minimum_order_value":
                round(min(amounts), 2),

            "maximum_order_value":
                round(max(amounts), 2),

            "standard_deviation":
                round(
                    standard_deviation,
                    2
                ),

            "spending_consistency":
                consistency,

            "coefficient_of_variation":
                round(
                    coefficient_variation,
                    3
                )
        }

    # =========================================================
    # RATINGS
    # =========================================================

    def _calculate_rating_profile(
        self,
        ratings
    ):

        if not ratings:

            return {

                "average_rating_given":
                    None,

                "ratings_count":
                    0,

                "positive_rating_rate":
                    None
            }

        positive = sum(
            rating >= 4
            for rating in ratings
        )

        return {

            "average_rating_given":
                round(
                    mean(ratings),
                    2
                ),

            "ratings_count":
                len(ratings),

            "positive_rating_rate":
                round(
                    positive / len(ratings),
                    3
                )
        }

    # =========================================================
    # CUSTOMER SEGMENT
    # =========================================================

    def _calculate_customer_segment(
        self,
        total_orders,
        average_order_value,
        orders_per_month,
        loyalty
    ):

        if (
            orders_per_month >= 8
            and loyalty["level"] == "high"
        ):

            return "Highly loyal frequent customer"

        if (
            orders_per_month >= 6
            and average_order_value >= 550
        ):

            return "Frequent premium customer"

        if (
            orders_per_month >= 4
        ):

            return "Frequent customer"

        if (
            average_order_value >= 550
        ):

            return "Premium occasional customer"

        if (
            orders_per_month <= 1
        ):

            return "Occasional customer"

        return "Regular customer"

    # =========================================================
    # BEHAVIORAL INSIGHTS
    # =========================================================

    def _generate_insights(
        self,
        user,
        total_orders,
        average_order_value,
        favorite_cuisines,
        loyalty,
        spending_profile,
        trend,
        spending_trend,
        days_since_last_order,
        dinner_orders,
        lunch_orders,
        breakfast_orders,
        late_night_orders,
        weekend_orders,
        weekday_orders
    ):

        insights = []

        # Cuisine

        if favorite_cuisines:

            cuisine = favorite_cuisines[0][0]

            count = favorite_cuisines[0][1]

            percentage = count / total_orders

            insights.append(
                f"{cuisine} is the most frequently "
                f"ordered cuisine ({percentage:.0%} "
                f"of orders)."
            )

        # Loyalty

        if loyalty["level"] == "high":

            insights.append(
                "Customer shows strong restaurant "
                "loyalty and frequently repeats "
                "previous restaurants."
            )

        elif loyalty["level"] == "medium":

            insights.append(
                "Customer shows moderate restaurant "
                "loyalty."
            )

        else:

            insights.append(
                "Customer frequently explores "
                "different restaurants."
            )

        # Spending

        insights.append(
            f"Average order value is "
            f"₹{average_order_value:.0f}, indicating "
            f"{spending_profile['spending_level']} "
            f"average order spending."
        )

        # Order trend

        if trend["direction"] == "increasing":

            insights.append(
                "Ordering activity is increasing "
                "compared with the earlier period."
            )

        elif trend["direction"] == "decreasing":

            insights.append(
                "Ordering activity is decreasing "
                "compared with the earlier period."
            )

        else:

            insights.append(
                "Ordering activity has remained "
                "relatively stable."
            )

        # Spending trend

        if spending_trend.get("direction") == "increasing":

            insights.append(
                "Customer spending has increased "
                "in the recent period."
            )

        elif spending_trend.get("direction") == "decreasing":

            insights.append(
                "Customer spending has decreased "
                "in the recent period."
            )

        # Recency

        if days_since_last_order <= 7:

            insights.append(
                "Customer has ordered within the "
                "last week."
            )

        elif days_since_last_order <= 30:

            insights.append(
                "Customer has been active within "
                "the last month."
            )

        else:

            insights.append(
                "Customer has not ordered recently."
            )

        # Time preference

        if dinner_orders > lunch_orders:

            insights.append(
                "Customer is more dinner-oriented "
                "than lunch-oriented."
            )

        elif lunch_orders > dinner_orders:

            insights.append(
                "Customer is more lunch-oriented."
            )

        return insights

    # =========================================================
    # SYNTHESIZED SUMMARY
    # =========================================================

    def _generate_summary(
        self,
        user,
        total_orders,
        total_spend,
        average_order_value,
        favorite_cuisines,
        loyalty,
        trend,
        spending_trend,
        customer_segment,
        days_since_last_order
    ):

        cuisines = ", ".join(
            cuisine
            for cuisine, _
            in favorite_cuisines[:3]
        )

        trend_text = trend["direction"]

        spending_text = spending_trend.get(
            "direction",
            "unknown"
        )

        return (
            f"{user.name} is a {customer_segment.lower()} "
            f"on the platform. They have placed "
            f"{total_orders} orders with total recorded "
            f"spending of ₹{total_spend:.0f} and an "
            f"average order value of ₹{average_order_value:.0f}. "
            f"Their strongest cuisine preferences are "
            f"{cuisines}. Restaurant loyalty is "
            f"{loyalty['level']}. Ordering activity is "
            f"{trend_text}, while spending is "
            f"{spending_text}. Their last recorded order "
            f"was {days_since_last_order} days ago."
        )

    # =========================================================
    # EMPTY USER
    # =========================================================

    def _empty_context(self, user):

        return {

            "user_id": user.user_id,
            "name": user.name,
            "city": user.city,

            "identity": {
                "name": user.name,
                "city": user.city
            },

            "ordering_profile": {},

            "recency": {},

            "frequency": {},

            "time_behavior": {},

            "loyalty": {},

            "spending": {},

            "spending_trend": {},

            "order_trend": {},

            "rating_behavior": {},

            "customer_segment":
                "No activity",

            "behavioral_insights": [],

            "evidence": {
                "orders_analyzed": 0,
                "data_source":
                    "platform-native orders, restaurants and ratings"
            },

            "summary":
                f"{user.name} exists in the platform "
                f"but has no recorded orders."
        }