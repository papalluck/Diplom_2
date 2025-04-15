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

        response = make_api_request("GET", url, headers=headers)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "success должен быть True"
        assert "orders" in data, "Response should contain orders"
        assert isinstance(data["orders"], list), "Orders should be a list"
        assert "total" in data, "Response should contain total"
        assert "totalToday" in data, "Response should contain totalToday"
        logger.info(f"Успешно получены заказы пользователя (с авторизацией).")

    @allure.title("Get user orders without authorization")
    def test_get_user_orders_without_auth(self):
        url = f"{BASE_URL}/orders"

        response = make_api_request("GET", url)
        assert response is not None, "make_api_request вернул None"
        assert response.status_code == 401, f"Expected status code 401, but got {response.status_code}"
        data = response.json()
        logger.info(f"Сообщение об ошибке: {data.get('message')}")
        assert data["success"] is False, "success должен быть False"
        assert "message" in data, "Response should contain message"
        assert data["message"] == YOU_SHOULD_BE_AUTHORISED_MESSAGE, f"Expected message to be '{YOU_SHOULD_BE_AUTHORISED_MESSAGE}', but got '{data['message']}'"