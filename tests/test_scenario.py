from app.domain.scenario import describe_day, search_holidays
from datetime import date


def test_describe_weekend():
    saturday = date(2026, 1, 3)
    assert "Суббота" in describe_day(saturday)


def test_search_exact():
    result = search_holidays("Новый год")
    assert "Новый год" in result or "найден" in result.lower()


def test_search_typo():
    result = search_holidays("Навый гот")
    assert "Новый год" in result


def test_search_empty():
    result = search_holidays("")
    assert "Напишите" in result
