import pytest
import allure
import requests
from config import BASE_URL
from api_utils import make_api_request, logger
from data.user_data import generate_unique_user_data
from data.response_messages import USER_ALREADY_EXISTS_MESSAGE, EMAIL_PASSWORD_AND_NAME_ARE_REQUIRED_FIELDS



@allure.suite("User Creation")
class TestUserCreation:

    @pytest.fixture(scope="function")
    def unique_user_data(self, fake):
        return generate_unique_user_data(fake)

    @allure.title("Create unique user")
    def test_create_unique_user(self, unique_user_data):
        url = f"{BASE_URL}/auth/register"
        headers = {'Content-Type': 'application/json'}

        try:
            response = make_api_request("POST", url, headers=headers, json=unique_user_data)
            assert response.status_code == 200
            response.raise_for_status()
            data = response.json()
            assert "accessToken" in data, "Response should contain accessToken"
            assert "refreshToken" in data, "Response should contain refreshToken"
            assert "user" in data, "Response should contain user"
            assert data["user"]["email"] == unique_user_data["email"], "Email should match"
            assert data["user"]["name"] == unique_user_data["name"], "Name should match"
            logger.info(f"Пользователь {unique_user_data['email']} успешно зарегистрирован.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при создании уникального пользователя: {e}")
            pytest.fail(f"Не удалось создать уникального пользователя: {e}")


    @allure.title("Create user that is already registered")
    def test_create_existing_user(self, unique_user_data):
        url = f"{BASE_URL}/auth/register"
        headers = {'Content-Type': 'application/json'}

        try:
            response1 = make_api_request("POST", url, headers=headers, json=unique_user_data)
            response1.raise_for_status()

            response = make_api_request("POST", url, headers=headers, json=unique_user_data)
            assert response.status_code == 403
            data = response.json()
            logger.info(f"Сообщение об ошибке: {data.get('message')}")
            assert data["message"] == USER_ALREADY_EXISTS_MESSAGE, f"Expected message to be '{USER_ALREADY_EXISTS_MESSAGE}'"
            logger.info(f"Проверено, что нельзя зарегистрировать пользователя {unique_user_data['email']} повторно.")


        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при попытке создать существующего пользователя: {e}")
            pytest.fail(f"Не удалось создать существующего пользователя: {e}")


    @allure.title("Create user without required field")
    @pytest.mark.parametrize("missing_field", ["email", "password", "name"])
    def test_create_user_without_required_field(self, missing_field, unique_user_data):
        url = f"{BASE_URL}/auth/register"
        payload = unique_user_data.copy()
        del payload[missing_field]

        try:
            response = make_api_request("POST", url, json=payload)
            assert response.status_code == 403
            data = response.json()
            logger.info(f"Сообщение об ошибке: {data.get('message')}")
            assert data["message"] == EMAIL_PASSWORD_AND_NAME_ARE_REQUIRED_FIELDS, f"Expected message to be '{EMAIL_PASSWORD_AND_NAME_ARE_REQUIRED_FIELDS}'"
            logger.info(f"Проверено, что нельзя создать пользователя без поля {missing_field}.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при попытке создать пользователя без обязательного поля {missing_field}: {e}")
            pytest.fail(f"Не удалось создать пользователя без обязательного поля {missing_field}: {e}")