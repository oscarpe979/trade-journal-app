from sqlalchemy.orm import Session
from app.crud import trade as trade_crud
from app.schemas import trade as trade_schema
from app.models import order as order_model
from app.models import trade as trade_model
from datetime import datetime

def process_new_orders(db: Session, user_id: int, new_orders: list[order_model.Order]):
    # Group orders by symbol
    orders_by_symbol = {}
    for order in new_orders:
        if order.symbol not in orders_by_symbol:
            orders_by_symbol[order.symbol] = []
        orders_by_symbol[order.symbol].append(order)

    for symbol, symbol_orders in orders_by_symbol.items():
        # Sort orders by execution time to process them in order
        symbol_orders.sort(key=lambda o: o.execution_time)
        
        db_trade = trade_crud.get_open_trade_by_symbol(db, user_id=user_id, symbol=symbol)

        if not db_trade:
            # Create a new trade if one doesn't exist
            # Find the first opening order to start the trade
            try:
                first_order = next(o for o in symbol_orders if o.position_effect == 'TO OPEN')
                symbol_orders.remove(first_order)
            except StopIteration:
                # If there are no opening orders in the new batch, we can't start a trade.
                # This could be closing orders for a trade opened in a previous session.
                # The current logic assumes that if a trade is open, it exists in the DB.
                # This case needs to be handled if we want to open and close in different uploads
                # and the open trade is not yet in the DB.
                # For now, we will assume the first upload for a symbol contains an opening order.
                continue

            direction = 'LONG' if first_order.side == 'BUY' else 'SHORT'

            trade_create = trade_schema.TradeCreate(
                symbol=symbol,
                status='OPEN',
                direction=direction,
                volume=first_order.quantity,
                avg_entry_price=first_order.price,
                entry_timestamp=first_order.execution_time,
                executions_count=1,
                notes=""
            )
            db_trade = trade_crud.create_trade(db, trade=trade_create, orders=[first_order], user_id=user_id)

        # Process remaining orders for the symbol
        for order in symbol_orders:
            update_trade_with_order(db, db_trade, order)

        # After processing all orders for the symbol, check if the trade is closed
        check_and_close_trade(db, db_trade)

def update_trade_with_order(db: Session, db_trade: trade_model.Trade, order: order_model.Order):
    # Recalculate trade properties
    total_entry_qty = 0
    total_entry_value = 0
    
    # It's better to append the order to the session's object list before recalculating
    db_trade.orders.append(order)
    db_trade.executions_count += 1

    for o in db_trade.orders:
        if o.position_effect == 'TO OPEN':
            total_entry_qty += o.quantity
            total_entry_value += o.quantity * o.price

    if total_entry_qty > 0:
        db_trade.avg_entry_price = total_entry_value / total_entry_qty
        db_trade.volume = total_entry_qty

    # Create a TradeUpdate model with only the updated fields
    trade_update_data = trade_schema.TradeUpdate(
        avg_entry_price=db_trade.avg_entry_price,
        volume=db_trade.volume,
        executions_count=db_trade.executions_count
    )
    
    trade_crud.update_trade(db, db_trade=db_trade, trade_update=trade_update_data)


def check_and_close_trade(db: Session, db_trade: trade_model.Trade):
    total_entry_qty = 0
    total_exit_qty = 0
    total_exit_value = 0

    for o in db_trade.orders:
        if o.position_effect == 'TO OPEN':
            total_entry_qty += o.quantity
        elif o.position_effect == 'TO CLOSE':
            total_exit_qty += o.quantity
            total_exit_value += o.quantity * o.price

    if total_entry_qty == total_exit_qty and total_entry_qty > 0:
        db_trade.status = 'CLOSED'
        db_trade.exit_timestamp = db_trade.orders[-1].execution_time # Last order's time
        
        if total_exit_qty > 0:
            db_trade.avg_exit_price = total_exit_value / total_exit_qty
        
        # Calculate PnL
        if db_trade.direction == 'LONG':
            pnl = (db_trade.avg_exit_price - db_trade.avg_entry_price) * db_trade.volume
        else: # SHORT
            pnl = (db_trade.avg_entry_price - db_trade.avg_exit_price) * db_trade.volume
        
        db_trade.pnl = pnl

        trade_update_data = trade_schema.TradeUpdate(
            status=db_trade.status,
            exit_timestamp=db_trade.exit_timestamp,
            avg_exit_price=db_trade.avg_exit_price,
            pnl=db_trade.pnl
        )
        trade_crud.update_trade(db, db_trade=db_trade, trade_update=trade_update_data)
