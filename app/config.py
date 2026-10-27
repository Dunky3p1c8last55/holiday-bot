import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


class Settings:
    def __init__(self) -> None:
        self.vk_token = os.getenv("VK_TOKEN", "")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
