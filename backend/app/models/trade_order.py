from sqlalchemy import Column, Integer, ForeignKey, Table
from ..database.database import Base

trade_orders = Table('trade_orders', Base.metadata,
    Column('trade_id', Integer, ForeignKey('trades.id')),
    Column('order_id', Integer, ForeignKey('orders.id'))
)
