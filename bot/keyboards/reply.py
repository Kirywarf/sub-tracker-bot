from typing import Optional
from urllib.parse import quote
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import settings
from bot.locales import get_text, normalize_language


def get_webapp_url(user_id: Optional[int] = None, first_name: Optional[str] = None, lang: str = "ru") -> str:
    url = getattr(settings, "WEBAPP_URL", "") or "https://sub-tracker-bot.onrender.com"
    url = url.rstrip("/")
    params = []
    if user_id:
        params.append(f"user_id={user_id}")
    if first_name:
        params.append(f"name={quote(first_name)}")
    if lang:
        params.append(f"lang={normalize_language(lang)}")
    if params:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{'&'.join(params)}"
    return url


def get_main_menu_keyboard(user_id: Optional[int] = None, first_name: Optional[str] = None, lang: str = "ru") -> ReplyKeyboardMarkup:
    url = get_webapp_url(user_id=user_id, first_name=first_name, lang=lang)
    app_btn_text = get_text("btn_open_app", lang)
    help_btn_text = get_text("btn_help", lang)
    lang_btn_text = get_text("btn_language", lang)
    kb = [
        [KeyboardButton(text=app_btn_text, web_app=WebAppInfo(url=url))],
        [KeyboardButton(text=help_btn_text), KeyboardButton(text=lang_btn_text)],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_cancel_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    cancel_text = get_text("btn_cancel", lang)
    kb = [
        [KeyboardButton(text=cancel_text)],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
