from typing import Optional
from urllib.parse import quote
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import settings


def get_webapp_url(user_id: Optional[int] = None, first_name: Optional[str] = None) -> str:
    url = getattr(settings, "WEBAPP_URL", "") or "https://sub-tracker-bot.onrender.com"
    url = url.rstrip("/")
    params = []
    if user_id:
        params.append(f"user_id={user_id}")
    if first_name:
        params.append(f"name={quote(first_name)}")
    if params:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{'&'.join(params)}"
    return url


def get_main_menu_keyboard(user_id: Optional[int] = None, first_name: Optional[str] = None) -> ReplyKeyboardMarkup:
    url = get_webapp_url(user_id=user_id, first_name=first_name)
    kb = [
        [KeyboardButton(text=" Открыть StopPay", web_app=WebAppInfo(url=url))],
        [KeyboardButton(text="ℹ️ Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="❌ Отмена")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
