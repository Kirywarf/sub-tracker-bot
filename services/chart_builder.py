import io
from typing import List, Dict, Any, Optional
import matplotlib
# Use non-interactive Agg backend to avoid GUI threads and file descriptor leaks
matplotlib.use("Agg")
import matplotlib.pyplot as plt


from collections import Counter


def build_expense_pie_chart(
    services_data: List[Dict[str, Any]],
    currency: str = "BYN",
) -> io.BytesIO:
    """
    Generates a stylish pie chart of subscription expenses.
    services_data is a list of dicts:
    [{"name": "Яндекс Плюс", "annual_cost": 3600.0}, ...]
    Returns io.BytesIO buffer with PNG image.
    Guarantees plt.close(fig) to prevent memory and file descriptor leaks.
    """
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(8, 6), dpi=120)

    try:
        # Background styling
        fig.patch.set_facecolor("#1e1e2e")
        ax.set_facecolor("#1e1e2e")

        # Filter out negative or non-numeric costs
        valid_services = [s for s in services_data if s.get("annual_cost", 0) > 0]
        total_expense = sum(s["annual_cost"] for s in valid_services)

        if not valid_services or total_expense <= 0:
            # Empty state graphic
            ax.text(
                0.5,
                0.5,
                "Нет данных о расходах",
                color="#cdd6f4",
                fontsize=16,
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
                return name if len(name) <= 20 else name[:18] + "…"

            labels = [format_label(item) for item in plot_items]
            costs = [item["annual_cost"] for item in plot_items]

            # Curated modern pastel/vibrant palette
            colors = [
                "#89b4fa",  # Blue
                "#a6e3a1",  # Green
                "#f38ba8",  # Red / Pink
                "#fab387",  # Peach / Orange
                "#cba6f7",  # Mauve / Purple
                "#94e2d5",  # Teal
                "#f9e2af",  # Yellow
            ]

            def make_autopct(values):
                total = sum(values)
                def my_autopct(pct):
                    val = pct * total / 100.0
                    if pct < 5:
                        return ""
                    if val >= 100:
                        val_str = f"{val:,.0f}"
                    elif val >= 10:
                        val_str = f"{val:,.1f}"
                    else:
                        val_str = f"{val:.2f}"
                    return f"{pct:.1f}%\n({val_str} {currency})"
                return my_autopct

            wedges, texts, autotexts = ax.pie(
                costs,
                labels=labels,
                autopct=make_autopct(costs),
                startangle=140,
                colors=colors[:len(plot_items)],
                wedgeprops=dict(width=0.6, edgecolor="#11111b", linewidth=2),
                pctdistance=0.75,
            )

            # Style text
            for text in texts:
                text.set_color("#cdd6f4")
                text.set_fontsize(11)
                text.set_weight("bold")

            for autotext in autotexts:
                autotext.set_color("#11111b")
                autotext.set_fontsize(9)
                autotext.set_weight("bold")

            ax.set_title(
                f"Структура годовых расходов ({currency})",
                color="#cdd6f4",
                fontsize=15,
                fontweight="bold",
                pad=20,
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
    Generates a bar chart showing monthly expense distribution across 12 months.
    Guarantees plt.close(fig).
    """
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(9, 5), dpi=120)

    try:
        fig.patch.set_facecolor("#1e1e2e")
        ax.set_facecolor("#1e1e2e")

        months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
        x = range(len(months))

        curr_symbols = {
            "RUB": "₽",
            "BYN": "Br",
            "USD": "$",
            "EUR": "€",
            "PLN": "zł",
        }
        curr_sym = curr_symbols.get(currency.upper().strip(), currency)

        bars = ax.bar(x, monthly_breakdown, color="#89b4fa", edgecolor="#b4befe", linewidth=1, width=0.6)

        ax.set_title(f"Прогнозируемые траты по месяцам ({curr_sym})", color="#cdd6f4", fontsize=14, fontweight="bold", pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(months, color="#cdd6f4", fontsize=10)
        ax.tick_params(axis="y", colors="#cdd6f4")
        ax.spines["bottom"].set_color("#45475a")
        ax.spines["left"].set_color("#45475a")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.2, color="#cdd6f4")

        # Values above bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f"{height:,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    color="#cdd6f4",
                    fontsize=8,
                    fontweight="bold",
                )

        plt.tight_layout()
        fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
        buf.seek(0)
    finally:
        plt.close(fig)

    return buf
