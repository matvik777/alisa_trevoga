from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_PATH = Path(__file__).resolve().parent.parent / "state" / "state.json"


def _default_state() -> dict[str, Any]:
    return {
        "last_seen_ids": {},
        "last_triggered_at": {},
    }


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return _default_state()

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict[str, Any]) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_last_seen_id(state: dict[str, Any], channel_username: str) -> int:
    return int(state.get("last_seen_ids", {}).get(channel_username, 0))


def set_last_seen_id(state: dict[str, Any], channel_username: str, message_id: int) -> None:
    state.setdefault("last_seen_ids", {})
    state["last_seen_ids"][channel_username] = int(message_id)


def get_last_triggered_at(state: dict[str, Any], rule_name: str) -> str | None:
    return state.get("last_triggered_at", {}).get(rule_name)


def set_last_triggered_at_now(state: dict[str, Any], rule_name: str) -> None:
    state.setdefault("last_triggered_at", {})
    state["last_triggered_at"][rule_name] = datetime.now(timezone.utc).isoformat()