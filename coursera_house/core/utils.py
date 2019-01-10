from coursera_house.settings import SMART_HOME_API_URL, SMART_HOME_ACCESS_TOKEN
import requests


def fetch_controller_data():
    response = requests.get(
        SMART_HOME_API_URL, headers={"Authorization": SMART_HOME_ACCESS_TOKEN}
    )
    controller_data = response.json().get("data", [])
    normalize_data = {sensor["name"]: sensor["value"] for sensor in controller_data}
    return normalize_data
