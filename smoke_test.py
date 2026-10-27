"""Smoke-проверка проекта. Запуск: python smoke_test.py"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def run_checks() -> int:
    errors: list[str] = []

    if not Path(".env").exists():
        errors.append("Нет файла .env (скопируйте .env.example → .env)")
    else:
        load_dotenv()
        if not os.getenv("VK_TOKEN"):
            errors.append("VK_TOKEN не задан в .env")

    try:
        from app.services.validators import is_valid_city, is_valid_date

        assert is_valid_date("01.01.2026")
        assert is_valid_city("Москва")
    except Exception as exc:
        errors.append(f"Валидаторы: {exc}")

    try:
        from app.domain import scenario

        today = scenario.today_text()
        assert "Сегодня" in today

        week = scenario.week_text()
        assert "Ближайшие 7 дней" in week

        search = scenario.search_holidays("Новый год")
        assert "Новый год" in search or "найден" in search.lower()
    except Exception as exc:
        errors.append(f"Сценарий: {exc}")

    if errors:
        print("Обнаружены проблемы:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("Все проверки пройдены")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
