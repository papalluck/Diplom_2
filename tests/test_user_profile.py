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

        try:
            response = make_api_request("GET", url, headers=headers)
            if response is None:
                 pytest.fail("make_api_request вернул None")
            assert response.status_code == 200
            response.raise_for_status()

            data = response.json()
            assert "user" in data, "Response should contain user"
            assert data["user"]["email"] == create_and_delete_user["user_data"]["email"], "Email should match"
            assert data["user"]["name"] == create_and_delete_user["user_data"]["name"], "Name should match"
            logger.info(f"Успешно получен профиль пользователя {create_and_delete_user['user_data']['email']} (с авторизацией).")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении профиля пользователя {create_and_delete_user['user_data']['email']} (с авторизацией): {e}")
            pytest.fail(f"Не удалось получить профиль пользователя (с авторизацией): {e}")

    @allure.title("Get user profile without authorization")
    def test_get_user_profile_without_auth(self):
        url = f"{BASE_URL}/auth/user"

        try:
            response = make_api_request("GET", url)
            if response is None:
                 pytest.fail("make_api_request вернул None")
            assert response.status_code == 401

            data = response.json()
            logger.info(f"Сообщение об ошибке: {data.get('message')}")
            assert data["message"] == YOU_SHOULD_BE_AUTHORISED_MESSAGE, f"Expected message to be '{YOU_SHOULD_BE_AUTHORISED_MESSAGE}'"
            logger.info(f"Проверено, что для получения профиля пользователя требуется авторизация.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении профиля пользователя (без авторизации): {e}")
            pytest.fail(f"Не удалось получить профиль пользователя (без авторизации): {e}")

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
        try:
            response = make_api_request("PATCH", url, headers=headers, json=updated_data)
            if response is None:
                 pytest.fail("make_api_request вернул None")
            assert response.status_code == 200
            response.raise_for_status()

            data = response.json()
            assert "user" in data, "Response should contain user"
            assert data["user"]["email"] == updated_data["email"], "Email should be updated"
            assert data["user"]["name"] == updated_data["name"], "Name should be updated"
            logger.info(f"Профиль пользователя {create_and_delete_user['user_data']['email']} успешно обновлен.")

            create_and_delete_user["user_data"]["email"] = updated_data["email"]
            create_and_delete_user["user_data"]["name"] = updated_data["name"]

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при обновлении профиля пользователя {create_and_delete_user['user_data']['email']} (с авторизацией): {e}")
            pytest.fail(f"Не удалось обновить профиль пользователя (с авторизацией): {e}")

    @allure.title("Update user profile without authorization")
    def test_update_user_profile_without_auth(self, fake):
        url = f"{BASE_URL}/auth/user"
        headers = {'Content-Type': 'application/json'}
        updated_data = generate_unique_user_data(fake)

        try:
            response = make_api_request("PATCH", url, json=updated_data, headers=headers)
            if response is None:
                 pytest.fail("make_api_request вернул None")
            assert response.status_code == 401

            data = response.json()
            logger.info(f"Сообщение об ошибке: {data.get('message')}")
            assert data["message"] == YOU_SHOULD_BE_AUTHORISED_MESSAGE, f"Expected message to be '{YOU_SHOULD_BE_AUTHORISED_MESSAGE}'"
            logger.info(f"Проверено, что для обновления профиля пользователя требуется авторизация.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при попытке обновления профиля пользователя (без авторизации): {e}")
            pytest.fail(f"Не удалось обновить профиль пользователя (без авторизации): {e}")

    @allure.title("Update user profile with authorization and existing email")
    def test_update_user_profile_with_auth_and_existing_email(self, create_and_delete_user, fake):
        url = f"{BASE_URL}/auth/user"
        headers = {"Authorization": f"{create_and_delete_user["tokens"]["accessToken"]}", "Content-Type": "application/json"}
        second_user_data = generate_unique_user_data(fake)
        make_api_request("POST", f"{BASE_URL}/auth/register", headers={'Content-Type': 'application/json'}, json=second_user_data)

        updated_data = {
            "email": second_user_data["email"],
            "name": fake.name(),
            "password": create_and_delete_user["user_data"]["password"]
        }

        try:
            response = make_api_request("PATCH", url, headers=headers, json=updated_data)
            if response is None:
                 pytest.fail("make_api_request вернул None")
            assert response.status_code == 403

            data = response.json()
            logger.info(f"Сообщение об ошибке: {data.get('message')}")
            assert data["message"] == EMAIL_ALREADY_EXISTS_MESSAGE, f"Expected message to be '{EMAIL_ALREADY_EXISTS_MESSAGE}'"
            logger.info(f"Проверено, что нельзя обновить email на существующий.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при попытке обновления email на существующий: {e}")
            pytest.fail(f"Не удалось обновить email на существующий: {e}")