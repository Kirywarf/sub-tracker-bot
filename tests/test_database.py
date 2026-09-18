import pytest
from datetime import date, timedelta
from database.requests import (
    get_or_create_user,
    add_subscription,
    get_user_subscriptions,
    get_subscription_by_id,
    update_subscription,
    toggle_subscription_status,
    delete_subscription,
    mark_subscription_paid,
    get_subscriptions_due_for_reminder,
)


@pytest.mark.asyncio
async def test_user_creation_and_idempotency(test_session):
    user1 = await get_or_create_user(test_session, telegram_id=1001, username="testuser")
    assert user1.telegram_id == 1001
    assert user1.username == "testuser"
    assert user1.timezone == "UTC+3"

    # Fetch existing
    user2 = await get_or_create_user(test_session, telegram_id=1001, username="newname")
    assert user2.telegram_id == 1001
    assert user2.username == "newname"


@pytest.mark.asyncio
async def test_add_and_get_subscriptions(test_session):
    await get_or_create_user(test_session, telegram_id=2001, username="subscriber")

    sub = await add_subscription(
        session=test_session,
        user_id=2001,
        service_name="Яндекс Плюс",
        price=299.0,
        currency="RUB",
        period_days=30,
        next_billing_date=date(2026, 10, 1),
        cancel_url="https://plus.yandex.ru",
    )
    assert sub.id is not None
    assert sub.service_name == "Яндекс Плюс"
    assert sub.is_active is True

    # Get user subscriptions
    subs = await get_user_subscriptions(test_session, user_id=2001)
    assert len(subs) == 1
    assert subs[0].service_name == "Яндекс Плюс"


@pytest.mark.asyncio
async def test_toggle_and_update_subscription(test_session):
    await get_or_create_user(test_session, telegram_id=3001)
    sub = await add_subscription(
        session=test_session,
        user_id=3001,
        service_name="Spotify",
        price=10.0,
        currency="USD",
        period_days=30,
        next_billing_date=date(2026, 10, 15),
    )

    # Toggle active
    updated = await toggle_subscription_status(test_session, sub.id)
    assert updated.is_active is False

    updated = await toggle_subscription_status(test_session, sub.id)
    assert updated.is_active is True

    # Update field
    mod_sub = await update_subscription(test_session, sub.id, price=11.99, service_name="Spotify Premium")
    assert mod_sub.price == 11.99
    assert mod_sub.service_name == "Spotify Premium"


@pytest.mark.asyncio
async def test_mark_subscription_paid(test_session):
    await get_or_create_user(test_session, telegram_id=4001)
    sub = await add_subscription(
        session=test_session,
        user_id=4001,
        service_name="Netflix",
        price=799.0,
        currency="RUB",
        period_days=30,
        next_billing_date=date.today(),
    )

    updated_sub = await mark_subscription_paid(test_session, sub.id)
    assert updated_sub.next_billing_date > date.today()
    assert updated_sub.next_billing_date == date.today() + timedelta(days=30)


@pytest.mark.asyncio
async def test_get_subscriptions_due_for_reminder(test_session):
    await get_or_create_user(test_session, telegram_id=5001)
    tomorrow = date.today() + timedelta(days=1)
    day_after_tomorrow = date.today() + timedelta(days=2)

    sub_due = await add_subscription(
        session=test_session,
        user_id=5001,
        service_name="Иви",
        price=800.0,
        currency="RUB",
        period_days=30,
        next_billing_date=tomorrow,
        cancel_url="https://ivi.ru/profile",
    )

    sub_later = await add_subscription(
        session=test_session,
        user_id=5001,
        service_name="Okko",
        price=399.0,
        currency="RUB",
        period_days=30,
        next_billing_date=day_after_tomorrow,
    )

    due_list = await get_subscriptions_due_for_reminder(test_session, tomorrow)
    assert len(due_list) == 1
    assert due_list[0].id == sub_due.id
    assert due_list[0].service_name == "Иви"


@pytest.mark.asyncio
async def test_delete_subscription(test_session):
    await get_or_create_user(test_session, telegram_id=6001)
    sub = await add_subscription(
        session=test_session,
        user_id=6001,
        service_name="DeleteMe",
        price=100.0,
        currency="BYN",
        period_days=30,
        next_billing_date=date(2026, 11, 1),
    )

    success = await delete_subscription(test_session, sub.id)
    assert success is True

    fetched = await get_subscription_by_id(test_session, sub.id)
    assert fetched is None
