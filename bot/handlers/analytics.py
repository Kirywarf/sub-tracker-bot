from collections import defaultdict
from typing import Dict, List, Any
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from database.requests import get_user_subscriptions
from services.chart_builder import build_expense_pie_chart

router = Router(name="analytics")

CURRENCY_DISPLAY = {
    "RUB": "₽",
    "BYN": "Br",
    "USD": "$",
    "EUR": "€",
    "PLN": "zł",
}


def calculate_annual_metrics(subscriptions) -> Dict[str, Any]:
    """
    Computes annual forecast and top-3 services grouped by currency.
    """
    currencies_data = defaultdict(lambda: {"total_annual": 0.0, "services": []})

    for sub in subscriptions:
        if not sub.is_active:
            continue
        annual_cost = (365.0 / sub.period_days) * sub.price
        currencies_data[sub.currency]["total_annual"] += annual_cost
        currencies_data[sub.currency]["services"].append({
            "name": sub.service_name,
            "annual_cost": annual_cost,
            "price": sub.price,
            "period_days": sub.period_days,
        })

    result = {}
    for curr, data in currencies_data.items():
        sorted_services = sorted(data["services"], key=lambda x: x["annual_cost"], reverse=True)
        result[curr] = {
            "total_annual": data["total_annual"],
            "monthly_avg": data["total_annual"] / 12.0,
            "services_count": len(sorted_services),
            "top_3": sorted_services[:3],
            "all_services": sorted_services,
        }

    return result


@router.message(Command("analytics"))
@router.message(F.text == "📊 Аналитика")
async def show_analytics(message: Message, session: AsyncSession) -> None:
    subs = await get_user_subscriptions(session, message.from_user.id, active_only=True)

    if not subs:
        await message.answer(
            "📊 <b>Аналитика расходов</b>\n\n"
            "У вас пока нет активных подписок для анализа.\n"
            "Добавьте подписки через меню «➕ Добавить подписку», и здесь появится полный прогноз расходов с диаграммой!",
            parse_mode="HTML",
        )
        return

    metrics = calculate_annual_metrics(subs)

    # Pick dominant currency for chart
    dominant_curr = max(metrics.keys(), key=lambda c: metrics[c]["total_annual"])
    dominant_data = metrics[dominant_curr]

    # Generate pie chart
    chart_buf = build_expense_pie_chart(dominant_data["all_services"], currency=dominant_curr)
    chart_bytes = chart_buf.read()
    input_file = BufferedInputFile(chart_bytes, filename="analytics.png")

    # Format text report
    text_blocks = ["📊 <b>Аналитика регулярных расходов</b>\n"]

    for curr, data in metrics.items():
        curr_sym = CURRENCY_DISPLAY.get(curr, curr)
        text_blocks.append(
            f"<b>Валюта: {curr_sym} ({curr})</b>\n"
            f"• Прогноз на год: <b>{data['total_annual']:,.2f} {curr_sym}</b>\n"
            f"• Средняя нагрузка в месяц: <b>{data['monthly_avg']:,.2f} {curr_sym}</b>\n"
            f"• Активных сервисов: <b>{data['services_count']}</b>\n"
        )

        text_blocks.append("🏆 <b>Топ затратных сервисов в год:</b>")
        for idx, s in enumerate(data["top_3"], 1):
            text_blocks.append(
                f"  {idx}. <b>{s['name']}</b> — {s['annual_cost']:,.0f} {curr_sym}/год "
                f"({s['price']:g} {curr_sym} / {s['period_days']} дн.)"
            )
        text_blocks.append("")

    caption_text = "\n".join(text_blocks).strip()

    await message.answer_photo(
        photo=input_file,
        caption=caption_text,
        parse_mode="HTML",
    )
