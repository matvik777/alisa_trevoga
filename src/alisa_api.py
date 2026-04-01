import requests

from config import settings


class AlisaAPIError(Exception):
    pass


def run_scenario() -> dict:
    if not settings.yandex_access_token:
        raise AlisaAPIError("YANDEX_ACCESS_TOKEN is empty")

    if not settings.yandex_scenario_id:
        raise AlisaAPIError("YANDEX_SCENARIO_ID is empty")

    url = (
        f"https://api.iot.yandex.net/v1.0/scenarios/"
        f"{settings.yandex_scenario_id}/actions"
    )

    headers = {
        "Authorization": f"Bearer {settings.yandex_access_token}"
    }

    try:
        response = requests.post(url, headers=headers, timeout=(10, 30))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise AlisaAPIError(f"Failed to run scenario: {e}") from e