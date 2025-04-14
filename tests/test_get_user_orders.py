import pytest
import allure
import requests
from config import BASE_URL
from api_utils import make_api_request, logger
from data.response_messages import YOU_SHOULD_BE_AUTHORISED_MESSAGE

@allure.suite("Get User Orders")
class TestGetUserOrders:

    @allure.title("Get user orders with authorization")
    def test_get_user_orders_with_auth(self, create_and_delete_user):
        url = f"{BASE_URL}/orders"
        access_token = create_and_delete_user["tokens"]["accessToken"]
        headers = {"Authorization": f"{access_token}"}

        try:
            response = make_api_request("GET", url, headers=headers)
            if response is None:
                pytest.fail("make_api_request вернул None")
            assert response.status_code == 200
            response.raise_for_status()
            data = response.json()
            assert "orders" in data, "Response should contain orders"
            assert isinstance(data["orders"], list), "Orders should be a list"
            logger.info(f"Успешно получены заказы пользователя (с авторизацией).")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении заказов пользователя (с авторизацией): {e}")
            pytest.fail(f"Не удалось получить заказы пользователя (с авторизацией): {e}")

    @allure.title("Get user orders without authorization")
    def test_get_user_orders_without_auth(self):
        url = f"{BASE_URL}/orders"

        try:
            response = make_api_request("GET", url)
            if response is None:
                pytest.fail("make_api_request вернул None")
            assert response.status_code == 401
            data = response.json()
            logger.info(f"Сообщение об ошибке: {data.get('message')}")
            assert data["message"] == YOU_SHOULD_BE_AUTHORISED_MESSAGE, f"Expected message to be '{YOU_SHOULD_BE_AUTHORISED_MESSAGE}'"

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении заказов пользователя (без авторизации): {e}")
            pytest.fail(f"Не удалось получить заказы пользователя (без авторизации): {e}")