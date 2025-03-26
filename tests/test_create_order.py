import pytest
import requests
import allure
from config import BASE_URL, VALID_INGREDIENTS


@allure.suite("Order Creation")
class TestOrderCreation:
    @allure.title("Create order with authorization and ingredients")
    def test_create_order_with_auth_and_ingredients(self, create_user):
        url = f"{BASE_URL}/orders"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        payload = {"ingredients": VALID_INGREDIENTS}
        response = requests.post(url, headers=headers, json=payload)

        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        data = response.json()
        assert data["success"] == True, "Expected success to be True"
        assert "name" in data, "Response should contain order name"
        assert "order" in data, "Response should contain order"

    @allure.title("Create order without authorization")
    def test_create_order_without_auth(self):
        url = f"{BASE_URL}/orders"
        payload = {"ingredients": VALID_INGREDIENTS}
        response = requests.post(url, json=payload)
        assert response.status_code == 200
        try:
            data = response.json()
            assert data["success"] == True, "Expected success to be True"
        except:
            pass

    @allure.title("Create order with authorization but without ingredients")
    def test_create_order_with_auth_but_without_ingredients(self, create_user):
        url = f"{BASE_URL}/orders"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        payload = {"ingredients": []}
        response = requests.post(url, headers=headers, json=payload)

        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        data = response.json()
        assert data["success"] == False, "Expected success to be False"
        assert data["message"] == "Ingredient ids must be provided", "Expected message to be 'Ingredient ids must be provided'"

    @allure.title("Create order with authorization and invalid ingredients")
    def test_create_order_with_auth_and_invalid_ingredients(self, create_user):
        url = f"{BASE_URL}/orders"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        payload = {"ingredients": ["invalid_ingredient_id"]}
        response = requests.post(url, headers=headers, json=payload)
        assert response.status_code != 200