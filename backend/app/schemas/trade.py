from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from .order import Order

class TradeBase(BaseModel):
    symbol: str
    status: str
    direction: str
    volume: int
    avg_entry_price: float
    avg_exit_price: Optional[float] = None
    entry_timestamp: datetime
    exit_timestamp: Optional[datetime] = None
    pnl: Optional[float] = None
    executions_count: int
    notes: Optional[str] = None

class TradeCreate(TradeBase):
    pass

class TradeUpdate(BaseModel):
    symbol: Optional[str] = None
    status: Optional[str] = None
    direction: Optional[str] = None
    volume: Optional[int] = None
    avg_entry_price: Optional[float] = None
    avg_exit_price: Optional[float] = None
    entry_timestamp: Optional[datetime] = None
    exit_timestamp: Optional[datetime] = None
    pnl: Optional[float] = None
    executions_count: Optional[int] = None
    notes: Optional[str] = None

class Trade(TradeBase):
    id: int
    user_id: int
    orders: List[Order] = []

    model_config = ConfigDict(from_attributes=True)
