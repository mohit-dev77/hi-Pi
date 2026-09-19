import random
from datetime import datetime, timedelta
from app.database.db import Base, engine, SessionLocal
from app.database.models import User, Restaurant, Order

def seed(num_users=150):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = SessionLocal()

    # -------------------------
    # USERS
    # -------------------------
    cities = ["Noida", "Delhi", "Gurgaon", "Mumbai", "Bangalore", "Hyderabad"]
    first_names = ["Rahul", "Priya", "Amit", "Neha", "Arjun", "Sneha", "Rohit", "Kiran", "Anjali", "Vikram"]
    last_names = ["Sharma", "Singh", "Kumar", "Verma", "Mehta", "Patel", "Reddy", "Iyer", "Das", "Gupta"]

    users = []
    for i in range(1001, 1001 + num_users):
        if i == 1001:
            name = "Rahul Sharma"
            city = "Noida"
        else:
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            city = random.choice(cities)
        users.append(User(user_id=f"U{i}", name=name, city=city))

    # -------------------------
    # RESTAURANTS
    # -------------------------
    restaurants = [
        Restaurant(restaurant_id="R101", name="Biryani Blues", cuisine="Biryani"),
        Restaurant(restaurant_id="R102", name="Mainland China", cuisine="Chinese"),
        Restaurant(restaurant_id="R103", name="Punjabi Tadka", cuisine="North Indian"),
        Restaurant(restaurant_id="R104", name="Dominos", cuisine="Pizza"),
        Restaurant(restaurant_id="R105", name="South Spice", cuisine="South Indian"),
        Restaurant(restaurant_id="R106", name="Healthy Bowl", cuisine="Healthy"),
    ]

    db.add_all(users + restaurants)
    db.commit()

    # -------------------------
    # ORDERS
    # -------------------------
    start_date = datetime(2026, 1, 1, 12, 0)  # Starting from January 1, 2026
    idx = 1

    for user in users:
        num_orders = random.randint(5, 20)  # Each user places 5–20 orders
        for _ in range(num_orders):
            restaurant = random.choice(restaurants)
            amount = random.randint(200, 800)  # ₹200–₹800
            rating = random.choice([3, 4, 5, None])  # Some orders unrated
            hour = random.choice([13, 19, 20])  # Lunch / dinner hours
            
            # Spread orders across 150 days forward from the start date
            random_day_offset = random.randint(0, 150)
            dt = start_date + timedelta(days=random_day_offset, hours=hour, minutes=random.randint(0, 59))

            db.add(Order(
                order_id=f"O{idx:05d}",
                user_id=user.user_id,
                restaurant_id=restaurant.restaurant_id,
                amount=amount,
                order_time=dt,
                rating=rating
            ))
            idx += 1

    db.commit()
    db.close()
    print(f"Seeded {num_users} users with synthetic orders spread across a 150-day window.")

if __name__ == "__main__":
    seed(150)  # Generate 150 users