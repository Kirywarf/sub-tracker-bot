import re
from datetime import datetime, date
from typing import Tuple, Optional
from urllib.parse import urlparse
from bot.locales import get_text


def validate_service_name(text: str, lang: str = "ru") -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates service name.
    Returns (is_valid, cleaned_name, error_message).
    """
    cleaned = text.strip()
    if not cleaned:
        return False, None, get_text("val_err_name_empty", lang)
    if len(cleaned) > 100:
        return False, None, get_text("val_err_name_toolong", lang)
    return True, cleaned, None


def validate_price(text: str, lang: str = "ru") -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Validates price input. Supports commas and spaces, e.g. '299,50' or '1 200'.
    Returns (is_valid, price_float, error_message).
    """
    cleaned = text.strip().replace(" ", "").replace(",", ".")
    try:
        val = float(cleaned)
    except ValueError:
        return False, None, get_text("val_err_price_invalid", lang)

    if val <= 0:
        return False, None, get_text("val_err_price_positive", lang)
    if val > 10_000_000:
        return False, None, get_text("val_err_price_toobig", lang)

    return True, round(val, 2), None


def validate_period_days(text: str, lang: str = "ru") -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validates interval in days.
    Returns (is_valid, days_int, error_message).
    """
    cleaned = text.strip()
    if not cleaned.isdigit():
        return False, None, get_text("val_err_period_digits", lang)

    val = int(cleaned)
    if val < 1:
        return False, None, get_text("val_err_period_min", lang)
    if val > 3650:
        return False, None, get_text("val_err_period_max", lang)

    return True, val, None


def validate_billing_date(text: str, lang: str = "ru") -> Tuple[bool, Optional[date], Optional[str]]:
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
            get_text("val_err_date_format", lang),
        )

    # Allow dates starting from reasonable years
    if parsed_dt.year < 2000 or parsed_dt.year > 2100:
        return False, None, get_text("val_err_date_range", lang)

    return True, parsed_dt, None


def validate_cancel_url(text: str, lang: str = "ru") -> Tuple[bool, Optional[str], Optional[str]]:
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
            get_text("val_err_url", lang),
        )
    return True, cleaned, None
