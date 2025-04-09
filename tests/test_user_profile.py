import pytest
import requests
import allure
from config import BASE_URL
import logging

logger = logging.getLogger(__name__)

@allure.suite("Управление профилем пользователя")
class TestUserProfileManagement:

    @allure.title("Получение информации о пользователе с авторизацией")
    def test_get_user_info_with_auth(self, create_user):
        url = f"{BASE_URL}/auth/user"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        response = requests.get(url, headers=headers)

        logger.info(f"Запрос к {url}, статус код: {response.status_code}, Ответ: {response.text}")
        response.raise_for_status()
        data = response.json()
        assert data["success"] == True, f"Ожидалось success == True, но получено {data.get('success')}"
        assert "user" in data, "В ответе должен быть ключ 'user'"
        assert data["user"]["email"] == create_user["user_data"]["email"], "Email должен совпадать"
        assert data["user"]["name"] == create_user["user_data"]["name"], "Имя должно совпадать"

    @allure.title("Получение информации о пользователе без авторизации")
    def test_get_user_info_without_auth(self, create_user):
        url = f"{BASE_URL}/auth/user"
        response = requests.get(url)

        logger.info(f"Запрос к {url}, статус код: {response.status_code}, Ответ: {response.text}")
        assert response.status_code == 401, f"Ожидался статус код 401, но получен {response.status_code} - {response.text}"
        data = response.json()
        assert data["success"] == False, f"Ожидалось success == False, но получено {data.get('success')}"
        assert data["message"] == "You should be authorised", f"Ожидалось сообщение 'You should be authorised', но получено {data.get('message')}"

    @allure.title("Обновление информации о пользователе с авторизацией")
    def test_update_user_info_with_auth(self, create_user, fake):
        url = f"{BASE_URL}/auth/user"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        new_name = fake.name()
        payload = {"name": new_name}
        response = requests.patch(url, headers=headers, json=payload)

        logger.info(f"Запрос к {url} с данными: {payload}, статус код: {response.status_code}, Ответ: {response.text}")
        response.raise_for_status()
        data = response.json()
        assert data["success"] == True, f"Ожидалось success == True, но получено {data.get('success')}"
        assert "user" in data, "В ответе должен быть ключ 'user'"
        assert data["user"]["name"] == new_name, f"Имя должно быть обновлено до '{new_name}', но получено '{data['user'].get('name')}'"

    @allure.title("Обновление информации о пользователе без авторизации")
    def test_update_user_info_without_auth(self, create_user, fake):
        url = f"{BASE_URL}/auth/user"
        new_name = fake.name()
        payload = {"name": new_name}
        response = requests.patch(url, json=payload)

        logger.info(f"Запрос к {url}, статус код: {response.status_code}, Ответ: {response.text}")
        assert response.status_code == 401, f"Ожидался статус код 401, но получен {response.status_code} - {response.text}"
        data = response.json()
        assert data["success"] == False, f"Ожидалось success == False, но получено {data.get('success')}"
        assert data["message"] == "You should be authorised", f"Ожидалось сообщение 'You should be authorised', но получено {data.get('message')}"

    @allure.title("Попытка обновления email пользователя на существующий email")
    def test_update_user_email_with_existing_email_attempt_succeeds(self, create_user, fake):
        new_email = fake.email()
        url2 = f"{BASE_URL}/auth/register"
        payload2 = {"email": new_email, "password": fake.password(), "name": fake.name()}
        response2 = requests.post(url2, json=payload2)

        logger.info(f"Запрос к {url2}, статус код: {response2.status_code}, Ответ: {response2.text}")
        response2.raise_for_status()
        data2 = response2.json()
        second_user_token = data2["accessToken"]

        url = f"{BASE_URL}/auth/user"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        payload = {"email": new_email}
        response = requests.patch(url, headers=headers, json=payload)

        logger.info(f"Запрос к {url} с данными: {payload}, статус код: {response.status_code}, Ответ: {response.text}")
        assert response.status_code == 403, f"Ожидался статус код 403, но получен {response.status_code} - {response.text}"
        data = response.json()
        assert data["success"] == False, f"Ожидалось success == False, но получено {data.get('success')}"
        assert data["message"] == "User with such email already exists", f"Ожидалось сообщение 'User with such email already exists', но получено {data.get('message')}"

        delete_url = f"{BASE_URL}/auth/user"
        headers2 = {"Authorization": second_user_token}
        delete_response = requests.delete(delete_url, headers=headers2)

        logger.info(f"Запрос к {delete_url}, статус код: {delete_response.status_code}, Ответ: {delete_response.text}")
        delete_response.raise_for_status()