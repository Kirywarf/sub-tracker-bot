import pytest
from unittest.mock import patch, AsyncMock
from services.currency import (
    convert_currency,
    get_exchange_rates,
    get_exchange_rates_sync,
    detect_default_currency,
    DEFAULT_RATES_TO_USD,
)
from database.models import Subscription
from datetime import date


def test_convert_currency_same_currency():
    assert convert_currency(100.0, "RUB", "RUB") == 100.0
    assert convert_currency(50.5, "USD", "USD") == 50.5
    assert convert_currency(20.0, "BYN", "byn") == 20.0


def test_convert_currency_custom_rates():
    custom_rates = {
        "USD": 1.0,
        "RUB": 100.0,
        "BYN": 2.5,
        "EUR": 0.8,
        "PLN": 4.0,
    }
    # 10 USD -> RUB: 10 * 100 = 1000 RUB
    assert convert_currency(10.0, "USD", "RUB", rates=custom_rates) == 1000.0

    # 1000 RUB -> USD: 1000 / 100 = 10 USD
    assert convert_currency(1000.0, "RUB", "USD", rates=custom_rates) == 10.0

    # 5 BYN -> RUB: (5 / 2.5) * 100 = 200 RUB
    assert convert_currency(5.0, "BYN", "RUB", rates=custom_rates) == 200.0

    # 40 PLN -> BYN: (40 / 4.0) * 2.5 = 25 BYN
    assert convert_currency(40.0, "PLN", "BYN", rates=custom_rates) == 25.0


def test_convert_currency_fallback_rates():
    # If no rates supplied, uses cached or default rates without crashing
    converted = convert_currency(100.0, "USD", "RUB")
    assert converted > 0
    expected = 100.0 * DEFAULT_RATES_TO_USD["RUB"]
    assert pytest.approx(converted, 0.01) == expected


def test_detect_default_currency():
    subs = [
        Subscription(service_name="S1", price=10, currency="USD", period_days=30, next_billing_date=date.today(), is_active=True),
        Subscription(service_name="S2", price=20, currency="BYN", period_days=30, next_billing_date=date.today(), is_active=True),
        Subscription(service_name="S3", price=30, currency="BYN", period_days=30, next_billing_date=date.today(), is_active=True),
    ]
    assert detect_default_currency(subs) == "BYN"

    # Inactive subscriptions should not dominate
    subs_with_inactive = [
        Subscription(service_name="S1", price=10, currency="USD", period_days=30, next_billing_date=date.today(), is_active=True),
        Subscription(service_name="S2", price=20, currency="BYN", period_days=30, next_billing_date=date.today(), is_active=False),
        Subscription(service_name="S3", price=30, currency="BYN", period_days=30, next_billing_date=date.today(), is_active=False),
    ]
    assert detect_default_currency(subs_with_inactive) == "USD"

    # Empty subscriptions list
    assert detect_default_currency([]) == "RUB"


@pytest.mark.asyncio
async def test_get_exchange_rates_fallback_on_network_error():
    with patch("aiohttp.ClientSession.get", side_effect=Exception("Network error")):
        rates = await get_exchange_rates()
        assert "USD" in rates
        assert "RUB" in rates
        assert "BYN" in rates
        assert "PLN" in rates
