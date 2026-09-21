import io
from typing import List, Dict, Any, Optional
import matplotlib
# Use non-interactive Agg backend to avoid GUI threads and file descriptor leaks
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from collections import Counter

# Apple System Colors Palette (Dark Mode)
APPLE_PALETTE = [
    "#2997FF",  # System Blue
    "#30D158",  # System Green / Mint
    "#FF9F0A",  # System Orange
    "#BF5AF2",  # System Purple
    "#FF375F",  # System Pink
    "#64D2FF",  # System Teal / Cyan
    "#FFD60A",  # System Yellow
    "#5E5CE6",  # System Indigo
]

CURRENCY_SYMBOLS = {
    "BYN": "Br",
    "RUB": "₽",
    "USD": "$",
    "EUR": "€",
    "PLN": "zł",
}


def build_expense_pie_chart(
    services_data: List[Dict[str, Any]],
    currency: str = "BYN",
) -> io.BytesIO:
    """
    Generates an Apple Card / Watch Activity Rings style donut chart.
    services_data is a list of dicts:
    [{"name": "Яндекс Плюс", "annual_cost": 3600.0}, ...]
    Returns io.BytesIO buffer with PNG image.
    Guarantees plt.close(fig) to prevent memory and file descriptor leaks.
    """
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(8, 6.2), dpi=140)

    try:
        # Apple OLED deep black background
        fig.patch.set_facecolor("#000000")
        ax.set_facecolor("#000000")

        # Configure font priority for Apple typography
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = [
            "SF Pro Display",
            "SF Pro Text",
            "Helvetica Neue",
            "Helvetica",
            "Arial",
            "DejaVu Sans",
        ]

        # Filter out negative or non-numeric costs
        valid_services = [s for s in services_data if s.get("annual_cost", 0) > 0]
        total_expense = sum(s["annual_cost"] for s in valid_services)
        curr_sym = CURRENCY_SYMBOLS.get(currency.upper().strip(), currency)

        if not valid_services or total_expense <= 0:
            # Apple-style minimalist empty state
            circle = Circle((0.5, 0.5), 0.32, color="#1c1c1e", fill=False, linewidth=8)
            ax.add_patch(circle)
            ax.text(
                0.5,
                0.53,
                "Нет активных подписок",
                color="#f5f5f7",
                fontsize=15,
                fontweight="bold",
                ha="center",
                va="center",
            )
            ax.text(
                0.5,
                0.46,
                "Добавьте подписку для аналитики",
                color="#86868b",
                fontsize=11,
                ha="center",
                va="center",
            )
            ax.axis("off")
        else:
            # Sort by cost descending
            sorted_data = sorted(valid_services, key=lambda x: x["annual_cost"], reverse=True)

            # If more than 6, group smaller into 'Другие'
            if len(sorted_data) > 6:
                top_items = sorted_data[:5]
                other_cost = sum(x["annual_cost"] for x in sorted_data[5:])
                plot_items = top_items + [{"name": "Другие", "annual_cost": other_cost}]
            else:
                plot_items = sorted_data

            name_counts = Counter(item.get("name", "") for item in plot_items)

            def format_label(item: Dict[str, Any]) -> str:
                name = item.get("name", "")
                orig_curr = item.get("original_currency")
                if name_counts[name] > 1 and orig_curr:
                    name = f"{name} ({orig_curr})"
                return name if len(name) <= 18 else name[:16] + "…"

            labels = [format_label(item) for item in plot_items]
            costs = [item["annual_cost"] for item in plot_items]
            colors = (APPLE_PALETTE * 2)[:len(plot_items)]

            def make_autopct(values):
                total = sum(values)
                def my_autopct(pct):
                    val = pct * total / 100.0
                    if pct < 5.5:
                        return ""
                    return f"{pct:.1f}%"
                return my_autopct

            # Donut chart with smooth Apple Card ring styling
            wedges, texts, autotexts = ax.pie(
                costs,
                labels=labels,
                autopct=make_autopct(costs),
                startangle=140,
                colors=colors,
                wedgeprops=dict(width=0.36, edgecolor="#000000", linewidth=3.5),
                pctdistance=0.81,
                labeldistance=1.12,
            )

            # Typography in Apple aesthetic
            for text in texts:
                text.set_color("#f5f5f7")
                text.set_fontsize(10.5)
                text.set_weight("semibold")

            for autotext in autotexts:
                autotext.set_color("#000000")
                autotext.set_fontsize(9)
                autotext.set_weight("heavy")

            # Center ring metric (Apple Watch / Wallet style)
            total_str = f"{total_expense:,.0f}" if total_expense >= 100 else f"{total_expense:.2f}"
            ax.text(
                0,
                0.14,
                "В С Е Г О   В   Г О Д",
                color="#86868b",
                fontsize=8,
                fontweight="bold",
                ha="center",
                va="center",
            )
            ax.text(
                0,
                -0.03,
                total_str,
                color="#f5f5f7",
                fontsize=20,
                fontweight="heavy",
                ha="center",
                va="center",
            )
            ax.text(
                0,
                -0.19,
                f"{curr_sym} ({currency})",
                color="#86868b",
                fontsize=11,
                fontweight="medium",
                ha="center",
                va="center",
            )

            ax.set_title(
                f"Структура годовых расходов",
                color="#f5f5f7",
                fontsize=16,
                fontweight="bold",
                pad=22,
            )

        plt.tight_layout()
        fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
        buf.seek(0)
    finally:
        plt.close(fig)

    return buf


def build_monthly_projection_bar_chart(
    monthly_breakdown: List[float],
    currency: str = "RUB",
) -> io.BytesIO:
    """
    Generates an Apple Health / Wallet style bar chart showing monthly expense distribution.
    Guarantees plt.close(fig).
    """
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(9, 5), dpi=140)

    try:
        # Apple OLED deep black background
        fig.patch.set_facecolor("#000000")
        ax.set_facecolor("#000000")

        months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
        x = range(len(months))
        curr_sym = CURRENCY_SYMBOLS.get(currency.upper().strip(), currency)

        # Apple System Blue rounded bars
        bars = ax.bar(
            x,
            monthly_breakdown,
            color="#2997ff",
            edgecolor="#2997ff",
            linewidth=0,
            width=0.55,
            zorder=3,
        )

        ax.set_title(
            f"Прогнозируемые траты по месяцам ({curr_sym})",
            color="#f5f5f7",
            fontsize=15,
            fontweight="bold",
            pad=18,
        )
        ax.set_xticks(x)
        ax.set_xticklabels(months, color="#86868b", fontsize=10, fontweight="semibold")
        ax.tick_params(axis="y", colors="#86868b", labelsize=9)
        ax.spines["bottom"].set_color("#2c2c2e")
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", linestyle="-", alpha=0.15, color="#ffffff", zorder=1)

        # Values above bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f"{height:,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    color="#f5f5f7",
                    fontsize=8.5,
                    fontweight="bold",
                )

        plt.tight_layout()
        fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
        buf.seek(0)
    finally:
        plt.close(fig)

    return buf
