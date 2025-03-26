import pytest
import requests
import allure
from config import BASE_URL
from faker import Faker

fake = Faker()


@allure.suite("User Profile Management")
class TestUserProfileManagement:

    @allure.title("Get user info with authorization")
    def test_get_user_info_with_auth(self, create_user):
        url = f"{BASE_URL}/auth/user"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        response = requests.get(url, headers=headers)

        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        data = response.json()
        assert data["success"] == True, "Expected success to be True"
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == create_user["user_data"]["email"], "Email should match"
        assert data["user"]["name"] == create_user["user_data"]["name"], "Name should match"

    @allure.title("Get user info without authorization")
    def test_get_user_info_without_auth(self, create_user):
        url = f"{BASE_URL}/auth/user"
        response = requests.get(url)

        assert response.status_code == 401, f"Expected status code 401, but got {response.status_code}"
        data = response.json()
        assert data["success"] == False, "Expected success to be False"
        assert data["message"] == "You should be authorised", "Expected message to be 'You should be authorised'"

    @allure.title("Update user info with authorization")
    def test_update_user_info_with_auth(self, create_user):
        url = f"{BASE_URL}/auth/user"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        new_name = fake.name()
        payload = {"name": new_name}
        response = requests.patch(url, headers=headers, json=payload)

        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        data = response.json()
        assert data["success"] == True, "Expected success to be True"
        assert "user" in data, "Response should contain user"
        assert data["user"]["name"] == new_name, "Name should be updated"

    @allure.title("Update user info without authorization")
    def test_update_user_info_without_auth(self, create_user):
        url = f"{BASE_URL}/auth/user"
        new_name = fake.name()
        payload = {"name": new_name}
        response = requests.patch(url, json=payload)

        assert response.status_code == 401, f"Expected status code 401, but got {response.status_code}"
        data = response.json()
        assert data["success"] == False, "Expected success to be False"
        assert data["message"] == "You should be authorised", "Expected message to be 'You should be authorised'"

    @allure.title("Update user email with existing email")
    def test_update_user_email_with_existing_email(self, create_user):
        new_email = fake.email()
        url2 = f"{BASE_URL}/auth/register"
        payload2 = {"email": new_email, "password": fake.password(), "name": fake.name()}
        response2 = requests.post(url2, json=payload2)
        assert response2.status_code == 200
        data2 = response2.json()
        second_user_token = data2["accessToken"]

        url = f"{BASE_URL}/auth/user"
        headers = {"Authorization": create_user["tokens"]["accessToken"]}
        payload = {"email": new_email}
        response = requests.patch(url, headers=headers, json=payload)

        assert response.status_code == 403, f"Expected status code 403, but got {response.status_code}"
        data = response.json()
        assert data["success"] == False, "Expected success to be False"
        assert data["message"] == "User with such email already exists", "Expected message to be 'User with such email already exists'"

        delete_url = f"{BASE_URL}/auth/user"
        headers2 = {"Authorization": second_user_token}
        delete_response = requests.delete(delete_url, headers=headers2)
        if delete_response.status_code == 202:
            print(f"Second user {new_email} deleted successfully")
        else:
            print(f"Failed to delete second user {new_email}: {delete_response.status_code} - {delete_response.text}")