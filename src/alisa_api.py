from __future__ import annotations

import requests

from config import settings


class AlisaAPIError(Exception):
    pass


def resolve_scenario_id(scenario_id: str | None = None) -> str:
    configured_scenario_id = (scenario_id or "").strip()
    fallback_scenario_id = settings.yandex_scenario_id.strip()

    if configured_scenario_id and not configured_scenario_id.startswith("PASTE_"):
        return configured_scenario_id

    if fallback_scenario_id:
        return fallback_scenario_id

    if configured_scenario_id.startswith("PASTE_"):
        raise AlisaAPIError(
            "scenario_id contains a placeholder and YANDEX_SCENARIO_ID is empty",
        )

    raise AlisaAPIError("scenario_id is empty")


def run_scenario(scenario_id: str | None = None) -> dict:
    if not settings.yandex_access_token:
        raise AlisaAPIError("YANDEX_ACCESS_TOKEN is empty")

    resolved_scenario_id = resolve_scenario_id(scenario_id)

    url = f"https://api.iot.yandex.net/v1.0/scenarios/{resolved_scenario_id}/actions"
    headers = {
        "Authorization": f"Bearer {settings.yandex_access_token}",
    }

    try:
        response = requests.post(url, headers=headers, timeout=(10, 30))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise AlisaAPIError(f"Failed to run scenario '{resolved_scenario_id}': {e}") from e
