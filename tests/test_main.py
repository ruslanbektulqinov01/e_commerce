import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import random
import string

from app.main import app

client = TestClient(app)


def generate_random_email():
    return (
        "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        + "@example.com"
    )


def generate_random_product_name():
    return "".join(random.choices(string.ascii_lowercase, k=10)).capitalize()


@pytest.fixture
def test_product_data():
    return {
        "name": generate_random_product_name(),
        "description": "A product created during testing.",
        "price": 49.99,
        "quantity": 10,
        "is_active": True,
    }


@pytest_asyncio.fixture
async def auth_token():
    email = generate_random_email()
    TEST_USER = {
        "email": email,
        "password": "string",
        "first_name": "John",
        "last_name": "Doe",
        "is_superuser": True,
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        register_response = await ac.post("/auth/register", json=TEST_USER)
        assert (
            register_response.status_code == 200
        ), f"Registration failed with status {register_response.status_code}"
        register_data = register_response.json()
        assert (
            "access_token" in register_data
        ), "Registration failed, no access token in response"

        token = register_data["access_token"]
        verify_response = await ac.get(f"/auth/verify-email?token={token}")
        assert (
            verify_response.status_code == 200
        ), f"Email verification failed with status {verify_response.status_code}"

        login_data = {"username": TEST_USER["email"], "password": TEST_USER["password"]}

        login_response = await ac.post("/auth/login", data=login_data)
        assert (
            login_response.status_code == 200
        ), f"Login failed with status {login_response.status_code}"

        login_response_data = login_response.json()
        assert (
            "access_token" in login_response_data
        ), "No access token in login response"
        assert "token_type" in login_response_data, "No token type in login response"
        assert (
            login_response_data["token_type"] == "bearer"
        ), "Incorrect token type in login response"

        return login_response_data["access_token"]


@pytest_asyncio.fixture
async def test_product(auth_token, test_product_data):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = await ac.post("/products/", headers=headers, json=test_product_data)
        assert (
            response.status_code == 200
        ), f"Product creation failed with status {response.status_code}"

        data = response.json()
        assert "id" in data, "Product creation response missing 'id'"
        return data["id"]


def test_create_order_without_auth():
    response = client.get("/orders")
    assert (
        response.status_code == 401
    ), f"Expected status code 401, got {response.status_code}"
    assert (
        response.json()["detail"] == "Not authenticated"
    ), "Expected 'Not authenticated' detail message"


def test_create_product_without_auth(test_product_data):
    response = client.post("/products", json=test_product_data)
    assert (
        response.status_code == 401
    ), f"Expected status code 401, got {response.status_code}"
    assert (
        response.json()["detail"] == "Not authenticated"
    ), "Expected 'Not authenticated' detail message"


@pytest.mark.asyncio
async def test_create_product_with_auth(auth_token, test_product_data):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = await ac.post("/products/", headers=headers, json=test_product_data)
        print("Create Product Response:", response.json())  # Debug uchun

        assert (
            response.status_code == 200
        ), f"Product creation failed with status {response.status_code}"

        data = response.json()
        assert data["name"] == test_product_data["name"], "Product name mismatch"
        assert data["price"] == test_product_data["price"], "Product price mismatch"
        assert "id" in data, "Product creation response missing 'id'"
