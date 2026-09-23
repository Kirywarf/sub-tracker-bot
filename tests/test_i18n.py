import pytest
from unittest.mock import AsyncMock
from aiogram.types import Message, CallbackQuery, User as TgUser, Chat
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey

from bot.locales import get_text, normalize_language, get_language_keyboard, SUPPORTED_LANGUAGES
from bot.keyboards.reply import get_main_menu_keyboard, get_cancel_keyboard, get_webapp_url
from bot.keyboards.inline import get_subscription_card_keyboard
from bot.utils.validators import (
    validate_service_name,
    validate_price,
    validate_period_days,
    validate_billing_date,
    validate_cancel_url,
)
from database.requests import (
    get_or_create_user,
    get_user_language,
    update_user_language,
)
from bot.handlers.common import cmd_start, cmd_language, cb_set_language
from bot.handlers.subscriptions import format_sub_card
from bot.handlers.analytics import format_analytics_caption
from services.scheduler import build_reminder_keyboard
from database.models import Subscription
from datetime import date, timedelta


def make_mock_message(text: str, user_id: int = 12345) -> Message:
    msg = AsyncMock(spec=Message)
    msg.text = text
    msg.from_user = TgUser(id=user_id, is_bot=False, first_name="Test", username="testuser")
    msg.chat = Chat(id=user_id, type="private")
    msg.answer = AsyncMock()
    msg.bot = AsyncMock()
    msg.bot.set_chat_menu_button = AsyncMock()
    return msg


def make_mock_callback_query(data: str, user_id: int = 12345) -> CallbackQuery:
    cb = AsyncMock(spec=CallbackQuery)
    cb.data = data
    cb.from_user = TgUser(id=user_id, is_bot=False, first_name="Test", username="testuser")
    msg = AsyncMock(spec=Message)
    msg.chat = Chat(id=user_id, type="private")
    msg.edit_text = AsyncMock()
    msg.answer = AsyncMock()
    cb.message = msg
    cb.bot = AsyncMock()
    cb.bot.set_chat_menu_button = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def fsm_context():
    storage = MemoryStorage()
    key = StorageKey(bot_id=1, chat_id=12345, user_id=12345)
    return FSMContext(storage=storage, key=key)


def test_normalize_language():
    assert normalize_language("ru") == "ru"
    assert normalize_language("RU") == "ru"
    assert normalize_language("ru-RU") == "ru"
    assert normalize_language("be") == "be"
    assert normalize_language("be-BY") == "be"
    assert normalize_language("en") == "en"
    assert normalize_language("en-US") == "en"
    assert normalize_language("pl") == "pl"
    assert normalize_language("pl-PL") == "pl"
    assert normalize_language("fr") == "ru"
    assert normalize_language(None) == "ru"


def test_get_text():
    # Russian
    assert "Привет" in get_text("start_welcome", "ru")
    # Belarusian
    assert "Прывітанне" in get_text("start_welcome", "be")
    # English
    assert "Hello" in get_text("start_welcome", "en")
    # Polish
    assert "Cześć" in get_text("start_welcome", "pl")

    # Formatting
    formatted = get_text("card_amount_line", "en", price="9.99", curr="USD", days=30)
    assert "9.99 USD" in formatted
    assert "30 d." in formatted

    # Fallback to RU
    assert get_text("non_existent_key_xyz", "en") == "[non_existent_key_xyz]"


