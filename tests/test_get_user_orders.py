import pytest
import requests
import allure
from config import BASE_URL


@allure.suite("Get User Orders")
class TestGetUserOrders:

    @allure.title("Get user orders with authorization")
    def test_get_user_orders_with_auth(self, create_user):
        url = f"{BASE_URL}/orders"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        response = requests.get(url, headers=headers)

        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        data = response.json()
        assert data["success"] == True, "Expected success to be True"
        assert "orders" in data, "Response should contain orders"
        assert isinstance(data["orders"], list), "Orders should be a list"

    @allure.title("Get user orders without authorization")
    def test_get_user_orders_without_auth(self):
        url = f"{BASE_URL}/orders"
        response = requests.get(url)

        assert response.status_code == 401, f"Expected status code 401, but got {response.status_code}"
        data = response.json()
        assert data["success"] == False, "Expected success to be False"
        assert data["message"] == "You should be authorised", "Expected message to be 'You should be authorised'"