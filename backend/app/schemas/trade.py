from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class TradeBase(BaseModel):
    execution_time: datetime
    spread: Optional[str] = None
    side: str
    quantity: int
    position_effect: str
    symbol: str
    expiration_date: Optional[date] = None
    strike_price: Optional[float] = None
    option_type: Optional[str] = None
    price: float
    net_price: float
    order_type: Optional[str] = None
    notes: Optional[str] = None

class TradeCreate(TradeBase):
    pass

class TradeUpdate(TradeBase):
    pass

class Trade(TradeBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
