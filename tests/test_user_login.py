import pytest
import allure
import requests
from config import BASE_URL
from api_utils import make_api_request, logger
from data.response_messages import EMAIL_PASSWORD_INCORRECT_MESSAGE
from data.user_data import generate_unique_user_data

@allure.suite("User Authentication")
class TestUserAuthentication:

    @allure.title("Login with existing user")
    def test_login_with_existing_user(self, create_and_delete_user):
        url = f"{BASE_URL}/auth/login"
        payload = create_and_delete_user["user_data"]

        response = make_api_request("POST", url, json=payload)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

        data = response.json()
        assert "accessToken" in data, "Response should contain accessToken"
        assert "refreshToken" in data, "Response should contain refreshToken"
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == payload["email"], "Email should match"
        assert data["user"]["name"] == payload["name"], "Name should match"
        logger.info(f"Успешный вход пользователя {payload['email']}.")

    @allure.title("Login with invalid credentials")
    def test_login_with_invalid_credentials(self, fake):
        url = f"{BASE_URL}/auth/login"
        unique_user_data = generate_unique_user_data(fake)

        headers = {'Content-Type': 'application/json'}
        register_url = f"{BASE_URL}/auth/register"
        register_response = requests.post(register_url, headers=headers, json=unique_user_data, verify=False)
        assert register_response.status_code == 200, f"Не удалось зарегистрировать пользователя для теста: {register_response.text}"
        assert register_response.json()["success"] is True, "success должен быть True при регистрации пользователя для теста"


        payload = {
            "email": unique_user_data["email"],
            "password": "wrong_password"
        }

        response = make_api_request("POST", url, json=payload)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"


        data = response.json()
        logger.info(f"Сообщение об ошибке: {data.get('message')}")
        assert data["message"] == EMAIL_PASSWORD_INCORRECT_MESSAGE, f"Expected message to be '{EMAIL_PASSWORD_INCORRECT_MESSAGE}', but got '{data['message']}'"
        logger.info(f"Проверено, что вход с неверными учетными данными не удается.")