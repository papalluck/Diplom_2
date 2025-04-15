import pytest
import json
import requests
from config import BASE_URL
from data.user_data import generate_unique_user_data
from faker import Faker
from api_utils import logger
from api_helper import get_ingredient_ids_from_api

@pytest.fixture(scope="session")
def fake():
    faker = Faker()
    faker.seed_instance(42)
    return faker

@pytest.fixture(scope="session")
def get_ingredients():
    ingredient_ids = get_ingredient_ids_from_api()
    if ingredient_ids is None:
        pytest.fail("Не удалось получить список ингредиентов из API.")
    if len(ingredient_ids) < 2:
        pytest.skip("Недостаточно ингредиентов для создания заказа.")
    return ingredient_ids

@pytest.fixture(scope="function")
def create_and_delete_user(fake):
    unique_user_data = generate_unique_user_data(fake)

    register_url = f"{BASE_URL}/auth/register"
    register_headers = {'Content-Type': 'application/json'}
    register_payload = json.dumps(unique_user_data)
    access_token = None
    refresh_token = None

    try:
        register_response = requests.post(register_url, headers=register_headers, data=register_payload, verify=False)
        register_response.raise_for_status()
        register_data = register_response.json()
        access_token = register_data["accessToken"]
        refresh_token = register_data["refreshToken"]
        logger.info(f"Пользователь {unique_user_data['email']} успешно зарегистрирован.")

    except requests.exceptions.HTTPError as e:
        if register_response.status_code == 403 and "User already exists" in register_response.text:
            logger.warning(f"Пользователь {unique_user_data['email']} уже существует.")
            pass
        else:
            logger.error(f"Не удалось зарегистрировать пользователя: {e}")
            pytest.fail(f"Не удалось зарегистрировать пользователя: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при регистрации пользователя: {e}")
        pytest.fail(f"Не удалось зарегистрировать пользователя: {e}")

    login_url = f"{BASE_URL}/auth/login"
    login_headers = {'Content-Type': 'application/json'}
    login_payload = json.dumps({"email": unique_user_data["email"], "password": unique_user_data["password"]})

    try:
        login_response = requests.post(login_url, headers=login_headers, data=login_payload, verify=False)
        login_response.raise_for_status()
        login_data = login_response.json()
        access_token = login_data["accessToken"]
        refresh_token = login_data["refreshToken"]
        logger.info(f"Пользователь {unique_user_data['email']} успешно авторизован.")
        logger.info(f"Ответ сервера при авторизации: {login_data}")

    except requests.exceptions.HTTPError as e:
        logger.error(f"Не удалось авторизовать пользователя: {e}")
        pytest.fail(f"Не удалось авторизовать пользователя: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при авторизации пользователя: {e}")
        pytest.fail(f"Не удалось авторизовать пользователя: {e}")

    user_data = {"user_data": unique_user_data, "tokens": {"accessToken": access_token, "refreshToken": refresh_token}}

    yield user_data

    if access_token:
        delete_url = f"{BASE_URL}/auth/user"
        delete_headers = {"Authorization": f"{access_token}"}
        try:
            delete_response = requests.delete(delete_url, headers=delete_headers, verify=False)
            if delete_response.status_code == 202:
                logger.info(f"Пользователь {unique_user_data['email']} успешно удален.")
            elif delete_response.status_code == 404:
                pass
            else:
                logger.error(f"Не удалось удалить пользователя {unique_user_data['email']}: {delete_response.status_code} - {delete_response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Не удалось удалить пользователя {unique_user_data['email']}: {e}")
    else:
        logger.warning("Невозможно удалить пользователя, так как не был получен access_token.")