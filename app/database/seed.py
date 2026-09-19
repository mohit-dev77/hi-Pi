from datetime import datetime, timedelta
from app.database.db import Base, engine, SessionLocal
from app.database.models import User, Restaurant, Order

def seed():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = SessionLocal()

    users = [
        User(user_id="U1001", name="Rahul Sharma", city="Noida"),
        User(user_id="U1002", name="Priya Singh", city="Delhi"),
        User(user_id="U1003", name="Amit Kumar", city="Gurgaon"),
        User(user_id="U1004", name="Neha Verma", city="Noida"),
        User(user_id="U1005", name="Arjun Mehta", city="Delhi"),
    ]
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

    patterns = {
        "U1001": [
            ("R101",450,5),("R102",320,4),("R101",510,5),("R103",420,4),
            ("R101",480,5),("R102",390,4),("R101",520,5),("R103",460,4),
            ("R101",490,5),("R102",350,4),("R103",430,5),("R101",550,5)
        ],
        "U1002": [
            ("R104",240,4),("R105",310,4),("R104",220,3),("R105",350,5),
            ("R106",420,4),("R104",260,4),("R105",300,4),("R106",390,5)
        ],
        "U1003": [
            ("R103",500,5),("R104",280,4),("R103",450,5),("R101",600,4),
            ("R103",520,5),("R104",260,3),("R101",580,5),("R103",490,4)
        ],
        "U1004": [
            ("R106",380,5),("R105",330,5),("R106",420,4),("R105",290,4),
            ("R106",410,5),("R104",250,3)
        ],
        "U1005": [
            ("R102",700,5),("R101",650,5),("R102",720,4),("R103",680,5),
            ("R102",750,5),("R101",620,4)
        ]
    }

    base = datetime(2026, 9, 1, 19, 30)
    idx = 1
    for user_id, rows in patterns.items():
        for i, (restaurant_id, amount, rating) in enumerate(rows):
            hour = 20 if user_id in {"U1001","U1003","U1005"} else (13 if i % 2 == 0 else 19)
            dt = (base - timedelta(days=i*3)).replace(hour=hour, minute=(i*7)%60)
            db.add(Order(
                order_id=f"O{idx:04d}", user_id=user_id, restaurant_id=restaurant_id,
                amount=amount, order_time=dt, rating=rating
            ))
            idx += 1
    db.commit()
    db.close()
    print("Seeded foodlens.db")

if __name__ == "__main__":
    seed()
