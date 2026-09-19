from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.database.db import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)

class Restaurant(Base):
    __tablename__ = "restaurants"
    restaurant_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    cuisine = Column(String, nullable=False)

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    restaurant_id = Column(String, ForeignKey("restaurants.restaurant_id"), nullable=False)
    amount = Column(Float, nullable=False)
    order_time = Column(DateTime, nullable=False)
    rating = Column(Float, nullable=True)