def test_keyboards_i18n():
    kb_ru = get_main_menu_keyboard(lang="ru")
    assert kb_ru.keyboard[0][0].text == " Открыть StopPay"
    assert kb_ru.keyboard[1][0].text == "ℹ️ Помощь"
    assert kb_ru.keyboard[1][1].text == "🌐 Язык"

    kb_be = get_main_menu_keyboard(lang="be")
    assert kb_be.keyboard[0][0].text == " Адкрыць StopPay"
    assert kb_be.keyboard[1][0].text == "ℹ️ Даведка"
    assert kb_be.keyboard[1][1].text == "🌐 Мова"

    kb_en = get_main_menu_keyboard(lang="en")
    assert kb_en.keyboard[0][0].text == " Open StopPay"
    assert kb_en.keyboard[1][0].text == "ℹ️ Help"
    assert kb_en.keyboard[1][1].text == "🌐 Language"

    kb_pl = get_main_menu_keyboard(lang="pl")
    assert kb_pl.keyboard[0][0].text == " Otwórz StopPay"
    assert kb_pl.keyboard[1][0].text == "ℹ️ Pomoc"
    assert kb_pl.keyboard[1][1].text == "🌐 Język"

    # Cancel keyboards
    assert get_cancel_keyboard("ru").keyboard[0][0].text == "❌ Отмена"
    assert get_cancel_keyboard("be").keyboard[0][0].text == "❌ Адмена"
    assert get_cancel_keyboard("en").keyboard[0][0].text == "❌ Cancel"
    assert get_cancel_keyboard("pl").keyboard[0][0].text == "❌ Anuluj"

    # Language selection keyboard
    lang_kb = get_language_keyboard(current_lang="en")
    buttons = [btn.text for row in lang_kb.inline_keyboard for btn in row]
    assert any("Русский" in b for b in buttons)
    assert any("Беларуская" in b for b in buttons)
    assert any("English" in b and "•" in b for b in buttons)
    assert any("Polski" in b for b in buttons)

    # Webapp URL
    url = get_webapp_url(user_id=123, first_name="Alex", lang="pl")
    assert "lang=pl" in url
    assert "user_id=123" in url


def test_validators_i18n():
    # Service name
    valid, _, err = validate_service_name("", lang="en")
    assert not valid
    assert "cannot be empty" in err

    valid, _, err = validate_service_name("", lang="be")
    assert not valid
    assert "не можа быць пустой" in err

    # Price
    valid, _, err = validate_price("-10", lang="pl")
    assert not valid
    assert "musi być większa od zera" in err

    valid, _, err2 = validate_price("abc", lang="pl")
    assert not valid
    assert "Nieprawidłowy format kwoty" in err2

    # Period
    valid, _, err = validate_period_days("0", lang="en")
    assert not valid
    assert "must be at least 1 day" in err

    # Billing date
    valid, _, err = validate_billing_date("invalid-date", lang="pl")
    assert not valid
    assert "Nieprawidłowy format daty" in err

    # Cancel URL
    valid, _, err = validate_cancel_url("ftp://example.com", lang="be")
    assert not valid
    assert "https://" in err
    assert "спасылка" in err.lower()


@pytest.mark.asyncio
async def test_database_user_language(test_session):
    user = await get_or_create_user(
        session=test_session,
        telegram_id=8888,
        username="languser",
        language="be",
    )
    assert user.language == "be"

    lang = await get_user_language(test_session, 8888)
    assert lang == "be"

    updated = await update_user_language(test_session, 8888, "pl")
    assert updated.language == "pl"

    lang_after = await get_user_language(test_session, 8888)
    assert lang_after == "pl"


@pytest.mark.asyncio
async def test_cmd_start_i18n(fsm_context):
    msg = make_mock_message("/start")
    await cmd_start(msg, fsm_context, user_lang="en")
    msg.answer.assert_called_once()
    assert "Apple-style subscription tracker" in msg.answer.call_args[0][0]

    msg_pl = make_mock_message("/start")
    await cmd_start(msg_pl, fsm_context, user_lang="pl")
    assert "kontrola Twoich subskrypcji w stylu Apple" in msg_pl.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_cmd_language_and_callback(test_session):
    await get_or_create_user(
        session=test_session,
        telegram_id=12345,
        username="testuser",
        language="ru",
    )

    msg = make_mock_message("/language")
    await cmd_language(msg, user_lang="ru")
    msg.answer.assert_called_once()
    assert "Выберите язык" in msg.answer.call_args[0][0]

    cb = make_mock_callback_query("set_lang_be", user_id=12345)
    await cb_set_language(cb, session=test_session)
    cb.answer.assert_called_once()
    cb.message.edit_text.assert_called_once()
    assert "Мова паспяхова зменена на Беларускую" in cb.message.edit_text.call_args[0][0]

    # Verify DB was updated
    new_lang = await get_user_language(test_session, 12345)
    assert new_lang == "be"


