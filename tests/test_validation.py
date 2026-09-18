import pytest
from datetime import date
from bot.utils.validators import (
    validate_service_name,
    validate_price,
    validate_period_days,
    validate_billing_date,
    validate_cancel_url,
)


def test_validate_service_name():
    valid, val, err = validate_service_name("  Яндекс Музыка  ")
    assert valid is True
    assert val == "Яндекс Музыка"

    valid, val, err = validate_service_name("")
    assert valid is False
    assert "не может быть пустым" in err

    valid, val, err = validate_service_name("a" * 105)
    assert valid is False
    assert "Слишком длинное" in err


def test_validate_price():
    valid, val, err = validate_price("299")
    assert valid is True
    assert val == 299.0

    valid, val, err = validate_price(" 1 499,90 ")
    assert valid is True
    assert val == 1499.90

    valid, val, err = validate_price("-50")
    assert valid is False
    assert "больше нуля" in err

    valid, val, err = validate_price("abc")
    assert valid is False
    assert "Некорректный формат" in err


def test_validate_period_days():
    valid, val, err = validate_period_days("30")
    assert valid is True
    assert val == 30

    valid, val, err = validate_period_days("0")
    assert valid is False

    valid, val, err = validate_period_days("4000")
    assert valid is False
    assert "не может превышать" in err

    valid, val, err = validate_period_days("month")
    assert valid is False


def test_validate_billing_date():
    valid, val, err = validate_billing_date("25.10.2026")
    assert valid is True
    assert val == date(2026, 10, 25)

    # Leap year check
    valid, val, err = validate_billing_date("29.02.2024")
    assert valid is True
    assert val == date(2024, 2, 29)

    # Invalid leap day
    valid, val, err = validate_billing_date("29.02.2023")
    assert valid is False
    assert "Неверный формат" in err

    valid, val, err = validate_billing_date("32.01.2026")
    assert valid is False

    valid, val, err = validate_billing_date("not-a-date")
    assert valid is False


def test_validate_cancel_url():
    valid, val, err = validate_cancel_url("https://plus.yandex.ru/my/sub")
    assert valid is True
    assert val == "https://plus.yandex.ru/my/sub"

    valid, val, err = validate_cancel_url("http://example.com")
    assert valid is True

    valid, val, err = validate_cancel_url("ftp://example.com")
    assert valid is False

    valid, val, err = validate_cancel_url("just text")
    assert valid is False
