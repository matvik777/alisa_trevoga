from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
STATE_DIR = BASE_DIR / "state"
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


@dataclass
class AppSettings:
    telegram_api_id: int
    telegram_api_hash: str
    telegram_phone: str
    telegram_session_name: str
    yandex_access_token: str
    yandex_scenario_id: str

    @classmethod
    def from_env(cls) -> "AppSettings":
        return cls(
            telegram_api_id=int(os.getenv("TELEGRAM_API_ID", "0")),
            telegram_api_hash=os.getenv("TELEGRAM_API_HASH", ""),
            telegram_phone=os.getenv("TELEGRAM_PHONE", ""),
            telegram_session_name=os.getenv("TELEGRAM_SESSION_NAME", "telegram_monitor"),
            yandex_access_token=os.getenv("YANDEX_ACCESS_TOKEN", ""),
            yandex_scenario_id=os.getenv("YANDEX_SCENARIO_ID", ""),
        )


def load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a dict: {path}")

    return data


def load_channels() -> list[dict[str, Any]]:
    data = load_yaml_file(CONFIG_DIR / "channels.yaml")
    channels = data.get("channels", [])
    if not isinstance(channels, list):
        raise ValueError("config/channels.yaml: 'channels' must be a list")
    return channels


def load_rules() -> list[dict[str, Any]]:
    data = load_yaml_file(CONFIG_DIR / "rules.yaml")
    rules = data.get("rules", [])
    if not isinstance(rules, list):
        raise ValueError("config/rules.yaml: 'rules' must be a list")
    return rules


def load_targets() -> list[dict[str, Any]]:
    data = load_yaml_file(CONFIG_DIR / "targets.yaml")
    targets = data.get("targets", [])
    if not isinstance(targets, list):
        raise ValueError("config/targets.yaml: 'targets' must be a list")
    return targets


def load_schedule() -> dict[str, Any]:
    data = load_yaml_file(CONFIG_DIR / "schedule.yaml")
    schedule = data.get("schedule", {})
    if not isinstance(schedule, dict):
        raise ValueError("config/schedule.yaml: 'schedule' must be a dict")
    return schedule


settings = AppSettings.from_env()
channels_config = load_channels()
rules_config = load_rules()
targets_config = load_targets()
schedule_config = load_schedule()

STATE_DIR.mkdir(exist_ok=True)