def test_sub_card_formatting_i18n():
    sub = Subscription(
        service_name="Spotify",
        price=4.99,
        currency="USD",
        period_days=30,
        next_billing_date=date.today() + timedelta(days=5),
        cancel_url="https://spotify.com/cancel",
        is_active=True,
    )

    card_ru = format_sub_card(sub, lang="ru")
    assert "● Активна" in card_ru
    assert "• Сумма:" in card_ru
    assert "через 5 дн." in card_ru

    card_be = format_sub_card(sub, lang="be")
    assert "● Актыўная" in card_be
    assert "• Сума:" in card_be
    assert "праз 5 дн." in card_be

    card_en = format_sub_card(sub, lang="en")
    assert "● Active" in card_en
    assert "• Amount:" in card_en
    assert "in 5 d." in card_en

    card_pl = format_sub_card(sub, lang="pl")
    assert "● Aktywna" in card_pl
    assert "• Kwota:" in card_pl
    assert "za 5 dni" in card_pl


def test_analytics_caption_i18n():
    metrics = {
        "target_currency": "USD",
        "total_annual": 1200.0,
        "monthly_avg": 100.0,
        "services_count": 3,
        "services": [
            {"name": "AWS", "annual_cost": 600.0, "price": 50.0, "currency": "USD", "period_days": 30},
        ],
        "top_services": [
            {"name": "AWS", "annual_cost": 600.0, "price": 50.0, "currency": "USD", "period_days": 30},
        ],
        "currencies_used": ["USD"],
        "has_multiple_currencies": False,
        "rates": {},
    }

    cap_ru = format_analytics_caption(metrics, lang="ru")
    assert "Аналитика регулярных расходов" in cap_ru
    assert "В год:" in cap_ru

    cap_be = format_analytics_caption(metrics, lang="be")
    assert "Аналітыка рэгулярных выдаткаў" in cap_be
    assert "У год:" in cap_be

    cap_en = format_analytics_caption(metrics, lang="en")
    assert "Recurring Expense Analytics" in cap_en
    assert "Per year:" in cap_en

    cap_pl = format_analytics_caption(metrics, lang="pl")
    assert "Analityka wydatków cyklicznych" in cap_pl
    assert "Rocznie:" in cap_pl


def test_reminder_keyboard_i18n():
    kb_ru = build_reminder_keyboard(1, "https://example.com/cancel", lang="ru")
    assert kb_ru.inline_keyboard[0][0].text == "🔗 Отменить подписку"
    assert kb_ru.inline_keyboard[1][0].text == "✅ Отметить оплаченным"

    kb_be = build_reminder_keyboard(1, "https://example.com/cancel", lang="be")
    assert kb_be.inline_keyboard[0][0].text == "🔗 Адмяніць падпіску"
    assert kb_be.inline_keyboard[1][0].text == "✅ Адзначыць аплачаным"

    kb_en = build_reminder_keyboard(1, "https://example.com/cancel", lang="en")
    assert kb_en.inline_keyboard[0][0].text == "🔗 Cancel subscription"
    assert kb_en.inline_keyboard[1][0].text == "✅ Mark as paid"

    kb_pl = build_reminder_keyboard(1, "https://example.com/cancel", lang="pl")
    assert kb_pl.inline_keyboard[0][0].text == "🔗 Anuluj subskrypcję"
    assert kb_pl.inline_keyboard[1][0].text == "✅ Oznacz jako opłacone"


def test_subscription_card_keyboard_i18n():
    for lang, expected_renew in [
        ("ru", "🔄 Продлить"),
        ("be", "🔄 Падоўжыць"),
        ("en", "🔄 Renew"),
        ("pl", "🔄 Przedłuż"),
    ]:
        kb = get_subscription_card_keyboard(sub_id=1, is_active=True, cancel_url=None, lang=lang)
        buttons = [btn.text for row in kb.inline_keyboard for btn in row]
        assert expected_renew in buttons
        assert any(btn.callback_data == "renew_sub_1" for row in kb.inline_keyboard for btn in row)
        alert = get_text("sub_renewed_alert", lang, date="01.01.2027")
        assert "01.01.2027" in alert


