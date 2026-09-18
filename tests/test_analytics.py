import pytest
from datetime import date
from database.models import Subscription
from bot.handlers.analytics import calculate_annual_metrics


def test_calculate_annual_metrics():
    subs = [
        Subscription(
            id=1,
            user_id=1,
            service_name="Яндекс Плюс",
            price=299.0,
            currency="RUB",
            period_days=30,
            next_billing_date=date(2026, 10, 1),
            is_active=True,
        ),
        Subscription(
            id=2,
            user_id=1,
            service_name="Telegram Premium",
            price=2990.0,
            currency="RUB",
            period_days=365,
            next_billing_date=date(2026, 12, 1),
            is_active=True,
        ),
        Subscription(
            id=3,
            user_id=1,
            service_name="Inactive Service",
            price=1000.0,
            currency="RUB",
            period_days=30,
            next_billing_date=date(2026, 10, 1),
            is_active=False,
        ),
        Subscription(
            id=4,
            user_id=1,
            service_name="A1 Belarus",
            price=25.0,
            currency="BYN",
            period_days=30,
            next_billing_date=date(2026, 10, 5),
            is_active=True,
        ),
    ]

    metrics = calculate_annual_metrics(subs)

    # Check RUB metrics
    assert "RUB" in metrics
    rub = metrics["RUB"]
    assert rub["services_count"] == 2  # Inactive service excluded
    # Яндекс: (365 / 30) * 299 = 3637.833...
    # Telegram: (365 / 365) * 2990 = 2990.0
    expected_rub_annual = (365.0 / 30 * 299) + 2990.0
    assert pytest.approx(rub["total_annual"], 0.01) == expected_rub_annual
    assert pytest.approx(rub["monthly_avg"], 0.01) == expected_rub_annual / 12.0

    # Top-3 order
    assert rub["top_3"][0]["name"] == "Яндекс Плюс"
    assert rub["top_3"][1]["name"] == "Telegram Premium"

    # Check BYN metrics
    assert "BYN" in metrics
    byn = metrics["BYN"]
    assert byn["services_count"] == 1
    expected_byn_annual = (365.0 / 30 * 25)
    assert pytest.approx(byn["total_annual"], 0.01) == expected_byn_annual


def test_calculate_unified_metrics_multi_currency():
    from bot.handlers.analytics import calculate_unified_metrics, format_analytics_caption

    subs = [
        Subscription(
            id=1,
            user_id=1,
            service_name="Яндекс Плюс",
            price=300.0,
            currency="RUB",
            period_days=30,
            is_active=True,
        ),
        Subscription(
            id=2,
            user_id=1,
            service_name="Netflix",
            price=10.0,
            currency="USD",
            period_days=30,
            is_active=True,
        ),
        Subscription(
            id=3,
            user_id=1,
            service_name="Inactive",
            price=50.0,
            currency="USD",
            period_days=30,
            is_active=False,
        ),
    ]

    rates = {
        "USD": 1.0,
        "RUB": 100.0,
    }

    # Target currency: RUB
    # Яндекс: (365 / 30) * 300 = 3650.0 RUB
    # Netflix: (365 / 30) * 10 = 121.6667 USD -> * 100 = 12166.67 RUB
    metrics_rub = calculate_unified_metrics(subs, target_currency="RUB", rates=rates)

    assert metrics_rub["target_currency"] == "RUB"
    assert metrics_rub["services_count"] == 2  # Inactive excluded
    expected_total = 3650.0 + 12166.6667
    assert pytest.approx(metrics_rub["total_annual"], 0.01) == expected_total
    assert pytest.approx(metrics_rub["monthly_avg"], 0.01) == expected_total / 12.0

    # Netflix should be ranked #1 since 12166 > 3650 in RUB
    assert metrics_rub["services"][0]["name"] == "Netflix"
    assert metrics_rub["services"][0]["is_converted"] is True
    assert metrics_rub["services"][1]["name"] == "Яндекс Плюс"
    assert metrics_rub["services"][1]["is_converted"] is False

    # Target currency: USD
    metrics_usd = calculate_unified_metrics(subs, target_currency="USD", rates=rates)
    assert metrics_usd["target_currency"] == "USD"
    # Яндекс in USD: 3650.0 / 100 = 36.5 USD
    # Netflix in USD: 121.6667 USD
    expected_usd_total = 36.5 + 121.66667
    assert pytest.approx(metrics_usd["total_annual"], 0.01) == expected_usd_total

    # Caption formatting check
    caption = format_analytics_caption(metrics_rub)
    assert "Яндекс Плюс" in caption
    assert "Netflix" in caption
    assert "Все расходы приведены к: ₽ (RUB)" in caption
    assert "Топ затратных сервисов" in caption


def test_calculate_unified_metrics_with_duplicates_and_byn():
    from bot.handlers.analytics import calculate_unified_metrics, format_analytics_caption

    subs = [
        Subscription(
            id=1,
            user_id=1,
            service_name="Spotify",
            price=15.0,
            currency="BYN",
            period_days=30,
            is_active=True,
        ),
        Subscription(
            id=2,
            user_id=1,
            service_name="Яндекс Плюс",
            price=11.99,
            currency="BYN",
            period_days=30,
            is_active=True,
        ),
        Subscription(
            id=3,
            user_id=1,
            service_name="Spotify",
            price=15.0,
            currency="PLN",
            period_days=30,
            is_active=True,
        ),
    ]

    rates = {
        "USD": 1.0,
        "BYN": 3.0,
        "PLN": 3.75,
    }

    # Default target currency is BYN
    metrics = calculate_unified_metrics(subs, rates=rates)
    assert metrics["target_currency"] == "BYN"
    assert metrics["services_count"] == 3

    caption = format_analytics_caption(metrics)
    assert "Spotify (BYN)" in caption
    assert "Spotify (PLN)" in caption
    assert "Яндекс Плюс" in caption
    assert "Все расходы приведены к: Br (BYN)" in caption


