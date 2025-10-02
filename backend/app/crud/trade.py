from sqlalchemy.orm import Session
from app.models import trade as trade_model
from app.models import order as order_model
from app.schemas import trade as trade_schema

def get_trade_by_id(db: Session, trade_id: int, user_id: int):
    return db.query(trade_model.Trade).filter(trade_model.Trade.id == trade_id, trade_model.Trade.user_id == user_id).first()

def get_trades_by_user(db: Session, user_id: int):
    return db.query(trade_model.Trade).filter(trade_model.Trade.user_id == user_id).all()

def get_open_trade_by_symbol(db: Session, user_id: int, symbol: str):
    return db.query(trade_model.Trade).filter(
        trade_model.Trade.user_id == user_id,
        trade_model.Trade.symbol == symbol,
        trade_model.Trade.status == 'OPEN'
    ).first()

def create_trade(db: Session, trade: trade_schema.TradeCreate, orders: list[order_model.Order], user_id: int):
    db_trade = trade_model.Trade(**trade.model_dump(), user_id=user_id)
    db_trade.orders.extend(orders)
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

def update_trade(db: Session, db_trade: trade_model.Trade, trade_update: trade_schema.TradeUpdate, new_orders: list[order_model.Order] = None):
    update_data = trade_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_trade, key, value)
    
    if new_orders:
        db_trade.orders.extend(new_orders)
        
    db.commit()
    db.refresh(db_trade)
    return db_trade

def delete_trade(db: Session, trade_id: int, user_id: int):
    db_trade = get_trade_by_id(db, trade_id, user_id)
    if db_trade:
        # The relationship to orders should be handled by SQLAlchemy's cascade options,
        # but for explicit clarity, we can disassociate them.
        # However, the user wants to delete the constituent orders.
        for order in db_trade.orders:
            db.delete(order)
        db.delete(db_trade)
        db.commit()
    return db_trade
