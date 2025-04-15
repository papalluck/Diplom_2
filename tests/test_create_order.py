import pytest
import allure
import requests
from config import BASE_URL
from api_utils import make_api_request, logger
import random
from data.ingredients import VALID_INGREDIENTS


@allure.suite("Создание заказов")
class TestOrderCreation:
    @allure.title("Create order with authorization and ingredients")
    def test_create_order_with_auth_and_ingredients(self, create_and_delete_user, get_ingredients):
        url = f"{BASE_URL}/orders"
        access_token = create_and_delete_user["tokens"]["accessToken"]
        headers = {"Authorization": f"{access_token}", "Content-Type": "application/json"}

        logger.info(f"Заголовки для создания заказа: {headers}")

        selected_ingredient_ids = random.sample(get_ingredients, 2)

        payload = {"ingredients": selected_ingredient_ids}
        logger.info(f"Payload для создания заказа: {payload}")

        response = make_api_request("POST", url, headers=headers, json=payload)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        data = response.json()
        logger.info(f"Заказ успешно создан: {data}")
        assert data["success"] is True, "success должен быть True"
        assert "name" in data, "В ответе должно быть имя заказа"
        assert "order" in data, "В ответе должен быть информация о заказе"
        assert "number" in data["order"], "В ответе должен быть номер заказа"

    @allure.title("Create order without authorization")
    def test_create_order_without_auth(self):
        url = f"{BASE_URL}/orders"
        payload = {"ingredients": VALID_INGREDIENTS}
        logger.info(f"Payload для создания заказа без авторизации: {payload}")

        response = make_api_request("POST", url, json=payload)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "success должен быть True"
        assert "name" in data, "В ответе должно быть имя заказа"
        assert "order" in data, "В ответе должен быть информация о заказе"
        assert "number" in data["order"], "В ответе должен быть номер заказа"
        logger.info(f"Заказ успешно создан без авторизации: {data.get('name')}")

    @allure.title("Create order with authorization but without ingredients")
    def test_create_order_with_auth_but_without_ingredients(self, create_and_delete_user):
        url = f"{BASE_URL}/orders"
        access_token = create_and_delete_user["tokens"]["accessToken"]
        headers = {"Authorization": f"{access_token}", "Content-Type": "application/json"}
        payload = {"ingredients": []}
        logger.info(f"Payload для создания заказа с авторизацией, но без ингредиентов: {payload}")
        logger.info(f"Заголовки для создания заказа с авторизацией, но без ингредиентов: {headers}")

        response = make_api_request("POST", url, headers=headers, json=payload)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        data = response.json()
        assert data["success"] is False, "success должен быть False"
        assert "message" in data, "В ответе должно быть сообщение об ошибке"
        assert data["message"] == "Ingredient ids must be provided", "Сообщение об ошибке не соответствует ожидаемому"

    @allure.title("Create order with authorization and invalid ingredients")
    def test_create_order_with_auth_and_invalid_ingredients(self, create_and_delete_user):
        url = f"{BASE_URL}/orders"
        access_token = create_and_delete_user["tokens"]["accessToken"]
        headers = {"Authorization": f"{access_token}", "Content-Type": "application/json"}
        payload = {"ingredients": ["invalid_ingredient_id"]}
        logger.info(f"Payload для создания заказа с авторизацией и невалидными ингредиентами: {payload}")
        logger.info(f"Заголовки для создания заказа с авторизацией и невалидными ингредиентами: {headers}")

        response = make_api_request("POST", url, headers=headers, json=payload)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 500, f"Expected status code 500, but got {response.status_code}"

