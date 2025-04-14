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

        try:
            response = make_api_request("POST", url, json=payload)
            if response is None:
                pytest.fail("make_api_request вернул None")
            assert response.status_code == 200
            response.raise_for_status()

            data = response.json()
            assert "accessToken" in data, "Response should contain accessToken"
            assert "refreshToken" in data, "Response should contain refreshToken"
            assert "user" in data, "Response should contain user"
            assert data["user"]["email"] == payload["email"], "Email should match"
            assert data["user"]["name"] == payload["name"], "Name should match"
            logger.info(f"Успешный вход пользователя {payload['email']}.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при входе пользователя {payload['email']}: {e}")
            pytest.fail(f"Не удалось войти пользователю: {e}")

    @allure.title("Login with invalid credentials")
    def test_login_with_invalid_credentials(self, fake):
        url = f"{BASE_URL}/auth/login"
        unique_user_data = generate_unique_user_data(fake)

        headers = {'Content-Type': 'application/json'}
        register_url = f"{BASE_URL}/auth/register"
        register_response = requests.post(register_url, headers=headers, json=unique_user_data, verify=False)

        if register_response.status_code != 200:
            pytest.fail(f"Не удалось зарегистрировать пользователя для теста: {register_response.text}")


        payload = {
            "email": unique_user_data["email"],
            "password": "wrong_password"
        }

        try:
            response = make_api_request("POST", url, json=payload)
            if response is None:
                pytest.fail("make_api_request вернул None")
            assert response.status_code == 401


            data = response.json()
            logger.info(f"Сообщение об ошибке: {data.get('message')}")
            assert data["message"] == EMAIL_PASSWORD_INCORRECT_MESSAGE, f"Expected message to be '{EMAIL_PASSWORD_INCORRECT_MESSAGE}'"
            logger.info(f"Проверено, что вход с неверными учетными данными не удается.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при попытке входа с неверными учетными данными: {e}")
            pytest.fail(f"Не удалось войти с неверными учетными данными: {e}")