from coursera_house.settings import SMART_HOME_API_URL, SMART_HOME_ACCESS_TOKEN
import requests


def fetch_controller_data():
    response = requests.get(
        SMART_HOME_API_URL, headers={"Authorization": SMART_HOME_ACCESS_TOKEN}
    )
    return response.json().get("data", [])


def send_command_to_controller(mechanisms: dict):
    if not mechanisms:
        return
    commands = [{"name": name, "value": value} for name, value in mechanisms.items()]
    data_for_controller = {"controllers": commands}
    response = requests.post(
        SMART_HOME_API_URL,
        json=data_for_controller,
        headers={"Authorization": SMART_HOME_ACCESS_TOKEN},
    )
    return response.json().get("data", [])


def normalize_data(controller_data: list):
    return {sensor["name"]: sensor["value"] for sensor in controller_data}
