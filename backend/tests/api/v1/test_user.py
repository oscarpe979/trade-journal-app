from fastapi.testclient import TestClient


def test_create_user(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_create_user_existing_email(client: TestClient):
    # First, create a user
    client.post(
        "/api/v1/users/",
        json={"email": "test1@example.com", "password": "testpassword"},
    )

    # Then, try to create another user with the same email
    response = client.post(
        "/api/v1/users/",
        json={"email": "test1@example.com", "password": "testpassword"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}
