from sqlalchemy.orm import Session
from app.crud import trade as trade_crud
from app.schemas import trade as trade_schema
from app.models import order as order_model
from app.models import trade as trade_model
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_new_orders(db: Session, user_id: int, new_orders: list[order_model.Order]):
    logger.info("--- Starting in-memory processing of new orders ---")

    # 1. Get unique symbols and fetch all relevant open trades in one go
    symbols = list(set(o.symbol for o in new_orders))
    open_trades_from_db = trade_crud.get_open_trades_by_symbols(db, user_id=user_id, symbols=symbols)
    
    # 2. Create an in-memory map for active trades being processed, initially populated with current open trades from DB if any.
    trades_map = {trade.symbol: trade for trade in open_trades_from_db}
    closed_trades = []
    
    # 3. Sort orders chronologically
    new_orders.sort(key=lambda o: o.execution_time)

    # 4. Process each order in memory
    for order in new_orders:
        logger.info(f"Processing order in-memory: {order.id}, {order.symbol}, {order.side}, {order.quantity}")
        trade = trades_map.get(order.symbol)

        if order.position_effect == 'TO OPEN':
            direction = 'LONG' if order.side == 'BUY' else 'SHORT'
            if trade:
                if trade.status == 'CLOSED':
                    # This should not happen if the logic is correct
                    logger.error(f"Found a closed trade in the trades_map for symbol {order.symbol}")
                    # I will create a new trade anyway
                    new_trade = _create_new_trade(order, user_id)
                    trades_map[order.symbol] = new_trade
                elif trade.direction == direction:
                    # Add to existing open trade
                    _update_trade_with_order(trade, order)
                else:
                    logger.error(
                        f"Data anomaly: Received a 'TO OPEN' order (ID: {order.id}) for {order.symbol} "
                        f"with direction {direction}, but an open trade (ID: {trade.id}) "
                        f"already exists in the opposite direction ({trade.direction}). "
                        f"This order will be ignored."
                    )
            else:
                # No trade for this symbol, create a new one
                new_trade = _create_new_trade(order, user_id)
                trades_map[order.symbol] = new_trade
        
        elif order.position_effect == 'TO CLOSE':
            if trade:
                _update_trade_with_order(trade, order)
                if _close_trade_if_fully_exited(trade):
                    closed_trades.append(trade)
                    del trades_map[order.symbol]
            else:
                logger.warning(f"Orphan closing order found (no open trade): {order.id} for {order.symbol}")

    # 5. Batch save all changes to the database
    logger.info("--- Committing all changes to the database ---")
    for symbol, trade in trades_map.items():
        db.merge(trade)

    for trade in closed_trades:
        db.merge(trade)
    
    db.commit()
    logger.info("--- Database commit successful ---")

def _create_new_trade(order: order_model.Order, user_id: int) -> trade_model.Trade:
    logger.info(f"Creating new trade object in-memory for {order.symbol}")
    direction = 'LONG' if order.side == 'BUY' else 'SHORT'
    
    # Create a new ORM model instance directly
    new_trade = trade_model.Trade(
        symbol=order.symbol,
        user_id=user_id,
        status='OPEN',
        direction=direction,
        volume=order.quantity,
        avg_entry_price=order.price,
        entry_timestamp=order.execution_time,
        executions_count=1,
        orders=[order]
    )
    return new_trade

def _update_trade_with_order(trade: trade_model.Trade, order: order_model.Order):
    logger.info(f"Updating trade in-memory for {trade.symbol} with order {order.id}")
    
    trade.orders.append(order)
    trade.executions_count += 1

    # Recalculate trade properties
    total_entry_qty = 0
    total_entry_value = 0
    for o in trade.orders:
        if o.position_effect == 'TO OPEN':
            total_entry_qty += abs(o.quantity)
            total_entry_value += abs(o.quantity * o.price)

    if total_entry_qty > 0:
        trade.avg_entry_price = round(total_entry_value / total_entry_qty, 4)
        trade.volume = total_entry_qty

def _close_trade_if_fully_exited(trade: trade_model.Trade) -> bool:
    logger.info(f"Checking to close trade in-memory for {trade.symbol}")
    total_entry_qty = abs(sum(o.quantity for o in trade.orders if o.position_effect == 'TO OPEN'))
    total_exit_qty = abs(sum(o.quantity for o in trade.orders if o.position_effect == 'TO CLOSE'))

    logger.info(f"Trade {trade.symbol} quantities: entry={total_entry_qty}, exit={total_exit_qty}")

    if total_entry_qty == total_exit_qty and total_entry_qty > 0:
        logger.info(f"Closing trade in-memory for {trade.symbol}")
        trade.status = 'CLOSED'
        
        # Find the latest execution time among closing orders for the exit timestamp
        exit_orders = [o for o in trade.orders if o.position_effect == 'TO CLOSE']
        trade.exit_timestamp = max(o.execution_time for o in exit_orders)

        total_exit_value = abs(sum(o.quantity * o.price for o in exit_orders))
        if total_exit_qty > 0:
            trade.avg_exit_price = total_exit_value / total_exit_qty
        
        if trade.direction == 'LONG':
            pnl = round(((trade.avg_exit_price - trade.avg_entry_price) * trade.volume), 3)
        else: # SHORT
            pnl = round(((trade.avg_entry_price - trade.avg_exit_price) * trade.volume), 3)
        
        trade.pnl = pnl
        return True
    return False