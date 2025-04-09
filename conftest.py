import pytest
import requests
from config import BASE_URL
import json
import time
import logging
import data.user_data
from faker import Faker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def make_api_request(method, url, headers=None, data=None, retries=3, backoff_factor=0.5):
    for attempt in range(retries):
        try:
            response = requests.request(method, url, headers=headers, data=data)
            response.raise_for_status()
            logger.debug(f"Запрос к {url} успешен с {attempt + 1} попытки")
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Запрос к {url} не удался с {attempt + 1} попытки: {e}")
            if attempt == retries - 1:
                logger.error(f"Запрос к {url} не удался после {retries} попыток.")
                raise
            time.sleep(backoff_factor * (2 ** attempt))
    return None


@pytest.fixture(scope="session")
def fake():
    faker = Faker()
    faker.seed_instance(42)
    return faker


@pytest.fixture(scope="function")
def unique_user_data(fake):
    return data.user_data.generate_unique_user_data(fake)

@pytest.fixture(scope="function")
def create_user(unique_user_data):
    url = f"{BASE_URL}/auth/register"
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps(unique_user_data)

    try:
        response = make_api_request("POST", url, headers=headers, data=payload)
        data = response.json()
        access_token = data["accessToken"]
        refresh_token = data["refreshToken"]
        logger.info(f"Пользователь {unique_user_data['email']} успешно создан.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Не удалось создать пользователя: {e}")
        pytest.fail(f"Не удалось создать пользователя: {e}")

    yield {"user_data": unique_user_data, "tokens": {"accessToken": access_token, "refreshToken": refresh_token}}

    delete_url = f"{BASE_URL}/auth/user"
    headers = {"Authorization": access_token}
    try:
        delete_response = make_api_request("DELETE", delete_url, headers=headers)
        if delete_response.status_code == 202:
            logger.info(f"Пользователь {unique_user_data['email']} успешно удален.")
        elif delete_response.status_code == 404:
            logger.warning(f"Пользователь {unique_user_data['email']} не найден при удалении (возможно, уже удален).")
        else:
            logger.error(f"Не удалось удалить пользователя {unique_user_data['email']}: {delete_response.status_code} - {delete_response.text}")
            pytest.fail(f"Не удалось удалить пользователя {unique_user_data['email']}: {delete_response.status_code} - {delete_response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Не удалось удалить пользователя {unique_user_data['email']}: {e}")
        pytest.fail(f"Не удалось удалить пользователя {unique_user_data['email']}: {e}")