from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models import Subscription

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


def get_period_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📅 Ежемесячно (30 дней)", callback_data="period_30")],
        [InlineKeyboardButton(text="📆 Ежегодно (365 дней)", callback_data="period_365")],
        [InlineKeyboardButton(text="⚙️ Свой интервал (в днях)", callback_data="period_custom")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_skip_cancel_url_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="➡️ Пропустить", callback_data="skip_cancel_url")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subscriptions_list_keyboard(subscriptions: List[Subscription]) -> InlineKeyboardMarkup:
    buttons = []
    for sub in subscriptions:
        status_icon = "🟢" if sub.is_active else "⏸"
        currency_map = {"BYN": "Br", "RUB": "₽", "USD": "$", "EUR": "€", "PLN": "zł"}
        currency_disp = currency_map.get(sub.currency, sub.currency)
        price_disp = f"{sub.price:g}" if sub.price.is_integer() else f"{sub.price:.2f}"
        btn_text = f"{status_icon} {sub.service_name} • {price_disp} {currency_disp}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"view_sub_{sub.id}")])

    buttons.append([InlineKeyboardButton(text="➕ Добавить подписку", callback_data="add_new_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subscription_card_keyboard(
    sub_id: int,
    is_active: bool,
    cancel_url: Optional[str] = None,
) -> InlineKeyboardMarkup:
    buttons = []

    if cancel_url:
        buttons.append([InlineKeyboardButton(text="🔗 Страница отмены сервиса", url=cancel_url)])

    toggle_text = "⏸ Приостановить" if is_active else "▶️ Активировать"
    buttons.append([
        InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_sub_{sub_id}"),
        InlineKeyboardButton(text=toggle_text, callback_data=f"toggle_sub_{sub_id}"),
    ])
    buttons.append([
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_sub_{sub_id}"),
        InlineKeyboardButton(text="⬅️ К списку", callback_data="list_subs"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_delete_confirm_keyboard(sub_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="⚠️ Да, удалить", callback_data=f"confirm_del_{sub_id}"),
            InlineKeyboardButton(text="Отмена", callback_data=f"view_sub_{sub_id}"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_edit_fields_keyboard(sub_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📝 Название", callback_data=f"edit_field_{sub_id}_name"),
            InlineKeyboardButton(text="💰 Сумма", callback_data=f"edit_field_{sub_id}_price"),
        ],
        [
            InlineKeyboardButton(text="💱 Валюта", callback_data=f"edit_field_{sub_id}_currency"),
            InlineKeyboardButton(text="⏱ Период", callback_data=f"edit_field_{sub_id}_period"),
        ],
        [
            InlineKeyboardButton(text="📅 Дата списания", callback_data=f"edit_field_{sub_id}_date"),
            InlineKeyboardButton(text="🔗 Ссылка отмены", callback_data=f"edit_field_{sub_id}_url"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад к карточке", callback_data=f"view_sub_{sub_id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_edit_currency_keyboard(sub_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🇧🇾 BYN (Br)", callback_data=f"set_curr_{sub_id}_BYN"),
            InlineKeyboardButton(text="🇷🇺 RUB (₽)", callback_data=f"set_curr_{sub_id}_RUB"),
        ],
        [
            InlineKeyboardButton(text="🇺🇸 USD ($)", callback_data=f"set_curr_{sub_id}_USD"),
            InlineKeyboardButton(text="🇵🇱 PLN (zł)", callback_data=f"set_curr_{sub_id}_PLN"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Отмена", callback_data=f"view_sub_{sub_id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_analytics_currency_keyboard(active_currency: str) -> InlineKeyboardMarkup:
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
    return InlineKeyboardMarkup(inline_keyboard=buttons)

