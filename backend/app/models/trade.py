from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database.database import Base
import datetime

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    execution_time = Column(DateTime, nullable=False)
    spread = Column(String, nullable=True)
    side = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    position_effect = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    expiration_date = Column(Date, nullable=True)
    strike_price = Column(Float, nullable=True)
    option_type = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    net_price = Column(Float, nullable=False)
    order_type = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="trades")
