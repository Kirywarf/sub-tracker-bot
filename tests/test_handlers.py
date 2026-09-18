import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock
from aiogram.types import Message, CallbackQuery, User as TgUser, Chat
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey

from bot.handlers.common import cmd_start, cmd_cancel, cmd_help
from bot.handlers.subscriptions import (
    start_add_subscription,
    process_service_name,
    process_price,
    process_currency_selection,
    process_period_selection,
    process_custom_period,
    process_billing_date,
    process_skip_cancel_url,
    process_cancel_url,
    show_subscriptions_list,
    cb_list_subscriptions,
    cb_view_subscription,
    cb_toggle_subscription,
    cb_confirm_delete,
    cb_mark_paid,
    cb_set_edit_currency,
    process_edit_value,
)
from bot.handlers.analytics import show_analytics
from bot.states.subscription_states import AddSubscriptionStates, EditSubscriptionStates
from database.requests import get_or_create_user, get_user_subscriptions, add_subscription, get_subscription_by_id


def make_mock_message(text: str, user_id: int = 12345) -> Message:
    msg = AsyncMock(spec=Message)
    msg.text = text
    msg.from_user = TgUser(id=user_id, is_bot=False, first_name="Test", username="testuser")
    msg.chat = Chat(id=user_id, type="private")
    msg.date = date.today()
    msg.answer = AsyncMock()
    msg.answer_photo = AsyncMock()
    return msg


def make_mock_callback_query(data: str, user_id: int = 12345) -> CallbackQuery:
    cb = AsyncMock(spec=CallbackQuery)
    cb.data = data
    cb.from_user = TgUser(id=user_id, is_bot=False, first_name="Test", username="testuser")
    msg = AsyncMock(spec=Message)
    msg.edit_text = AsyncMock()
    msg.answer = AsyncMock()
    cb.message = msg
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def fsm_context():
    storage = MemoryStorage()
    key = StorageKey(bot_id=1, chat_id=12345, user_id=12345)
    return FSMContext(storage=storage, key=key)


@pytest.mark.asyncio
async def test_cmd_start_and_help(fsm_context):
    msg = make_mock_message("/start")
    await cmd_start(msg, fsm_context)
    msg.answer.assert_called_once()
    assert "Привет" in msg.answer.call_args[0][0]
    assert await fsm_context.get_state() is None

    msg_help = make_mock_message("/help")
    await cmd_help(msg_help)
    msg_help.answer.assert_called_once()
    assert "Справка" in msg_help.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_cmd_cancel(fsm_context):
    await fsm_context.set_state(AddSubscriptionStates.service_name)
    msg = make_mock_message("❌ Отмена")
    await cmd_cancel(msg, fsm_context)
    assert await fsm_context.get_state() is None
    assert "отменено" in msg.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_add_subscription_fsm_flow(test_session, fsm_context):
    await get_or_create_user(test_session, telegram_id=12345)

    # 1. Start FSM
    msg1 = make_mock_message("➕ Добавить подписку")
    await start_add_subscription(msg1, fsm_context)
    assert await fsm_context.get_state() == AddSubscriptionStates.service_name.state

    # 2. Service name
    msg2 = make_mock_message("Netflix Premium")
    await process_service_name(msg2, fsm_context)
    assert await fsm_context.get_state() == AddSubscriptionStates.price.state
    data = await fsm_context.get_data()
    assert data["service_name"] == "Netflix Premium"

    # 3. Price
    msg3 = make_mock_message("799.50")
    await process_price(msg3, fsm_context)
    assert await fsm_context.get_state() == AddSubscriptionStates.currency.state
    data = await fsm_context.get_data()
    assert data["price"] == 799.50

    # 4. Currency (choose BYN)
    cb4 = make_mock_callback_query("curr_BYN")
    await process_currency_selection(cb4, fsm_context)
    assert await fsm_context.get_state() == AddSubscriptionStates.period.state
    data = await fsm_context.get_data()
    assert data["currency"] == "BYN"

    # 5. Period (monthly 30 days)
    cb5 = make_mock_callback_query("period_30")
    await process_period_selection(cb5, fsm_context)
    assert await fsm_context.get_state() == AddSubscriptionStates.billing_date.state
    data = await fsm_context.get_data()
    assert data["period_days"] == 30

    # 6. Billing date
    msg6 = make_mock_message("15.11.2026")
    await process_billing_date(msg6, fsm_context)
    assert await fsm_context.get_state() == AddSubscriptionStates.cancel_url.state
    data = await fsm_context.get_data()
    assert data["next_billing_date"] == date(2026, 11, 15)

    # 7. Cancel URL
    msg7 = make_mock_message("https://netflix.com/cancel")
    await process_cancel_url(msg7, fsm_context, test_session)
    # FSM cleared
    assert await fsm_context.get_state() is None

    # Check database
    subs = await get_user_subscriptions(test_session, 12345)
    assert len(subs) == 1
    assert subs[0].service_name == "Netflix Premium"
    assert subs[0].currency == "BYN"
    assert subs[0].price == 799.50
    assert subs[0].period_days == 30
    assert subs[0].cancel_url == "https://netflix.com/cancel"


