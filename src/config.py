import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    yandex_access_token: str = os.getenv("YANDEX_ACCESS_TOKEN", "")
    yandex_scenario_id: str = os.getenv("YANDEX_SCENARIO_ID", "")


settings = Settings()