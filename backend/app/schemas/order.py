from pydantic import BaseModel, field_validator
from datetime import datetime, date
from typing import Optional
import math

class OrderBase(BaseModel):
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

    @field_validator('strike_price', 'price', 'net_price', mode='before')
    @classmethod
    def validate_float_fields(cls, field_value):
        if field_value is None:
            return field_value
        if isinstance(field_value, float):
            if math.isnan(field_value) or math.isinf(field_value):
                return 0.0  # or None, depending on your business logic
        return field_value

class OrderCreate(OrderBase):
    pass

class OrderUpdate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # replaces orm_mode in Pydantic v2
