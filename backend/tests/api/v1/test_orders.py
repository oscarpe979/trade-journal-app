from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from app.crud import order as order_crud
from tests.api.v1.test_user import get_user_token


def test_upload_orders_csv_success(client: TestClient, db_session: Session):
    # 1. Create a user and get a token
    email = "order_tester@example.com"
    password = "testpassword"
    token, user_id = get_user_token(client, email, password)

    # 2. Prepare the CSV data
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-09-30 10:00:00,STOCK,BUY,1,TO OPEN,AAPL,,,STOCK,10.5,10.5,LMT\n"
        "2025-09-30 10:05:00,STOCK,SELL,1,TO CLOSE,AAPL,,,STOCK,11.0,11.0,LMT\n"
    )

    # 3. Upload the CSV file
    response = client.post(
        "/api/v1/orders/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("orders.csv", csv_data, "text/csv")},
    )

    # 4. Assert the response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "2 orders have been successfully uploaded and processed."}

    # 5. Verify orders in the database
    user_orders = order_crud.get_orders_by_user(db=db_session, user_id=user_id)
    assert len(user_orders) == 2
    assert user_orders[0].symbol == "AAPL"
    assert user_orders[0].quantity == 1
    assert user_orders[1].price == 11.0

def test_upload_orders_csv_invalid_file_type(client: TestClient):
    # 1. Create a user and get a token
    email = "invalid_file@example.com"
    password = "testpassword"
    token, _ = get_user_token(client, email, password)

    # 2. Prepare a non-CSV file
    invalid_file_data = "this is not a csv"

    # 3. Upload the file
    response = client.post(
        "/api/v1/orders/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("orders.txt", invalid_file_data, "text/plain")},
    )

    # 4. Assert the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid file type. Please upload a CSV or XLSX file."}


def test_upload_orders_csv_invalid_columns(client: TestClient):
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
        "/api/v1/orders/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("orders.csv", csv_data, "text/csv")},
    )

    # 4. Assert the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid CSV format" in response.json()["detail"]


def test_upload_orders_csv_unauthenticated(client: TestClient):
    # 2. Prepare the CSV data
    csv_data = (
        "Exec Time,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,Price,Net Price,Order Type\n"
        "2025-09-30 10:00:00,SINGLE,BUY,1,TO OPEN,AAPL,2025-10-10,150,C,10.5,10.5,LIMIT\n"
    )

    # 3. Upload the CSV file without authentication
    response = client.post(
        "/api/v1/orders/upload",
        files={"file": ("orders.csv", csv_data, "text/csv")},
    )

    # 4. Assert the response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}
