import re
from datetime import datetime, date
from typing import Tuple, Optional
from urllib.parse import urlparse


def validate_service_name(text: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates service name.
    Returns (is_valid, cleaned_name, error_message).
    """
    cleaned = text.strip()
    if not cleaned:
        return False, None, "Название сервиса не может быть пустым. Пожалуйста, введите название."
    if len(cleaned) > 100:
        return False, None, "Слишком длинное название (максимум 100 символов). Попробуйте сократить."
    return True, cleaned, None


def validate_price(text: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Validates price input. Supports commas and spaces, e.g. '299,50' or '1 200'.
    Returns (is_valid, price_float, error_message).
    """
    cleaned = text.strip().replace(" ", "").replace(",", ".")
    try:
        val = float(cleaned)
    except ValueError:
        return False, None, "Некорректный формат суммы. Введите число (например, <code>299</code> или <code>850.50</code>)."

    if val <= 0:
        return False, None, "Сумма списания должна быть больше нуля."
    if val > 10_000_000:
        return False, None, "Слишком большая сумма (максимум 10 000 000). Проверьте введенное значение."

    return True, round(val, 2), None


def validate_period_days(text: str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validates interval in days.
    Returns (is_valid, days_int, error_message).
    """
    cleaned = text.strip()
    if not cleaned.isdigit():
        return False, None, "Интервал должен быть целым положительным числом дней (например, <code>30</code> или <code>14</code>)."

    val = int(cleaned)
    if val < 1:
        return False, None, "Интервал должен быть не менее 1 дня."
    if val > 3650:
        return False, None, "Интервал не может превышать 3650 дней (10 лет)."

    return True, val, None


def validate_billing_date(text: str) -> Tuple[bool, Optional[date], Optional[str]]:
    """
    Validates date in DD.MM.YYYY format.
    Returns (is_valid, date_obj, error_message).
    """
    cleaned = text.strip()
    try:
        parsed_dt = datetime.strptime(cleaned, "%d.%m.%Y").date()
    except ValueError:
        return (
            False,
            None,
            "Неверный формат даты. Пожалуйста, укажите дату в формате <code>ДД.ММ.ГГГГ</code> (например, <code>25.12.2026</code>).",
        )

    # Allow dates starting from today or reasonable past (e.g. within last 30 days is acceptable for setting up)
    if parsed_dt.year < 2000 or parsed_dt.year > 2100:
        return False, None, "Год должен быть в диапазоне от 2000 до 2100."

    return True, parsed_dt, None


def validate_cancel_url(text: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates URL for canceling subscription.
    Must start with http:// or https:// and have valid domain.
    """
    cleaned = text.strip()
    parsed = urlparse(cleaned)
    if not (parsed.scheme in ("http", "https") and parsed.netloc):
        return (
            False,
            None,
            "Некорректная ссылка! Ссылка должна начинаться с <code>https://</code> или <code>http://</code> (например: <code>https://plus.yandex.ru</code>).",
        )
    return True, cleaned, None
