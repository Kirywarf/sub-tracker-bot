from datetime import date, timedelta
from typing import List, Optional, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Subscription


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    timezone: str = "UTC+3",
) -> User:
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=telegram_id, username=username, timezone=timezone)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    elif username and user.username != username:
        user.username = username
        await session.commit()
        await session.refresh(user)

    return user


async def update_user_timezone(
    session: AsyncSession,
    telegram_id: int,
    timezone: str,
) -> Optional[User]:
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user:
        user.timezone = timezone
        await session.commit()
        await session.refresh(user)
    return user


async def add_subscription(
    session: AsyncSession,
    user_id: int,
    service_name: str,
    price: float,
    currency: str,
    period_days: int,
    next_billing_date: date,
    cancel_url: Optional[str] = None,
) -> Subscription:
    sub = Subscription(
        user_id=user_id,
        service_name=service_name,
        price=price,
        currency=currency,
        period_days=period_days,
        next_billing_date=next_billing_date,
        cancel_url=cancel_url,
        is_active=True,
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub


async def get_user_subscriptions(
    session: AsyncSession,
    user_id: int,
    active_only: bool = False,
) -> List[Subscription]:
    query = select(Subscription).where(Subscription.user_id == user_id)
    if active_only:
        query = query.where(Subscription.is_active.is_(True))
    query = query.order_by(Subscription.next_billing_date.asc())
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_subscription_by_id(
    session: AsyncSession,
    sub_id: int,
) -> Optional[Subscription]:
    query = select(Subscription).where(Subscription.id == sub_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def update_subscription(
    session: AsyncSession,
    sub_id: int,
    **kwargs: Any,
) -> Optional[Subscription]:
    query = select(Subscription).where(Subscription.id == sub_id)
    result = await session.execute(query)
    sub = result.scalar_one_or_none()
    if not sub:
        return None

    for key, value in kwargs.items():
        if hasattr(sub, key):
            setattr(sub, key, value)

    await session.commit()
    await session.refresh(sub)
    return sub


async def toggle_subscription_status(
    session: AsyncSession,
    sub_id: int,
) -> Optional[Subscription]:
    sub = await get_subscription_by_id(session, sub_id)
    if not sub:
        return None
    sub.is_active = not sub.is_active
    await session.commit()
    await session.refresh(sub)
    return sub


async def delete_subscription(
    session: AsyncSession,
    sub_id: int,
) -> bool:
    query = delete(Subscription).where(Subscription.id == sub_id)
    result = await session.execute(query)
    await session.commit()
    return (result.rowcount or 0) > 0


async def mark_subscription_paid(
    session: AsyncSession,
    sub_id: int,
) -> Optional[Subscription]:
    sub = await get_subscription_by_id(session, sub_id)
    if not sub:
        return None

    # Calculate new billing date by adding period_days
    new_date = sub.next_billing_date + timedelta(days=sub.period_days)
    today = date.today()
    # If overdue by more than a period, adjust to next future billing
    while new_date <= today:
        new_date += timedelta(days=sub.period_days)

    sub.next_billing_date = new_date
    await session.commit()
    await session.refresh(sub)
    return sub


async def get_subscriptions_due_for_reminder(
    session: AsyncSession,
    target_date: date,
) -> List[Subscription]:
    query = (
        select(Subscription)
        .where(
            Subscription.is_active.is_(True),
            Subscription.next_billing_date == target_date,
        )
        .order_by(Subscription.user_id.asc())
    )
    result = await session.execute(query)
    return list(result.scalars().all())