@pytest.mark.asyncio
async def test_add_subscription_custom_period_and_skip_url(test_session, fsm_context):
    await get_or_create_user(test_session, telegram_id=12345)

    # State: custom period
    await fsm_context.set_state(AddSubscriptionStates.period)
    cb_custom = make_mock_callback_query("period_custom")
    await process_period_selection(cb_custom, fsm_context)
    assert await fsm_context.get_state() == AddSubscriptionStates.custom_period.state

    # Input days
    msg_days = make_mock_message("14")
    await process_custom_period(msg_days, fsm_context)
    assert await fsm_context.get_state() == AddSubscriptionStates.billing_date.state
    data = await fsm_context.get_data()
    assert data["period_days"] == 14

    # Set remaining data
    await fsm_context.update_data(
        service_name="TwoWeekGym",
        price=50.0,
        currency="BYN",
        next_billing_date=date(2026, 10, 20),
    )
    await fsm_context.set_state(AddSubscriptionStates.cancel_url)

    # Skip URL
    cb_skip = make_mock_callback_query("skip_cancel_url")
    await process_skip_cancel_url(cb_skip, fsm_context, test_session)
    assert await fsm_context.get_state() is None

    subs = await get_user_subscriptions(test_session, 12345)
    assert any(s.service_name == "TwoWeekGym" and s.period_days == 14 and s.cancel_url is None for s in subs)


@pytest.mark.asyncio
async def test_list_and_view_and_toggle_subscription(test_session):
    await get_or_create_user(test_session, telegram_id=12345)
    sub = await add_subscription(
        session=test_session,
        user_id=12345,
        service_name="YouTube Premium",
        price=399.0,
        currency="RUB",
        period_days=30,
        next_billing_date=date(2026, 10, 1),
    )

    # List subscriptions
    msg = make_mock_message("📋 Мои подписки")
    await show_subscriptions_list(msg, test_session)
    msg.answer.assert_called_once()
    assert "Ваши подписки (1)" in msg.answer.call_args[0][0]

    # View subscription
    cb_view = make_mock_callback_query(f"view_sub_{sub.id}")
    await cb_view_subscription(cb_view, test_session)
    cb_view.message.edit_text.assert_called_once()
    assert "YouTube Premium" in cb_view.message.edit_text.call_args[0][0]

    # Toggle subscription (active -> inactive)
    cb_toggle = make_mock_callback_query(f"toggle_sub_{sub.id}")
    await cb_toggle_subscription(cb_toggle, test_session)
    reloaded = await get_subscription_by_id(test_session, sub.id)
    assert reloaded.is_active is False


@pytest.mark.asyncio
async def test_edit_fields_flow(test_session, fsm_context):
    await get_or_create_user(test_session, telegram_id=12345)
    sub = await add_subscription(
        session=test_session,
        user_id=12345,
        service_name="Gym",
        price=100.0,
        currency="BYN",
        period_days=30,
        next_billing_date=date(2026, 10, 1),
    )

    # Change currency via callback
    cb_curr = make_mock_callback_query(f"set_curr_{sub.id}_USD")
    await cb_set_edit_currency(cb_curr, test_session)
    reloaded = await get_subscription_by_id(test_session, sub.id)
    assert reloaded.currency == "USD"

    # Edit price via FSM
    await fsm_context.set_state(EditSubscriptionStates.edit_value)
    await fsm_context.update_data(edit_sub_id=sub.id, edit_field="price")
    msg_price = make_mock_message("150")
    await process_edit_value(msg_price, fsm_context, test_session)
    reloaded = await get_subscription_by_id(test_session, sub.id)
    assert reloaded.price == 150.0


@pytest.mark.asyncio
async def test_delete_subscription_callback(test_session):
    await get_or_create_user(test_session, telegram_id=12345)
    sub = await add_subscription(
        session=test_session,
        user_id=12345,
        service_name="ToDelete",
        price=50.0,
        currency="RUB",
        period_days=30,
        next_billing_date=date(2026, 10, 1),
    )

    cb_del = make_mock_callback_query(f"confirm_del_{sub.id}")
    await cb_confirm_delete(cb_del, test_session)
    reloaded = await get_subscription_by_id(test_session, sub.id)
    assert reloaded is None


@pytest.mark.asyncio
async def test_mark_paid_callback(test_session):
    await get_or_create_user(test_session, telegram_id=12345)
    sub = await add_subscription(
        session=test_session,
        user_id=12345,
        service_name="Spotify",
        price=10.0,
        currency="USD",
        period_days=30,
        next_billing_date=date(2026, 10, 1),
    )

    cb = make_mock_callback_query(f"paid_{sub.id}")
    await cb_mark_paid(cb, test_session)

    cb.answer.assert_called_once()
    cb.message.edit_text.assert_called_once()
    assert "Оплата отмечена" in cb.message.edit_text.call_args[0][0]


@pytest.mark.asyncio
async def test_analytics_handler(test_session):
    await get_or_create_user(test_session, telegram_id=12345)
    await add_subscription(
        session=test_session,
        user_id=12345,
        service_name="Яндекс Плюс",
        price=299.0,
        currency="RUB",
        period_days=30,
        next_billing_date=date(2026, 10, 1),
    )

    msg = make_mock_message("/analytics")
    await show_analytics(msg, test_session)

    msg.answer_photo.assert_called_once()
    caption = msg.answer_photo.call_args.kwargs["caption"]
    assert "Аналитика регулярных расходов" in caption
    assert "Яндекс Плюс" in caption
    assert "RUB" in caption
