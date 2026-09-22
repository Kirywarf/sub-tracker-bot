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


from bot.locales import get_text


def format_analytics_caption(metrics: Dict[str, Any], lang: str = "ru") -> str:
    """
    Generates an Apple Card-style readable HTML report caption for the analytics photo.
    """
    target_curr = metrics["target_currency"]
    curr_sym = CURRENCY_DISPLAY.get(target_curr, target_curr)

    if target_curr == "BYN":
        header_curr = get_text("analytics_all_converted", lang, curr="Br (BYN)")
    else:
        header_curr = get_text("analytics_all_converted", lang, curr=f"{curr_sym} ({target_curr})")

    year_str = f"{metrics['total_annual']:,.0f}"
    month_str = f"{metrics['monthly_avg']:,.0f}"

    text_blocks = [
        get_text("analytics_title", lang),
        f"<i>{header_curr}</i>\n",
        get_text("analytics_in_year", lang, amount=year_str, curr=curr_sym),
        get_text("analytics_in_month", lang, amount=month_str, curr=curr_sym),
        get_text("analytics_subs_count", lang, count=metrics["services_count"]) + "\n",
    ]

    if metrics["services_count"] > 0:
        text_blocks.append(get_text("analytics_top_title", lang))
        from collections import Counter
        name_counts = Counter(s.get("name", "") for s in metrics.get("services", []))
        yr_short = get_text("analytics_year_short", lang)

        for idx, s in enumerate(metrics["top_services"], 1):
            service_title = s['name']
            if name_counts[s['name']] > 1 and s.get("original_currency"):
                service_title = f"{s['name']} ({s['original_currency']})"

            text_blocks.append(
                f"{idx}. <b>{service_title}</b> — {s['annual_cost']:,.0f} {curr_sym}{yr_short}"
            )
        text_blocks.append("")

    if metrics["has_multiple_currencies"]:
        text_blocks.append(get_text("analytics_switch_hint", lang))

    return "\n".join(text_blocks).strip()



from bot.utils.cleaner import send_clean_message, send_clean_photo


@router.message(Command("analytics"))
@router.message(F.text.in_({"📊 Аналитика", "📊 Аналітыка", "📊 Analytics", "📊 Analityka"}))
async def show_analytics(message: Message, session: AsyncSession, user_lang: str = "ru") -> None:
    subs = await get_user_subscriptions(session, message.from_user.id, active_only=True)

    if not subs:
        await send_clean_message(
            message,
            get_text("analytics_empty", user_lang),
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

    caption_text = format_analytics_caption(metrics, lang=user_lang)
    reply_markup = get_analytics_currency_keyboard(target_curr, user_id=message.from_user.id, lang=user_lang)

    await send_clean_photo(
        message,
        photo=input_file,
        caption=caption_text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("analytics_curr_"))
async def cb_switch_analytics_currency(callback: CallbackQuery, session: AsyncSession, user_lang: str = "ru") -> None:
    target_curr = callback.data.split("_")[-1].upper()
    subs = await get_user_subscriptions(session, callback.from_user.id, active_only=True)

    if not subs:
        await callback.answer(get_text("analytics_no_active_alert", user_lang), show_alert=True)
        return

    rates = await get_exchange_rates()
    metrics = calculate_unified_metrics(subs, target_currency=target_curr, rates=rates)

    chart_buf = build_expense_pie_chart(metrics["services"], currency=target_curr)
    chart_bytes = chart_buf.read()
    input_file = BufferedInputFile(chart_bytes, filename="analytics.png")

    caption_text = format_analytics_caption(metrics, lang=user_lang)
    reply_markup = get_analytics_currency_keyboard(target_curr, user_id=callback.from_user.id, lang=user_lang)

    media = InputMediaPhoto(media=input_file, caption=caption_text, parse_mode="HTML")
    try:
        if callback.message:
            await callback.message.edit_media(media=media, reply_markup=reply_markup)
    except Exception as e:
        logger.debug(f"Ignored edit_media error (likely identical content): {e}")

    curr_sym = CURRENCY_DISPLAY.get(target_curr, target_curr)
    await callback.answer(get_text("analytics_switched_alert", user_lang, curr=f"{curr_sym} ({target_curr})"))

