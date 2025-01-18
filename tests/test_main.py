import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestMain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_register_and_login(self):
        # 1) Ro'yxatdan o'tish
        reg_data = {
            "email": "test@example.com",
            "password": "secret",
            "first_name": "Test",
            "last_name": "User",
            "is_superuser": True,
        }
        response = self.client.post("/auth/register", json=reg_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

        # 2) login
        login_data = {"username": "test@example.com", "password": "secret"}
        response = self.client.post("/auth/login", data=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

        access_token = response.json()["access_token"]

        # 3) products create (superuser required)
        headers = {"Authorization": f"Bearer {access_token}"}
        prod_data = {
            "name": "Test Product",
            "description": "Test Desc",
            "price": 10.5,
            "is_active": True,
        }
        response = self.client.post("/products/", json=prod_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())


if __name__ == "__main__":
    unittest.main()
