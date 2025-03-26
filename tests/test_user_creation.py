import pytest
import requests
import allure
from config import BASE_URL
from faker import Faker
import json


@allure.suite("User Creation")
class TestUserCreation:

    @allure.title("Create unique user")
    def test_create_unique_user(self, unique_user_data):
        url = f"{BASE_URL}/auth/register"
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps(unique_user_data)
        response = requests.post(url, headers=headers, data=payload)

        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        data = response.json()
        assert data["success"] == True, "Expected success to be True"
        assert "accessToken" in data, "Response should contain accessToken"
        assert "refreshToken" in data, "Response should contain refreshToken"
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == unique_user_data["email"], "Email should match"
        assert data["user"]["name"] == unique_user_data["name"], "Name should match"


    @allure.title("Create user that is already registered")
    def test_create_existing_user(self, unique_user_data):
        url = f"{BASE_URL}/auth/register"
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps(unique_user_data)
        requests.post(url,headers=headers, data=payload)

        response = requests.post(url, json=unique_user_data)
        assert response.status_code == 403, f"Expected status code 403, but got {response.status_code}"
        data = response.json()
        assert data["success"] == False, "Expected success to be False"
        assert data["message"] == "User already exists", "Expected message to be 'User already exists'"

    @allure.title("Create user without required field")
    @pytest.mark.parametrize("missing_field", ["email", "password", "name"])
    def test_create_user_without_required_field(self, missing_field, unique_user_data):
        url = f"{BASE_URL}/auth/register"
        payload = unique_user_data.copy()
        del payload[missing_field]

        response = requests.post(url, json=payload)
        assert response.status_code == 403, f"Expected status code 403, but got {response.status_code}"
        data = response.json()
        assert data["success"] == False, "Expected success to be False"
        assert data["message"] == "Email, password and name are required fields", "Expected message to be 'Email, password and name are required fields'"