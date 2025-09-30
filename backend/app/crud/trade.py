from sqlalchemy.orm import Session
from app.models import trade as trade_model
from app.schemas import trade as trade_schema

def create_trade(db: Session, trade: trade_schema.TradeCreate, user_id: int):
    db_trade = trade_model.Trade(**trade.model_dump(), user_id=user_id)
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

def get_trades_by_user(db: Session, user_id: int):
    return db.query(trade_model.Trade).filter(trade_model.Trade.user_id == user_id).all()
