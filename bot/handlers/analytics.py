import logging
from collections import defaultdict
from typing import Dict, List, Any, Optional
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from database.requests import get_user_subscriptions
from services.chart_builder import build_expense_pie_chart
from services.currency import (
    CURRENCY_DISPLAY,
    get_exchange_rates,
    get_exchange_rates_sync,
    convert_currency,
    detect_default_currency,
)
from bot.keyboards.inline import get_analytics_currency_keyboard

logger = logging.getLogger(__name__)

router = Router(name="analytics")


def calculate_annual_metrics(subscriptions) -> Dict[str, Any]:
    """
    Computes annual forecast and top-3 services grouped by currency.
    Kept for backward compatibility.
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


def calculate_unified_metrics(
    subscriptions,
    target_currency: str = "BYN",
    rates: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Converts all active subscriptions to a single target currency (default BYN),
    calculates unified annual/monthly metrics and sorted service rankings.
    """
    target_curr = target_currency.upper().strip()
    current_rates = rates if rates is not None else get_exchange_rates_sync()

    converted_services = []
    currencies_used = set()

    for sub in subscriptions:
        if not getattr(sub, "is_active", True):
            continue

        orig_curr = getattr(sub, "currency", "RUB").upper().strip()
        currencies_used.add(orig_curr)

        orig_annual = (365.0 / sub.period_days) * sub.price
        converted_annual = convert_currency(
            amount=orig_annual,
            from_curr=orig_curr,
            to_curr=target_curr,
            rates=current_rates,
        )
        converted_monthly = converted_annual / 12.0

        converted_services.append({
            "name": sub.service_name,
            "annual_cost": converted_annual,
            "monthly_cost": converted_monthly,
            "original_price": sub.price,
            "original_currency": orig_curr,
            "period_days": sub.period_days,
            "is_converted": (orig_curr != target_curr),
        })

    sorted_services = sorted(converted_services, key=lambda x: x["annual_cost"], reverse=True)
    total_annual = sum(s["annual_cost"] for s in sorted_services)
    monthly_avg = total_annual / 12.0 if sorted_services else 0.0

    has_multiple_currencies = (
        len(currencies_used) > 1 or (len(currencies_used) == 1 and target_curr not in currencies_used)
    )

    return {
        "target_currency": target_curr,
        "total_annual": total_annual,
        "monthly_avg": monthly_avg,
        "services_count": len(sorted_services),
        "services": sorted_services,
        "top_services": sorted_services[:5],
        "currencies_used": sorted(list(currencies_used)),
        "has_multiple_currencies": has_multiple_currencies,
        "rates": current_rates,
    }


def format_analytics_caption(metrics: Dict[str, Any]) -> str:
    """
    Generates an Apple Card-style readable HTML report caption for the analytics photo.
    """
    target_curr = metrics["target_currency"]
    curr_sym = CURRENCY_DISPLAY.get(target_curr, target_curr)

    if target_curr == "BYN":
        header_curr = "Все расходы приведены к: Br (BYN)"
    else:
        header_curr = f"Все расходы приведены к: {curr_sym} ({target_curr})"

    text_blocks = [
        " <b>Аналитика регулярных расходов</b>",
        f"<i>{header_curr}</i>\n",
        f"• В год: <b>{metrics['total_annual']:,.0f} {curr_sym}</b>",
        f"• В месяц: <b>{metrics['monthly_avg']:,.0f} {curr_sym}</b>",
        f"• Подписок: <b>{metrics['services_count']}</b>\n",
    ]

    if metrics["services_count"] > 0:
        text_blocks.append("<b>Топ затратных сервисов:</b>")
        from collections import Counter
        name_counts = Counter(s.get("name", "") for s in metrics.get("services", []))

        for idx, s in enumerate(metrics["top_services"], 1):
            service_title = s['name']
            if name_counts[s['name']] > 1 and s.get("original_currency"):
                service_title = f"{s['name']} ({s['original_currency']})"

            text_blocks.append(
                f"{idx}. <b>{service_title}</b> — {s['annual_cost']:,.0f} {curr_sym}/год"
            )
        text_blocks.append("")

    if metrics["has_multiple_currencies"]:
        text_blocks.append("<i>Валюту можно переключить ниже:</i>")

    return "\n".join(text_blocks).strip()



from bot.utils.cleaner import send_clean_message, send_clean_photo


@router.message(Command("analytics"))
@router.message(F.text == "📊 Аналитика")
async def show_analytics(message: Message, session: AsyncSession) -> None:
    subs = await get_user_subscriptions(session, message.from_user.id, active_only=True)

    if not subs:
        await send_clean_message(
            message,
            " <b>Аналитика расходов</b>\n\n"
            "У вас пока нет активных подписок.\n"
            "Добавьте подписку, и здесь появится аналитика.",
            parse_mode="HTML",
        )
        return

    rates = await get_exchange_rates()
    target_curr = detect_default_currency(subs)
    metrics = calculate_unified_metrics(subs, target_currency=target_curr, rates=rates)

    # Generate pie chart with ALL converted services
    chart_buf = build_expense_pie_chart(metrics["services"], currency=target_curr)
    chart_bytes = chart_buf.read()
    input_file = BufferedInputFile(chart_bytes, filename="analytics.png")

    caption_text = format_analytics_caption(metrics)
    reply_markup = get_analytics_currency_keyboard(target_curr)

    await send_clean_photo(
        message,
        photo=input_file,
        caption=caption_text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("analytics_curr_"))
async def cb_switch_analytics_currency(callback: CallbackQuery, session: AsyncSession) -> None:
    target_curr = callback.data.split("_")[-1].upper()
    subs = await get_user_subscriptions(session, callback.from_user.id, active_only=True)

    if not subs:
        await callback.answer("Нет активных подписок для анализа", show_alert=True)
        return

    rates = await get_exchange_rates()
    metrics = calculate_unified_metrics(subs, target_currency=target_curr, rates=rates)

    chart_buf = build_expense_pie_chart(metrics["services"], currency=target_curr)
    chart_bytes = chart_buf.read()
    input_file = BufferedInputFile(chart_bytes, filename="analytics.png")

    caption_text = format_analytics_caption(metrics)
    reply_markup = get_analytics_currency_keyboard(target_curr)

    media = InputMediaPhoto(media=input_file, caption=caption_text, parse_mode="HTML")
    try:
        if callback.message:
            await callback.message.edit_media(media=media, reply_markup=reply_markup)
    except Exception as e:
        logger.debug(f"Ignored edit_media error (likely identical content): {e}")

    curr_sym = CURRENCY_DISPLAY.get(target_curr, target_curr)
    await callback.answer(f"Переключено на {curr_sym} ({target_curr})")

