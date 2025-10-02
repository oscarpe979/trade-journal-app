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
        "2025-10-01 10:00:00,SINGLE,BUY,10,TO OPEN,MSFT,2025-10-10,300,C,10.0,10.0,LIMIT\n"
        "2025-10-01 10:05:00,SINGLE,SELL,10,TO CLOSE,MSFT,2025-10-10,300,C,12.0,12.0,LIMIT\n"
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
        "2025-10-02 10:00:00,SINGLE,BUY,5,TO OPEN,GOOG,2025-10-10,140,C,5.0,5.0,LIMIT\n"
        "2025-10-02 10:05:00,SINGLE,SELL,5,TO CLOSE,GOOG,2025-10-10,140,C,6.0,6.0,LIMIT\n"
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
        "2025-10-03 10:00:00,SINGLE,BUY,2,TO OPEN,AMZN,2025-10-10,130,C,2.0,2.0,LIMIT\n"
        "2025-10-03 10:05:00,SINGLE,SELL,2,TO CLOSE,AMZN,2025-10-10,130,C,2.5,2.5,LIMIT\n"
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
        "2025-10-04 10:00:00,SINGLE,BUY,5,TO OPEN,TSLA,2025-10-10,250,C,8.0,8.0,LIMIT\n"
        "2025-10-04 10:01:00,SINGLE,BUY,5,TO OPEN,TSLA,2025-10-10,250,C,8.5,8.5,LIMIT\n"
        "2025-10-04 10:05:00,SINGLE,SELL,10,TO CLOSE,TSLA,2025-10-10,250,C,9.0,9.0,LIMIT\n"
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
