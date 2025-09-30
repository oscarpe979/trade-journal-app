from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from app.crud import trade as trade_crud
from tests.api.v1.test_user import get_user_token


def test_upload_trades_csv_success(client: TestClient, db_session: Session):
    # 1. Create a user and get a token
    email = "trade_tester@example.com"
    password = "testpassword"
    token, user_id = get_user_token(client, email, password)

    # 2. Prepare the CSV data
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-09-30 10:00:00,SINGLE,BUY,1,TO OPEN,AAPL,2025-10-10,150,C,10.5,10.5,LIMIT\n"
        "2025-09-30 10:05:00,SINGLE,SELL,1,TO CLOSE,AAPL,2025-10-10,150,C,11.0,11.0,LIMIT\n"
    )

    # 3. Upload the CSV file
    response = client.post(
        "/api/v1/trades/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("trades.csv", csv_data, "text/csv")},
    )

    # 4. Assert the response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "2 trades have been successfully uploaded."}

    # 5. Verify trades in the database
    user_trades = trade_crud.get_trades_by_user(db=db_session, user_id=user_id)
    assert len(user_trades) == 2
    assert user_trades[0].symbol == "AAPL"
    assert user_trades[0].quantity == 1
    assert user_trades[1].price == 11.0

def test_upload_trades_csv_invalid_file_type(client: TestClient):
    # 1. Create a user and get a token
    email = "invalid_file@example.com"
    password = "testpassword"
    token, _ = get_user_token(client, email, password)

    # 2. Prepare a non-CSV file
    invalid_file_data = "this is not a csv"

    # 3. Upload the file
    response = client.post(
        "/api/v1/trades/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("trades.txt", invalid_file_data, "text/plain")},
    )

    # 4. Assert the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid file type. Please upload a CSV file."}


def test_upload_trades_csv_invalid_columns(client: TestClient):
    # 1. Create a user and get a token
    email = "invalid_columns@example.com"
    password = "testpassword"
    token, _ = get_user_token(client, email, password)

    # 2. Prepare CSV data with invalid columns
    csv_data = (
        "Wrong Column 1,Wrong Column 2\n"
        "val1,val2\n"
    )

    # 3. Upload the CSV file
    response = client.post(
        "/api/v1/trades/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("trades.csv", csv_data, "text/csv")},
    )

    # 4. Assert the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid CSV format" in response.json()["detail"]


def test_upload_trades_csv_unauthenticated(client: TestClient):
    # 2. Prepare the CSV data
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-09-30 10:00:00,SINGLE,BUY,1,TO OPEN,AAPL,2025-10-10,150,C,10.5,10.5,LIMIT\n"
    )

    # 3. Upload the CSV file without authentication
    response = client.post(
        "/api/v1/trades/upload",
        files={"file": ("trades.csv", csv_data, "text/csv")},
    )

    # 4. Assert the response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}
