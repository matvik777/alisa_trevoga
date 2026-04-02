from __future__ import annotations

import requests

from config import settings


class AlisaAPIError(Exception):
    pass


def run_scenario(scenario_id: str) -> dict:
    if not settings.yandex_access_token:
        raise AlisaAPIError("YANDEX_ACCESS_TOKEN is empty")

    if not scenario_id:
        raise AlisaAPIError("scenario_id is empty")

    url = f"https://api.iot.yandex.net/v1.0/scenarios/{scenario_id}/actions"
    headers = {
        "Authorization": f"Bearer {settings.yandex_access_token}",
    }

    try:
        response = requests.post(url, headers=headers, timeout=(10, 30))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise AlisaAPIError(f"Failed to run scenario '{scenario_id}': {e}") from e