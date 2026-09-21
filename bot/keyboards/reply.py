from typing import Optional
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import settings


def get_main_menu_keyboard(user_id: Optional[int] = None) -> ReplyKeyboardMarkup:
    kb = []
    if getattr(settings, "WEBAPP_URL", None):
        url = settings.WEBAPP_URL
        if user_id:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}user_id={user_id}"
        kb.append([KeyboardButton(text=" Открыть StopPay", web_app=WebAppInfo(url=url))])
    kb.extend([
        [KeyboardButton(text="➕ Добавить подписку"), KeyboardButton(text="📋 Мои подписки")],
        [KeyboardButton(text="📊 Аналитика"), KeyboardButton(text="ℹ️ Помощь")],
    ])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="❌ Отмена")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
