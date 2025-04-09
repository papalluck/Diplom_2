import pytest
import requests
import allure
from config import BASE_URL, VALID_INGREDIENTS
import logging


logger = logging.getLogger(__name__)

@allure.suite("Создание заказа")
class TestOrderCreation:

    @allure.title("Создание заказа с авторизацией и ингредиентами")
    def test_create_order_with_auth_and_ingredients(self, create_user):
        url = f"{BASE_URL}/orders"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        payload = {"ingredients": VALID_INGREDIENTS}
        response = requests.post(url, headers=headers, json=payload)

        logger.info(f"Запрос к {url} с данными: {payload}, статус код: {response.status_code}, Ответ: {response.text}")
        response.raise_for_status()
        data = response.json()
        assert data["success"] == True, f"Ожидалось success == True, но получено {data.get('success')}"
        assert "name" in data, "В ответе должно быть имя заказа"
        assert "order" in data, "В ответе должен быть заказ"
        logger.info(f"Заказ успешно создан: {data.get('name')}")


    @allure.title("Создание заказа без авторизации")
    def test_create_order_without_auth(self):
        url = f"{BASE_URL}/orders"
        payload = {"ingredients": VALID_INGREDIENTS}
        response = requests.post(url, json=payload)

        logger.info(f"Запрос к {url} с данными: {payload}, статус код: {response.status_code}, Ответ: {response.text}")
        response.raise_for_status()
        data = response.json()
        assert data["success"] == True, f"Ожидалось success == True, но получено {data.get('success')}"
        assert "name" in data, "В ответе должно быть имя заказа"
        assert "order" in data, "В ответе должен быть заказ"
        logger.info(f"Заказ успешно создан без авторизации: {data.get('name')}")


    @allure.title("Создание заказа с авторизацией, но без ингредиентов")
    def test_create_order_with_auth_but_without_ingredients(self, create_user):
        url = f"{BASE_URL}/orders"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        payload = {"ingredients": []}
        response = requests.post(url, headers=headers, json=payload)

        logger.info(f"Запрос к {url} с данными: {payload}, статус код: {response.status_code}, Ответ: {response.text}")
        assert response.status_code == 400, f"Ожидался статус код 400, но получен {response.status_code} - {response.text}"
        data = response.json()
        assert data["success"] == False, f"Ожидалось success == False, но получено {data.get('success')}"
        assert data["message"] == "Ingredient ids must be provided", f"Ожидалось сообщение 'Ingredient ids must be provided', но получено {data.get('message')}"


    @allure.title("Создание заказа с авторизацией и невалидными ингредиентами")
    def test_create_order_with_auth_and_invalid_ingredients(self, create_user):
        url = f"{BASE_URL}/orders"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        payload = {"ingredients": ["invalid_ingredient_id"]}
        response = requests.post(url, headers=headers, json=payload)

        logger.info(f"Запрос к {url} с данными: {payload}, статус код: {response.status_code}, Ответ: {response.text}")
        assert response.status_code == 500, f"Ожидался статус код 500, но получен {response.status_code} - {response.text}"
