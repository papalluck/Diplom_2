import pytest
import requests
import allure
from config import BASE_URL
@allure.suite("User Authentication")
class TestUserAuthentication:

    @allure.title("Login with existing user")
    def test_login_with_existing_user(self, create_user):
        url = f"{BASE_URL}/auth/login"
        payload = create_user["user_data"]
        response = requests.post(url, json=payload)

        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code} - {response.text}"
        data = response.json()
        assert data["success"] == True, f"Expected success to be True, but got {data.get('success')}"
        assert "accessToken" in data, "Response should contain accessToken"
        assert "refreshToken" in data, "Response should contain refreshToken"
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == payload["email"], "Email should match"
        assert data["user"]["name"] == payload["name"], "Name should match"

    @allure.title("Login with invalid credentials")
    def test_login_with_invalid_credentials(self, create_user):
        url = f"{BASE_URL}/auth/login"
        payload = {
            "email": create_user["user_data"]["email"],
            "password": "wrong_password"
        }
        response = requests.post(url, json=payload)

        assert response.status_code == 401, f"Expected status code 401, but got {response.status_code} - {response.text}"
        data = response.json()
        assert data["success"] == False, f"Expected success to be False, but got {data.get('success')}"
        assert data["message"] == "email or password are incorrect", "Expected message to be 'email or password are incorrect'"