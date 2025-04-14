import requests
import allure
from allure_commons.types import AttachmentType
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_api_request(method, url, headers=None, json=None, data=None, files=None, retries=3):

    session = requests.Session()
    session.verify = False

    for attempt in range(retries):
        try:
            with allure.step(f"Выполнение {method} запроса к {url} (попытка {attempt + 1})"):
                logger.info(f"Выполнение {method} запроса к {url} (попытка {attempt + 1})")
                response = session.request(method, url, headers=headers, json=json, data=data, files=files)

                allure.attach(
                    f"{method} {url}\nHeaders: {headers}\nBody: {json or data or files}\nResponse Code: {response.status_code}\nResponse Body: {response.text}",
                    name=f"Request/Response Details (Attempt {attempt + 1})",
                    attachment_type=AttachmentType.TEXT,
                )

                return response

        except requests.exceptions.RequestException as e:
            logger.warning(f"Запрос к {url} не удался с {attempt + 1} попытки: {e}")
            allure.attach(str(e), name=f"Ошибка при запросе (попытка {attempt + 1})", attachment_type=AttachmentType.TEXT)
            if attempt == retries - 1:
                logger.error(f"Запрос к {url} не удался после {retries} попыток.")
                return None

    return None