import time
import logging
from typing import Dict, Optional, List, Any
import aiohttp

logger = logging.getLogger(__name__)

CURRENCY_DISPLAY = {
    "BYN": "Br",
    "RUB": "₽",
    "USD": "$",
    "EUR": "€",
    "PLN": "zł",
}

DEFAULT_RATES_TO_USD: Dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "RUB": 85.0,
    "BYN": 3.05,
    "PLN": 3.90,
}

_cached_rates: Dict[str, float] = DEFAULT_RATES_TO_USD.copy()
_last_fetch_time: float = 0.0
CACHE_TTL_SECONDS: float = 12 * 3600.0  # 12 hours


async def get_exchange_rates() -> Dict[str, float]:
    """
    Fetches real-time exchange rates relative to USD from open.er-api.com.
    Uses in-memory caching with 12h TTL and falls back to default rates upon failure.
    """
    global _cached_rates, _last_fetch_time
    now = time.time()

    if _last_fetch_time > 0 and (now - _last_fetch_time) < CACHE_TTL_SECONDS:
        return _cached_rates.copy()

    url = "https://open.er-api.com/v6/latest/USD"
    try:
        timeout = aiohttp.ClientTimeout(total=4.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    rates = data.get("rates", {})
                    if rates and "RUB" in rates:
                        # Ensure our primary currencies are present
                        merged = DEFAULT_RATES_TO_USD.copy()
                        for curr in DEFAULT_RATES_TO_USD:
                            if curr in rates:
                                merged[curr] = float(rates[curr])
                        _cached_rates = merged
                        _last_fetch_time = now
                        logger.info("Successfully fetched live exchange rates from open.er-api.com")
                        return _cached_rates.copy()
    except Exception as e:
        logger.warning(f"Failed to fetch live exchange rates: {e}. Using cached/fallback rates.")

    return _cached_rates.copy()


def get_exchange_rates_sync() -> Dict[str, float]:
    """
    Synchronous access to current cached or fallback exchange rates.
    """
    return _cached_rates.copy()


def convert_currency(
    amount: float,
    from_curr: str,
    to_curr: str,
    rates: Optional[Dict[str, float]] = None,
) -> float:
    """
    Converts amount from from_curr to to_curr using given rates (or cached rates).
    Rates are assumed to be units of currency per 1 USD.
    """
    from_curr = from_curr.upper().strip()
    to_curr = to_curr.upper().strip()

    if from_curr == to_curr:
        return float(amount)

    current_rates = rates if rates is not None else get_exchange_rates_sync()

    rate_from = current_rates.get(from_curr, DEFAULT_RATES_TO_USD.get(from_curr, 1.0))
    rate_to = current_rates.get(to_curr, DEFAULT_RATES_TO_USD.get(to_curr, 1.0))

    if rate_from <= 0:
        rate_from = 1.0
    if rate_to <= 0:
        rate_to = 1.0

    # Convert to USD then to target currency
    amount_in_usd = amount / rate_from
    return amount_in_usd * rate_to


DEFAULT_BASE_CURRENCY = "BYN"


def detect_default_currency(subscriptions: Optional[List[Any]] = None) -> str:
    """
    Returns the base currency for conversion, which defaults to BYN (Belarusian Rubles).
    """
    return DEFAULT_BASE_CURRENCY

