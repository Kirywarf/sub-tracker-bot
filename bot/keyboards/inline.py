from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from database.models import Subscription
from config import settings
from bot.locales import get_text, normalize_language
from bot.keyboards.reply import get_webapp_url

CURRENCY_LABELS = {
    "BYN": "🇧🇾 BYN (Br)",
    "RUB": "🇷🇺 RUB (₽)",
    "USD": "🇺🇸 USD ($)",
    "PLN": "🇵🇱 PLN (zł)",
}


def get_currency_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🇧🇾 BYN (Br)", callback_data="curr_BYN"),
            InlineKeyboardButton(text="🇷🇺 RUB (₽)", callback_data="curr_RUB"),
        ],
        [
            InlineKeyboardButton(text="🇺🇸 USD ($)", callback_data="curr_USD"),
            InlineKeyboardButton(text="🇵🇱 PLN (zł)", callback_data="curr_PLN"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_period_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=get_text("period_monthly", lang), callback_data="period_30")],
        [InlineKeyboardButton(text=get_text("period_annual", lang), callback_data="period_365")],
        [InlineKeyboardButton(text=get_text("period_custom", lang), callback_data="period_custom")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_skip_cancel_url_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=get_text("btn_skip", lang), callback_data="skip_cancel_url")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subscriptions_list_keyboard(
    subscriptions: List[Subscription],
    user_id: Optional[int] = None,
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    buttons = []
    for sub in subscriptions:
        status_icon = "●" if sub.is_active else "○"
        currency_map = {"BYN": "Br", "RUB": "₽", "USD": "$", "EUR": "€", "PLN": "zł"}
        currency_disp = currency_map.get(sub.currency, sub.currency)
        price_disp = f"{sub.price:g}" if sub.price.is_integer() else f"{sub.price:.2f}"
        btn_text = f"{status_icon} {sub.service_name} · {price_disp} {currency_disp}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"view_sub_{sub.id}")])

    buttons.append([InlineKeyboardButton(text=get_text("btn_add_sub", lang), callback_data="add_new_sub")])

    if getattr(settings, "WEBAPP_URL", None):
        url = get_webapp_url(user_id=user_id, lang=lang)
        buttons.append([InlineKeyboardButton(text=get_text("btn_open_stoppay_app", lang), web_app=WebAppInfo(url=url))])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subscription_card_keyboard(
    sub_id: int,
    is_active: bool,
    cancel_url: Optional[str] = None,
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    buttons = []

    if cancel_url:
        buttons.append([InlineKeyboardButton(text=get_text("btn_cancel_url_page", lang), url=cancel_url)])

    toggle_text = get_text("btn_pause", lang) if is_active else get_text("btn_activate", lang)
    buttons.append([
        InlineKeyboardButton(text=get_text("btn_renew", lang), callback_data=f"renew_sub_{sub_id}"),
        InlineKeyboardButton(text=toggle_text, callback_data=f"toggle_sub_{sub_id}"),
    ])
    buttons.append([
        InlineKeyboardButton(text=get_text("btn_edit", lang), callback_data=f"edit_sub_{sub_id}"),
        InlineKeyboardButton(text=get_text("btn_delete", lang), callback_data=f"delete_sub_{sub_id}"),
    ])
    buttons.append([
        InlineKeyboardButton(text=get_text("btn_back_to_list", lang), callback_data="list_subs"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_delete_confirm_keyboard(sub_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=get_text("btn_confirm_delete", lang), callback_data=f"confirm_del_{sub_id}"),
            InlineKeyboardButton(text=get_text("btn_cancel_modal", lang), callback_data=f"view_sub_{sub_id}"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_edit_fields_keyboard(sub_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=get_text("field_name", lang), callback_data=f"edit_field_{sub_id}_name"),
            InlineKeyboardButton(text=get_text("field_price", lang), callback_data=f"edit_field_{sub_id}_price"),
        ],
        [
            InlineKeyboardButton(text=get_text("field_currency", lang), callback_data=f"edit_field_{sub_id}_currency"),
            InlineKeyboardButton(text=get_text("field_period", lang), callback_data=f"edit_field_{sub_id}_period"),
        ],
        [
            InlineKeyboardButton(text=get_text("field_date", lang), callback_data=f"edit_field_{sub_id}_date"),
            InlineKeyboardButton(text=get_text("field_url", lang), callback_data=f"edit_field_{sub_id}_url"),
        ],
        [
            InlineKeyboardButton(text=get_text("btn_back_to_card", lang), callback_data=f"view_sub_{sub_id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_edit_currency_keyboard(sub_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="BYN (Br)", callback_data=f"set_curr_{sub_id}_BYN"),
            InlineKeyboardButton(text="RUB (₽)", callback_data=f"set_curr_{sub_id}_RUB"),
        ],
        [
            InlineKeyboardButton(text="USD ($)", callback_data=f"set_curr_{sub_id}_USD"),
            InlineKeyboardButton(text="PLN (zł)", callback_data=f"set_curr_{sub_id}_PLN"),
        ],
        [
            InlineKeyboardButton(text=get_text("btn_cancel_modal", lang), callback_data=f"view_sub_{sub_id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_analytics_currency_keyboard(
    active_currency: str,
    user_id: Optional[int] = None,
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    active = active_currency.upper().strip()
    currencies = [
        ("BYN", "🇧🇾 BYN"),
        ("RUB", "🇷🇺 RUB"),
        ("USD", "🇺🇸 USD"),
        ("PLN", "🇵🇱 PLN"),
    ]
    buttons = []
    row = []
    for code, label in currencies:
        btn_text = f"• {label} •" if code == active else label
        row.append(InlineKeyboardButton(text=btn_text, callback_data=f"analytics_curr_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    if getattr(settings, "WEBAPP_URL", None):
        url = get_webapp_url(user_id=user_id, lang=lang)
        buttons.append([InlineKeyboardButton(text=get_text("analytics_btn_interactive", lang), web_app=WebAppInfo(url=url))])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
