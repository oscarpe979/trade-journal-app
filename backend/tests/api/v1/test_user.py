from fastapi.testclient import TestClient
from starlette import status

# Helper function to create a user and get their token
def get_user_token(client: TestClient, email: str, password: str) -> str:
    # Create user
    client.post(
        "/api/v1/users/",
        json={"email": email, "password": password},
    )
    # Login and get token
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": password},
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]

# I. User Registration Tests
def test_create_user(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password_hash" not in data # Ensure password hash is not returned

def test_create_user_existing_email(client: TestClient):
    # First, create a user
    client.post(
        "/api/v1/users/",
        json={"email": "existing@example.com", "password": "testpassword"},
    )

    # Then, try to create another user with the same email
    response = client.post(
        "/api/v1/users/",
        json={"email": "existing@example.com", "password": "testpassword"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Email already registered"}

def test_create_user_invalid_email(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={"email": "invalid-email", "password": "testpassword"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY # Pydantic validation error

def test_create_user_missing_email(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={"password": "testpassword"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_user_missing_password(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={"email": "missingpass@example.com"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# II. User Login/Authentication Tests
def test_login_for_access_token_success(client: TestClient):
    email = "login_success@example.com"
    password = "loginpassword"
    get_user_token(client, email, password) # Create user and get token

def test_login_for_access_token_wrong_password(client: TestClient):
    email = "wrong_pass@example.com"
    password = "correctpassword"
    get_user_token(client, email, password) # Create user

    response = client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}

def test_login_for_access_token_non_existent_user(client: TestClient):
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "nonexistent@example.com", "password": "anypassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}

def test_login_for_access_token_missing_username(client: TestClient):
    response = client.post(
        "/api/v1/login/access-token",
        data={"password": "anypassword"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_for_access_token_missing_password(client: TestClient):
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_for_access_token_invalid_form_data(client: TestClient):
    # Login endpoint expects form data, not JSON
    response = client.post(
        "/api/v1/login/access-token",
        json={"username": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY # FastAPI expects form data

# III. Protected Routes Tests
def test_read_users_me_success(client: TestClient):
    email = "me_success@example.com"
    password = "mepassword"
    token = get_user_token(client, email, password)

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == email
    assert "id" in data

def test_read_users_me_no_token(client: TestClient):
    response = client.get(
        "/api/v1/users/me",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}

def test_read_users_me_invalid_token(client: TestClient):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
