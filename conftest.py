import pytest
import requests
from faker import Faker
from config import BASE_URL  # Import BASE_URL
import json

fake = Faker()


@pytest.fixture(scope="function")
def unique_user_data():
    """
    Фикстура для генерации уникальных данных пользователя.
    """
    email = fake.email()
    password = fake.password()
    name = fake.name()
    user_data = {"email": email, "password": password, "name": name}
    return user_data


@pytest.fixture(scope="function")
def create_user(unique_user_data):
    """
    Фикстура для создания пользователя и возвращения его данных и токенов.
    """
    url = f"{BASE_URL}/auth/register"
    headers = {'Content-Type': 'application/json'}  # Add header
    payload = json.dumps(unique_user_data)  # Ensure JSON format
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        print(f"Failed to create user: {response.status_code} - {response.text}")
    assert response.status_code == 200
    data = response.json()
    access_token = data["accessToken"]
    refresh_token = data["refreshToken"]

    yield {"user_data": unique_user_data, "tokens": {"accessToken": access_token, "refreshToken": refresh_token}}

    # Delete user after tests
    delete_url = f"{BASE_URL}/auth/user"
    headers = {"Authorization": access_token}
    delete_response = requests.delete(delete_url, headers=headers)
    if delete_response.status_code == 202:
        print(f"User {unique_user_data['email']} deleted successfully")
    else:
        print(f"Failed to delete user {unique_user_data['email']}: {delete_response.status_code} - {delete_response.text}")