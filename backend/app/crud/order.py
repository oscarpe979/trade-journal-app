from sqlalchemy.orm import Session
from app.models import order as order_model
from app.schemas import order as order_schema

def create_order(db: Session, order: order_schema.OrderCreate, user_id: int):
    db_order = order_model.Order(**order.model_dump(), user_id=user_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders_by_user(db: Session, user_id: int):
    return db.query(order_model.Order).filter(order_model.Order.user_id == user_id).all()
