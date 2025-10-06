from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.database import Base
from .trade_order import trade_orders

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String, index=True, nullable=False)
    status = Column(String, default='OPEN', nullable=False)
    direction = Column(String, nullable=False)
    
    volume = Column(Integer, nullable=False)
    avg_entry_price = Column(Float, nullable=False)
    avg_exit_price = Column(Float, nullable=True)

    entry_timestamp = Column(DateTime(timezone=True))
    exit_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    pnl = Column(Float, nullable=True)
    
    executions_count = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)

    owner = relationship("User", back_populates="trades")
    orders = relationship("Order", secondary=trade_orders, back_populates="trades")
