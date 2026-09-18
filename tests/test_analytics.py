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
