from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from app.crud import trade as trade_crud
from tests.api.v1.test_user import get_user_token

def upload_orders(client: TestClient, token: str, csv_data: str):
    return client.post(
        "/api/v1/orders/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("orders.csv", csv_data, "text/csv")},
    )

def test_get_trades_unauthenticated(client: TestClient):
    response = client.get("/api/v1/trades")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}

def test_get_trades_success(client: TestClient, db_session: Session):
    # 1. Create a user and get a token
    email = "trade_tester@example.com"
    password = "testpassword"
    token, user_id = get_user_token(client, email, password)

    # 2. Upload orders that create a closed trade
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-10-01 10:00:00,STOCK,BUY,10,TO OPEN,MSFT,,,STOCK,10.0,10.0,LMT\n"
        "2025-10-01 10:05:00,STOCK,SELL,10,TO CLOSE,MSFT,,,STOCK,12.0,12.0,LMT\n"
    )
    upload_response = upload_orders(client, token, csv_data)
    assert upload_response.status_code == status.HTTP_201_CREATED

    # 3. Get trades
    response = client.get("/api/v1/trades", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK

    trades = response.json()
    assert len(trades) == 1
    trade = trades[0]
    assert trade["symbol"] == "MSFT"
    assert trade["status"] == "CLOSED"
    assert trade["volume"] == 10
    assert trade["avg_entry_price"] == 10.0
    assert trade["avg_exit_price"] == 12.0
    assert trade["pnl"] == 20.0

def test_get_trade_by_id_success(client: TestClient, db_session: Session):
    # 1. Create a user and get a token
    email = "trade_by_id@example.com"
    password = "testpassword"
    token, user_id = get_user_token(client, email, password)

    # 2. Upload orders
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-10-02 10:00:00,STOCK,BUY,5,TO OPEN,GOOG,,,STOCK,5.0,5.0,LMT\n"
        "2025-10-02 10:05:00,STOCK,SELL,5,TO CLOSE,GOOG,,,STOCK,6.0,6.0,LMT\n"
    )
    upload_orders(client, token, csv_data)

    # 3. Get the created trade
    trades = trade_crud.get_trades_by_user(db=db_session, user_id=user_id)
    trade_id = trades[0].id

    # 4. Get trade by id
    response = client.get(f"/api/v1/trades/{trade_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["symbol"] == "GOOG"

def test_get_trade_by_id_not_found(client: TestClient):
    # 1. Create a user and get a token
    email = "trade_not_found@example.com"
    password = "testpassword"
    token, _ = get_user_token(client, email, password)

    # 2. Request a non-existent trade
    response = client.get("/api/v1/trades/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_trade_success(client: TestClient, db_session: Session):
    # 1. Create a user and get a token
    email = "delete_trade@example.com"
    password = "testpassword"
    token, user_id = get_user_token(client, email, password)

    # 2. Upload orders
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-10-03 10:00:00,STOCK,BUY,2,TO OPEN,AMZN,,,STOCK,2.0,2.0,LMT\n"
        "2025-10-03 10:05:00,STOCK,SELL,2,TO CLOSE,AMZN,,,STOCK,2.5,2.5,LMT\n"
    )
    upload_orders(client, token, csv_data)

    # 3. Get the created trade and its orders
    trades = trade_crud.get_trades_by_user(db=db_session, user_id=user_id)
    trade_id = trades[0].id
    order_ids = [order.id for order in trades[0].orders]

    # 4. Delete the trade
    response = client.delete(f"/api/v1/trades/{trade_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK

    # 5. Verify the trade and its orders are deleted
    deleted_trade = trade_crud.get_trade_by_id(db=db_session, trade_id=trade_id, user_id=user_id)
    assert deleted_trade is None
    
    # This part of the test needs to be improved, as we don't have a get_order_by_id function
    # For now, we can assume that if the trade is deleted, the orders are also deleted due to the cascade.

def test_trade_creation_multiple_orders(client: TestClient, db_session: Session):
    # 1. Create a user and get a token
    email = "multi_order_trade@example.com"
    password = "testpassword"
    token, user_id = get_user_token(client, email, password)

    # 2. Upload orders
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-10-04 10:00:00,STOCK,BUY,5,TO OPEN,TSLA,,,STOCK,8.0,8.0,LMT\n"
        "2025-10-04 10:01:00,STOCK,BUY,5,TO OPEN,TSLA,,,STOCK,8.5,8.5,LMT\n"
        "2025-10-04 10:05:00,STOCK,SELL,10,TO CLOSE,TSLA,,,STOCK,9.0,9.0,LMT\n"
    )
    upload_orders(client, token, csv_data)

    # 3. Get trades and assert
    response = client.get("/api/v1/trades", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK

    trades = response.json()
    assert len(trades) == 1
    trade = trades[0]
    assert trade["symbol"] == "TSLA"
    assert trade["status"] == "CLOSED"
    assert trade["volume"] == 10
    assert trade["avg_entry_price"] == 8.25 # (5*8 + 5*8.5) / 10
    assert trade["avg_exit_price"] == 9.0
    assert round(trade["pnl"], 2) == 7.5 # (9.0 - 8.25) * 10

def test_trade_creation_multiple_symbols(client: TestClient, db_session: Session):
    # 1. Create a user and get a token
    email = "multi_symbol_trade@example.com"
    password = "testpassword"
    token, user_id = get_user_token(client, email, password)

    # 2. Upload orders for multiple symbols
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-10-05 10:00:00,STOCK,BUY,10,TO OPEN,AAPL,,,STOCK,10.0,10.0,LMT\n"
        "2025-10-05 10:05:00,STOCK,SELL,10,TO CLOSE,AAPL,,,STOCK,12.0,12.0,LMT\n"
        "2025-10-05 10:10:00,STOCK,BUY,5,TO OPEN,GOOG,,,STOCK,5.0,5.0,LMT\n"
        "2025-10-05 10:15:00,STOCK,SELL,5,TO CLOSE,GOOG,,,STOCK,6.0,6.0,LMT\n"
        "2025-10-05 10:20:00,STOCK,BUY,2,TO OPEN,TSLA,,,STOCK,8.0,8.0,LMT\n"
        "2025-10-05 10:25:00,STOCK,SELL,2,TO CLOSE,TSLA,,,STOCK,9.0,9.0,LMT\n"
    )
    upload_orders(client, token, csv_data)

    # 3. Get trades and assert
    response = client.get("/api/v1/trades", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK

    trades = response.json()
    assert len(trades) == 3

    trades_by_symbol = {trade["symbol"]: trade for trade in trades}
    assert set(trades_by_symbol.keys()) == {"AAPL", "GOOG", "TSLA"}

    # Assert AAPL trade
    aapl_trade = trades_by_symbol["AAPL"]
    assert aapl_trade["status"] == "CLOSED"
    assert aapl_trade["volume"] == 10
    assert aapl_trade["avg_entry_price"] == 10.0
    assert aapl_trade["avg_exit_price"] == 12.0
    assert aapl_trade["pnl"] == 20.0

    # Assert GOOG trade
    goog_trade = trades_by_symbol["GOOG"]
    assert goog_trade["status"] == "CLOSED"
    assert goog_trade["volume"] == 5
    assert goog_trade["avg_entry_price"] == 5.0
    assert goog_trade["avg_exit_price"] == 6.0
    assert goog_trade["pnl"] == 5.0

    # Assert TSLA trade
    tsla_trade = trades_by_symbol["TSLA"]
    assert tsla_trade["status"] == "CLOSED"
    assert tsla_trade["volume"] == 2
    assert tsla_trade["avg_entry_price"] == 8.0
    assert tsla_trade["avg_exit_price"] == 9.0
    assert tsla_trade["pnl"] == 2.0

def test_complex_trade_scenario(client: TestClient, db_session: Session):
    # 1. Create a user and get a token
    email = "complex_trade@example.com"
    password = "testpassword"
    token, user_id = get_user_token(client, email, password)

    # 2. Upload orders for the complex scenario
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-10-06 10:00:00,STOCK,BUY,50,TO OPEN,NVDA,,,STOCK,10.0,10.0,LMT\n"
        "2025-10-06 10:01:00,STOCK,BUY,50,TO OPEN,NVDA,,,STOCK,10.5,10.5,LMT\n"
        "2025-10-06 10:05:00,STOCK,SELL,25,TO CLOSE,NVDA,,,STOCK,12.0,12.0,LMT\n"
        "2025-10-06 10:06:00,STOCK,SELL,25,TO CLOSE,NVDA,,,STOCK,12.5,12.5,LMT\n"
        "2025-10-06 10:07:00,STOCK,SELL,25,TO CLOSE,NVDA,,,STOCK,13.0,13.0,LMT\n"
        "2025-10-06 10:08:00,STOCK,SELL,25,TO CLOSE,NVDA,,,STOCK,13.5,13.5,LMT\n"
        "2025-10-06 10:18:00,STOCK,SELL,20,TO OPEN,NVDA,,,STOCK,5.0,5.0,LMT\n"
        "2025-10-06 10:19:00,STOCK,SELL,20,TO OPEN,NVDA,,,STOCK,5.2,5.2,LMT\n"
        "2025-10-06 10:20:00,STOCK,SELL,30,TO OPEN,NVDA,,,STOCK,5.4,5.4,LMT\n"
        "2025-10-06 10:21:00,STOCK,SELL,30,TO OPEN,NVDA,,,STOCK,5.6,5.6,LMT\n"
        "2025-10-06 10:30:00,STOCK,BUY,100,TO CLOSE,NVDA,,,STOCK,4.0,4.0,LMT\n"
    )
    upload_orders(client, token, csv_data)

    # 3. Get trades and assert
    response = client.get("/api/v1/trades", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK

    trades = response.json()
    assert len(trades) == 2

    # The service doesn't guarantee the order of trades, so we sort by entry timestamp
    trades.sort(key=lambda t: t["entry_timestamp"])

    # Assert Long Trade
    long_trade = trades[0]
    assert long_trade["symbol"] == "NVDA"
    assert long_trade["direction"] == "LONG"
    assert long_trade["status"] == "CLOSED"
    assert long_trade["volume"] == 100
    assert long_trade["avg_entry_price"] == 10.25
    assert long_trade["avg_exit_price"] == 12.75
    assert round(long_trade["pnl"], 2) == 250.0

    # Assert Short Trade
    short_trade = trades[1]
    assert short_trade["symbol"] == "NVDA"
    assert short_trade["direction"] == "SHORT"
    assert short_trade["status"] == "CLOSED"
    assert short_trade["volume"] == 100
    assert short_trade["avg_entry_price"] == 5.34
    assert short_trade["avg_exit_price"] == 4.0
    assert round(short_trade["pnl"], 2) == 134.0

def test_fully_closed_and_reopened_trade(client: TestClient, db_session: Session):
    # 1. Create a user and get a token
    email = "partial_reopen@example.com"
    password = "testpassword"
    token, user_id = get_user_token(client, email, password)

    # 2. Upload orders for the scenario
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-10-07 10:00:00,STOCK,BUY,10,TO OPEN,AAPL,,,STOCK,150.0,150.0,LMT\n"
        "2025-10-07 10:01:00,STOCK,BUY,10,TO OPEN,AAPL,,,STOCK,151.0,151.0,LMT\n"
        "2025-10-07 10:02:00,STOCK,BUY,10,TO OPEN,AAPL,,,STOCK,152.0,152.0,LMT\n"
        "2025-10-07 10:05:00,STOCK,SELL,15,TO CLOSE,AAPL,,,STOCK,155.0,155.0,LMT\n"
        "2025-10-07 10:06:00,STOCK,SELL,15,TO CLOSE,AAPL,,,STOCK,156.0,156.0,LMT\n"
        "2025-10-07 10:16:00,STOCK,BUY,5,TO OPEN,AAPL,,,STOCK,160.0,160.0,LMT\n"
        "2025-10-07 10:17:00,STOCK,BUY,5,TO OPEN,AAPL,,,STOCK,161.0,161.0,LMT\n"
        "2025-10-07 10:18:00,STOCK,BUY,5,TO OPEN,AAPL,,,STOCK,162.0,162.0,LMT\n"
        "2025-10-07 10:20:00,STOCK,SELL,15,TO CLOSE,AAPL,,,STOCK,165.0,165.0,LMT\n"
    )
    upload_orders(client, token, csv_data)

    # 3. Get trades and assert
    response = client.get("/api/v1/trades", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK

    trades = response.json()
    assert len(trades) == 2

    trades.sort(key=lambda t: t["entry_timestamp"])

    # Assert First Trade
    first_trade = trades[0]
    assert first_trade["symbol"] == "AAPL"
    assert first_trade["status"] == "CLOSED"
    assert first_trade["volume"] == 30
    assert first_trade["avg_entry_price"] == 151.0
    assert first_trade["avg_exit_price"] == 155.5
    assert round(first_trade["pnl"], 2) == 135.0

    # Assert Second Trade
    second_trade = trades[1]
    assert second_trade["symbol"] == "AAPL"
    assert second_trade["status"] == "CLOSED"
    assert second_trade["volume"] == 15
    assert second_trade["avg_entry_price"] == 161.0
    assert second_trade["avg_exit_price"] == 165.0
    assert round(second_trade["pnl"], 2) == 60.0


def test_real_complex_trade(client: TestClient, db_session: Session):
    # 1. Create a user and get a token
    email = "partial_reopen@example.com"
    password = "testpassword"
    token, user_id = get_user_token(client, email, password)

    # 2. Upload orders for the scenario
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        '8/9/2025 0:40:30,STOCK,BUY,1700,TO CLOSE,BTAI,,,STOCK,4.2,4.2,LMT\n'
        '8/9/2025 0:40:30,STOCK,BUY,1200,TO CLOSE,BTAI,,,STOCK,4.2,4.2,LMT\n'
        '8/9/2025 0:38:47,STOCK,BUY,100,TO CLOSE,BTAI,,,STOCK,4.2,4.2,LMT\n'
        '8/9/2025 0:32:22,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.435,4.435,LMT\n'
        '8/9/2025 0:30:01,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.25,4.25,LMT\n'
        '8/9/2025 0:30:12,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.37,4.37,LMT\n'
        '8/9/2025 0:29:40,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.1906,4.1906,LMT\n'
        '8/9/2025 0:29:31,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.12,4.12,LMT\n'
        '8/9/2025 0:29:13,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.08,4.08,LMT\n'
        '8/9/2025 0:27:05,STOCK,BUY,3100,TO CLOSE,BTAI,,,STOCK,3.98,3.98,LMT\n'
        '8/9/2025 0:22:53,STOCK,SELL,-250,TO OPEN,BTAI,,,STOCK,4.23,4.23,LMT\n'
        '8/9/2025 0:22:52,STOCK,SELL,-50,TO OPEN,BTAI,,,STOCK,4.23,4.23,LMT\n'
        '8/9/2025 0:16:05,STOCK,SELL,-300,TO OPEN,BTAI,,,STOCK,4.16,4.16,LMT\n'
        '8/9/2025 0:14:40,STOCK,SELL,-271,TO OPEN,BTAI,,,STOCK,4.13,4.13,LMT\n'
        '8/9/2025 0:14:40,STOCK,SELL,-229,TO OPEN,BTAI,,,STOCK,4.13,4.13,LMT\n'
        '8/8/2025 23:54:43,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.12,4.12,LMT\n'
        '8/8/2025 23:51:06,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.11,4.11,LMT\n'
        '8/8/2025 23:49:20,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,3.94,3.94,LMT\n'
        '8/8/2025 23:47:30,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.065,4.065,LMT\n'
        '8/8/2025 23:43:34,STOCK,BUY,3000,TO CLOSE,BTAI,,,STOCK,3.975,3.975,LMT\n'
        '8/8/2025 23:41:51,STOCK,SELL,-250,TO OPEN,BTAI,,,STOCK,4.37,4.37,LMT\n'
        '8/8/2025 23:41:51,STOCK,SELL,-250,TO OPEN,BTAI,,,STOCK,4.37,4.37,LMT\n'
        '8/8/2025 23:40:13,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.26,4.26,LMT\n'
        '8/8/2025 23:38:17,STOCK,SELL,-500,TO OPEN,BTAI,,,STOCK,4.1,4.1,LMT\n'
        '8/8/2025 23:37:47,STOCK,SELL,-430,TO OPEN,BTAI,,,STOCK,4,4,LMT\n'
        '8/8/2025 23:37:47,STOCK,SELL,-70,TO OPEN,BTAI,,,STOCK,4,4,LMT\n'
        '8/8/2025 23:36:45,STOCK,SELL,-1000,TO OPEN,BTAI,,,STOCK,3.96,3.96,LMT\n'
        '8/8/2025 23:35:32,STOCK,SELL,-1000,TO CLOSE,BTAI,,,STOCK,3.99,3.99,LMT\n'
        '8/8/2025 23:35:24,STOCK,BUY,1000,TO OPEN,BTAI,,,STOCK,4.01,4.01,LMT\n'
    )
    upload_orders(client, token, csv_data)

    # 3. Get trades and assert
    response = client.get("/api/v1/trades", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK

    trades = response.json()
    assert len(trades) == 4

    trades.sort(key=lambda t: t["entry_timestamp"])

    # Assert First Trade
    first_trade = trades[0]
    assert first_trade["symbol"] == "BTAI"
    assert first_trade["status"] == "CLOSED"
    assert first_trade["volume"] == 1000
    assert first_trade["avg_entry_price"] == 4.01
    assert first_trade["avg_exit_price"] == 3.99
    assert round(first_trade["pnl"], 2) == -20.0

    # Assert First Trade
    first_trade = trades[1]
    assert first_trade["symbol"] == "BTAI"
    assert first_trade["status"] == "CLOSED"
    assert first_trade["volume"] == 3000
    assert first_trade["avg_entry_price"] == 4.108333333333333
    assert first_trade["avg_exit_price"] == 3.975
    assert round(first_trade["pnl"], 2) == 400.0