import requests
from config import BASE_URL
from api_utils import logger

def get_ingredient_ids_from_api():
    url = f"{BASE_URL}/ingredients"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        data = response.json()
        logger.info("Список ингредиентов успешно получен.")
        ingredient_ids = [ingredient["_id"] for ingredient in data["data"]]
        return ingredient_ids
    except requests.exceptions.RequestException as e:
        logger.error(f"Не удалось получить список ингредиентов: {e}")
        return None