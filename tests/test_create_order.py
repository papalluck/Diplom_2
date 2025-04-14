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

        if len(get_ingredients) < 2:
            pytest.skip("Недостаточно ингредиентов для создания заказа.")


        selected_ingredient_ids = random.sample(get_ingredients, 2)


        payload = {"ingredients": selected_ingredient_ids}
        logger.info(f"Payload для создания заказа: {payload}")

        try:
            response = make_api_request("POST", url, headers=headers, json=payload)

            if response is None:
                pytest.fail("make_api_request вернул None")

            assert response.status_code == 200
            response.raise_for_status()
            data = response.json()
            logger.info(f"Заказ успешно создан: {data}")
            assert "name" in data, "В ответе должно быть имя заказа"
            assert "order" in data, "В ответе должен быть заказ"


        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при создании заказа: {e}")
            pytest.fail(f"Не удалось создать заказ: {e}")

    @allure.title("Create order without authorization")
    def test_create_order_without_auth(self):
        url = f"{BASE_URL}/orders"
        payload = {"ingredients": VALID_INGREDIENTS}
        logger.info(f"Payload для создания заказа без авторизации: {payload}")
        try:
            response = make_api_request("POST", url, json=payload)
            if response is None:
                pytest.fail("make_api_request вернул None")
            assert response.status_code == 200
            response.raise_for_status()
            data = response.json()
            assert "name" in data, "В ответе должно быть имя заказа"
            assert "order" in data, "В ответе должен быть заказ"
            logger.info(f"Заказ успешно создан без авторизации: {data.get('name')}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при создании заказа без авторизации: {e}")
            pytest.fail(f"Не удалось создать заказ без авторизации: {e}")

    @allure.title("Create order with authorization but without ingredients")
    def test_create_order_with_auth_but_without_ingredients(self, create_and_delete_user):
        url = f"{BASE_URL}/orders"
        access_token = create_and_delete_user["tokens"]["accessToken"]
        headers = {"Authorization": f"{access_token}", "Content-Type": "application/json"}
        payload = {"ingredients": []}
        logger.info(f"Payload для создания заказа с авторизацией, но без ингредиентов: {payload}")
        logger.info(f"Заголовки для создания заказа с авторизацией, но без ингредиентов: {headers}")

        try:
            response = make_api_request("POST", url, headers=headers, json=payload)
            if response is None:
                pytest.fail("make_api_request вернул None")
            assert response.status_code == 400

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при создании заказа с авторизацией, но без ингредиентов: {e}")
            pytest.fail(f"Не удалось создать заказ с авторизацией, но без ингредиентов: {e}")

    @allure.title("Create order with authorization and invalid ingredients")
    def test_create_order_with_auth_and_invalid_ingredients(self, create_and_delete_user):
        url = f"{BASE_URL}/orders"
        access_token = create_and_delete_user["tokens"]["accessToken"]
        headers = {"Authorization": f"{access_token}", "Content-Type": "application/json"}
        payload = {"ingredients": ["invalid_ingredient_id"]}
        logger.info(f"Payload для создания заказа с авторизацией и невалидными ингредиентами: {payload}")
        logger.info(f"Заголовки для создания заказа с авторизацией и невалидными ингредиентами: {headers}")

        try:
            response = make_api_request("POST", url, headers=headers, json=payload)
            if response is None:
                pytest.fail("make_api_request вернул None")
            assert response.status_code == 500


        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при создании заказа с авторизацией и невалидными ингредиентами: {e}")
            pytest.fail(f"Не удалось создать заказ с авторизацией и невалидными ингредиентами: {e}")
