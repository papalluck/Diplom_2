import pytest
import allure
import requests
from config import BASE_URL
from api_utils import make_api_request, logger
from data.user_data import generate_unique_user_data
from data.response_messages import YOU_SHOULD_BE_AUTHORISED_MESSAGE, EMAIL_ALREADY_EXISTS_MESSAGE

@allure.suite("User Profile Management")
class TestUserProfile:

    @allure.title("Get user profile with authorization")
    def test_get_user_profile_with_auth(self, create_and_delete_user):
        url = f"{BASE_URL}/auth/user"
        headers = {"Authorization": f"{create_and_delete_user["tokens"]["accessToken"]}"}

        response = make_api_request("GET", url, headers=headers)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

        data = response.json()
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == create_and_delete_user["user_data"]["email"], "Email should match"
        assert data["user"]["name"] == create_and_delete_user["user_data"]["name"], "Name should match"
        logger.info(f"Успешно получен профиль пользователя {create_and_delete_user['user_data']['email']} (с авторизацией).")

    @allure.title("Get user profile without authorization")
    def test_get_user_profile_without_auth(self):
        url = f"{BASE_URL}/auth/user"

        response = make_api_request("GET", url)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"

        data = response.json()
        logger.info(f"Сообщение об ошибке: {data.get('message')}")
        assert data["message"] == YOU_SHOULD_BE_AUTHORISED_MESSAGE, f"Expected message to be '{YOU_SHOULD_BE_AUTHORISED_MESSAGE}', got '{data['message']}'"
        logger.info(f"Проверено, что для получения профиля пользователя требуется авторизация.")

    @allure.title("Update user profile with authorization")
    def test_update_user_profile_with_auth(self, create_and_delete_user, fake):
        url = f"{BASE_URL}/auth/user"
        headers = {"Authorization": f"{create_and_delete_user["tokens"]["accessToken"]}", "Content-Type": "application/json"}
        updated_data = {
            "email": generate_unique_user_data(fake)["email"],
            "name": fake.name(),
            "password": create_and_delete_user["user_data"]["password"]
        }
        logger.info(f"Новые данные пользователя: {updated_data}")

        response = make_api_request("PATCH", url, headers=headers, json=updated_data)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

        data = response.json()
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == updated_data["email"], "Email should be updated"
        assert data["user"]["name"] == updated_data["name"], "Name should be updated"
        logger.info(f"Профиль пользователя {create_and_delete_user['user_data']['email']} успешно обновлен.")

        create_and_delete_user["user_data"]["email"] = updated_data["email"]
        create_and_delete_user["user_data"]["name"] = updated_data["name"]

    @allure.title("Update user profile without authorization")
    def test_update_user_profile_without_auth(self, fake):
        url = f"{BASE_URL}/auth/user"
        headers = {'Content-Type': 'application/json'}
        updated_data = generate_unique_user_data(fake)

        response = make_api_request("PATCH", url, json=updated_data, headers=headers)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"

        data = response.json()
        logger.info(f"Сообщение об ошибке: {data.get('message')}")
        assert data["message"] == YOU_SHOULD_BE_AUTHORISED_MESSAGE, f"Expected message to be '{YOU_SHOULD_BE_AUTHORISED_MESSAGE}', got '{data['message']}'"
        logger.info(f"Проверено, что для обновления профиля пользователя требуется авторизация.")

    @allure.title("Update user profile with authorization and existing email")
    def test_update_user_profile_with_auth_and_existing_email(self, create_and_delete_user, fake):
        url = f"{BASE_URL}/auth/user"
        headers = {"Authorization": f"{create_and_delete_user["tokens"]["accessToken"]}", "Content-Type": "application/json"}
        second_user_data = generate_unique_user_data(fake)
        register_response = make_api_request("POST", f"{BASE_URL}/auth/register", headers={'Content-Type': 'application/json'}, json=second_user_data)
        assert register_response is not None, "make_api_request вернул None"
        assert register_response.status_code == 200, "Ожидался статус код 200 при регистрации второго пользователя"
        assert register_response.json()["success"] is True, "success должен быть True при регистрации второго пользователя"

        updated_data = {
            "email": second_user_data["email"],
            "name": fake.name(),
            "password": create_and_delete_user["user_data"]["password"]
        }

        response = make_api_request("PATCH", url, headers=headers, json=updated_data)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 403, f"Expected status code 403, got {response.status_code}"

        data = response.json()
        logger.info(f"Сообщение об ошибке: {data.get('message')}")
        assert data["message"] == EMAIL_ALREADY_EXISTS_MESSAGE, f"Expected message to be '{EMAIL_ALREADY_EXISTS_MESSAGE}', got '{data['message']}'"
        logger.info(f"Проверено, что нельзя обновить email на существующий.")