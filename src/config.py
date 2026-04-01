import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
CHANNELS_CONFIG_PATH = BASE_DIR / "config" / "channels.yaml"

load_dotenv(ENV_PATH)


class Settings:
    telegram_api_id: int = int(os.getenv("TELEGRAM_API_ID", "0"))
    telegram_api_hash: str = os.getenv("TELEGRAM_API_HASH", "")
    telegram_phone: str = os.getenv("TELEGRAM_PHONE", "")
    telegram_session_name: str = os.getenv("TELEGRAM_SESSION_NAME", "telegram_monitor")

    yandex_access_token: str = os.getenv("YANDEX_ACCESS_TOKEN", "")
    yandex_scenario_id: str = os.getenv("YANDEX_SCENARIO_ID", "")


def load_channels_config() -> list[dict]:
    if not CHANNELS_CONFIG_PATH.exists():
        return []

    with open(CHANNELS_CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    channels = data.get("channels", [])
    if not isinstance(channels, list):
        raise ValueError("config/channels.yaml: 'channels' must be a list")

    return channels


settings = Settings()
channels_config = load_channels_config()