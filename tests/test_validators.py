from app.services.validators import is_valid_city, is_valid_date


def test_city():
    assert is_valid_city("Москва")
    assert is_valid_city("New York")
    assert not is_valid_city("12345")
    assert not is_valid_city("")


def test_date():
    assert is_valid_date("01.01.2026")
    assert not is_valid_date("2026-01-01")
    assert not is_valid_date("32.13.2026")
