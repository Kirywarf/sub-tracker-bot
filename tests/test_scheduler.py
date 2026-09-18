import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock
from database.requests import get_or_create_user, add_subscription
from services.scheduler import check_and_send_reminders, build_reminder_keyboard


@pytest.mark.asyncio
async def test_check_and_send_reminders_trigger(test_session):
    # Setup test user and subscriptions
    await get_or_create_user(test_session, telegram_id=777)

    tomorrow = date.today() + timedelta(days=1)
    day_after = date.today() + timedelta(days=2)

    # Sub 1: Due tomorrow with cancel_url
    sub1 = await add_subscription(
        session=test_session,
        user_id=777,
        service_name="Иви",
        price=800.0,
        currency="RUB",
        period_days=30,
        next_billing_date=tomorrow,
        cancel_url="https://ivi.ru/cancel",
    )

    # Sub 2: Due day after tomorrow (should NOT trigger)
    await add_subscription(
        session=test_session,
        user_id=777,
        service_name="Кинопоиск",
        price=299.0,
        currency="RUB",
        period_days=30,
        next_billing_date=day_after,
    )

    # Sub 3: Due tomorrow but INACTIVE (should NOT trigger)
    sub3 = await add_subscription(
        session=test_session,
        user_id=777,
        service_name="Inactive Service",
        price=500.0,
        currency="RUB",
        period_days=30,
        next_billing_date=tomorrow,
    )
    sub3.is_active = False
    await test_session.commit()

    # Create mock session_factory that yields test_session
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__.return_value = test_session
    mock_session_factory.return_value.__aexit__.return_value = None

    # Create mock Bot
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()

    sent_count = await check_and_send_reminders(mock_bot, mock_session_factory)

    assert sent_count == 1
    assert mock_bot.send_message.call_count == 1

    call_args = mock_bot.send_message.call_args
    kwargs = call_args.kwargs

    assert kwargs["chat_id"] == 777
    assert "Напоминание о списании!" in kwargs["text"]
    assert "800 ₽" in kwargs["text"]
    assert "Иви" in kwargs["text"]

    # Verify buttons
    reply_markup = kwargs["reply_markup"]
    assert len(reply_markup.inline_keyboard) == 2
    # Row 1: Cancel URL button
    assert reply_markup.inline_keyboard[0][0].text == "🔗 Отменить подписку"
    assert reply_markup.inline_keyboard[0][0].url == "https://ivi.ru/cancel"
    # Row 2: Mark Paid button
    assert reply_markup.inline_keyboard[1][0].text == "✅ Отметить оплаченным"
    assert reply_markup.inline_keyboard[1][0].callback_data == f"paid_{sub1.id}"


def test_build_reminder_keyboard_without_url():
    kb = build_reminder_keyboard(sub_id=42, cancel_url=None)
    assert len(kb.inline_keyboard) == 1
    assert kb.inline_keyboard[0][0].text == "✅ Отметить оплаченным"
    assert kb.inline_keyboard[0][0].callback_data == "paid_42"
