import logging
from datetime import date, timedelta
from typing import Optional
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramAPIError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import settings
from database.requests import get_subscriptions_due_for_reminder
from bot.locales import get_text

logger = logging.getLogger(__name__)

CURRENCY_SYMBOLS = {
    "RUB": "₽",
    "BYN": "Br",
    "USD": "$",
    "EUR": "€",
    "PLN": "zł",
}


def build_reminder_keyboard(sub_id: int, cancel_url: Optional[str], lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = []
    if cancel_url:
        buttons.append([InlineKeyboardButton(text=get_text("btn_reminder_cancel", lang), url=cancel_url)])
    buttons.append([InlineKeyboardButton(text=get_text("btn_mark_paid", lang), callback_data=f"paid_{sub_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def check_and_send_reminders(bot: Bot, session_factory: async_sessionmaker[AsyncSession]) -> int:
    """
    Checks for subscriptions whose next_billing_date is tomorrow (current_date + 1 day),
    and sends notification messages to users in their preferred language.
    Returns the count of successfully sent reminders.
    """
    tomorrow = date.today() + timedelta(days=1)
    sent_count = 0

    async with session_factory() as session:
        due_subscriptions = await get_subscriptions_due_for_reminder(session, tomorrow)

    logger.info(f"Found {len(due_subscriptions)} subscriptions due for reminder on {tomorrow}")

    for sub in due_subscriptions:
        curr_symbol = CURRENCY_SYMBOLS.get(sub.currency, sub.currency)
        price_display = f"{sub.price:g} {curr_symbol}" if sub.price.is_integer() else f"{sub.price:.2f} {curr_symbol}"

        user_lang = getattr(sub.user, "language", "ru") if getattr(sub, "user", None) else "ru"
        text = get_text("reminder_alert", user_lang, price=price_display, service=sub.service_name)
        kb = build_reminder_keyboard(sub.id, sub.cancel_url, lang=user_lang)

        try:
            await bot.send_message(
                chat_id=sub.user_id,
                text=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
            sent_count += 1
            logger.info(f"Sent reminder for subscription #{sub.id} to user {sub.user_id} in '{user_lang}'")
        except TelegramAPIError as e:
            logger.warning(f"Failed to send reminder to user {sub.user_id} for sub #{sub.id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending reminder: {e}", exc_info=True)

    return sent_count


def setup_scheduler(bot: Bot, session_factory: async_sessionmaker[AsyncSession]) -> AsyncIOScheduler:
    """
    Configures and returns AsyncIOScheduler for daily reminders.
    """
    scheduler = AsyncIOScheduler()

    # Daily check at configured hour and minute
    scheduler.add_job(
        check_and_send_reminders,
        trigger=CronTrigger(hour=settings.REMINDER_HOUR, minute=settings.REMINDER_MINUTE),
        args=[bot, session_factory],
        id="daily_subscription_reminders",
        name="Daily Subscription Reminders Check",
        replace_existing=True,
    )

    return scheduler
