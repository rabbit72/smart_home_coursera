from __future__ import absolute_import, unicode_literals
from ..celery import app
from django.core.mail import send_mail

from coursera_house.core.utils import fetch_controller_data, normalize_data
from coursera_house.core.utils import send_command_to_controller

from .models import Setting


@app.task
def smart_home_manager():
    checks = (
        check_leak_detector,
        check_cold_water_tap,
        check_boil_temperature,
        check_curtains,
        check_air_temperature,
        check_smoke,
    )
    real_condition = normalize_data(fetch_controller_data())
    command_for_controller = {}
    for check in checks:
        command_for_controller.update(check(real_condition))
    send_command_to_controller(command_for_controller)


def check_leak_detector(condition: dict) -> dict:
    leak_detector = condition["leak_detector"]
    taps = "cold_water", "hot_water"
    if leak_detector:
        commands = {tap: False for tap in taps if condition[tap]}
    else:
        commands = {}
    if leak_detector and commands:
        send_mail(
            'smart home',
            'Leak detector - True',
            'rabbit72ru@bk.ru',
            ['rabbit72rus@gmail.com'],
            fail_silently=False,
        )
    return commands


def check_cold_water_tap(condition: dict) -> dict:
    commands = {}
    cold_water_tap = condition["cold_water"]
    if not cold_water_tap:
        if condition["boiler"]:
            commands["boiler"] = False
        if condition["washing_machine"] == "on":
            commands["washing_machine"] = "off"
    return commands


def check_boil_temperature(condition: dict) -> dict:
    commands = {}
    smoke_detector = condition["smoke_detector"]
    cold_water_tap = condition["cold_water"]
    boiler_temperature = condition["boiler_temperature"]
    boiler_status = condition["boiler"]
    hot_water_target_temperature = Setting.objects.get(
        controller_name="hot_water_target_temperature"
    ).value
    boil_turn_on_point = hot_water_target_temperature * 0.9
    boil_turn_off_point = hot_water_target_temperature * 1.1
    if cold_water_tap and not smoke_detector:
        if (boiler_temperature < boil_turn_on_point) and not boiler_status:
            commands["boiler"] = True
        elif (boiler_temperature > boil_turn_off_point) and boiler_status:
            commands["boiler"] = False
    return commands


def check_air_temperature(condition: dict) -> dict:
    commands = {}
    smoke_detector = condition["smoke_detector"]
    bedroom_temperature = condition["bedroom_temperature"]
    air_conditioner = condition["air_conditioner"]
    bedroom_target_temperature = Setting.objects.get(
        controller_name="bedroom_target_temperature"
    ).value
    air_conditioner_turn_off_point = bedroom_target_temperature * 0.9
    air_conditioner_turn_on_point = bedroom_target_temperature * 1.1
    if not smoke_detector:
        if (bedroom_temperature > air_conditioner_turn_on_point) and not air_conditioner:
            commands["air_conditioner"] = True
        elif (bedroom_temperature < air_conditioner_turn_off_point) and air_conditioner:
            commands["air_conditioner"] = False
    return commands


def check_curtains(condition: dict) -> dict:
    commands = {}
    curtains = condition["curtains"]
    outdoor_light = condition["outdoor_light"]
    bedroom_light = condition["bedroom_light"]
    sunrise = 50
    if curtains == "slightly_open":
        return {}
    if (outdoor_light < sunrise) and not bedroom_light and curtains != "open":
        commands["curtains"] = "open"
    elif ((outdoor_light > sunrise) or bedroom_light) and curtains != "close":
        commands["curtains"] = "close"
    return commands


def check_smoke(condition: dict) -> dict:
    machines = [
        "air_conditioner",
        "bedroom_light",
        "bathroom_light",
        "boiler",
    ]
    smoke_detector = condition["smoke_detector"]
    if smoke_detector:
        commands = {machine: False for machine in machines if condition[machine]}
        if condition["washing_machine"] == "on":
            commands["washing_machine"] = "off"
    else:
        commands = {}

    return commands
