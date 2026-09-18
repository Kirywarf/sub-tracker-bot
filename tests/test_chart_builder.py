import matplotlib.pyplot as plt
from services.chart_builder import build_expense_pie_chart, build_monthly_projection_bar_chart


def test_build_expense_pie_chart_and_no_leak():
    # Verify starting state: no open figures
    plt.close("all")
    assert len(plt.get_fignums()) == 0

    data = [
        {"name": "Яндекс Плюс", "annual_cost": 3600.0},
        {"name": "YouTube Premium", "annual_cost": 4800.0},
        {"name": "Spotify", "annual_cost": 2400.0},
    ]

    buf = build_expense_pie_chart(data, currency="RUB")

    # Check buffer contains valid PNG data
    content = buf.getvalue()
    assert len(content) > 0
    assert content.startswith(b"\x89PNG\r\n\x1a\n")

    # CRITICAL: Matplotlib figure must be closed to avoid memory/FD leaks
    assert len(plt.get_fignums()) == 0


def test_build_expense_pie_chart_empty():
    plt.close("all")
    buf = build_expense_pie_chart([], currency="BYN")
    content = buf.getvalue()
    assert len(content) > 0
    assert content.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(plt.get_fignums()) == 0


def test_build_monthly_bar_chart_and_no_leak():
    plt.close("all")
    monthly = [1000.0, 1200.0, 800.0, 1500.0, 1000.0, 900.0, 1100.0, 1300.0, 1000.0, 1000.0, 1200.0, 1400.0]
    buf = build_monthly_projection_bar_chart(monthly, currency="RUB")

    content = buf.getvalue()
    assert len(content) > 0
    assert content.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(plt.get_fignums()) == 0


def test_build_expense_pie_chart_currencies_and_labels():
    plt.close("all")
    data = [
        {"name": "Very Long Subscription Name That Should Be Truncated", "annual_cost": 150.0},
        {"name": "Netflix", "annual_cost": 50.0},
        {"name": "Spotify", "annual_cost": 25.5},
        {"name": "Free Service", "annual_cost": 0.0},
    ]

    for curr in ["BYN", "USD", "PLN", "EUR"]:
        buf = build_expense_pie_chart(data, currency=curr)
        content = buf.getvalue()
        assert len(content) > 0
        assert content.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(plt.get_fignums()) == 0

