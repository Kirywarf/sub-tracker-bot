from datetime import date, datetime, timedelta
from typing import Optional
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.subscription_states import AddSubscriptionStates, EditSubscriptionStates
from bot.keyboards.reply import get_main_menu_keyboard, get_cancel_keyboard
from bot.keyboards.inline import (
    get_currency_keyboard,
    get_period_keyboard,
    get_skip_cancel_url_keyboard,
    get_subscriptions_list_keyboard,
    get_subscription_card_keyboard,
    get_delete_confirm_keyboard,
    get_edit_fields_keyboard,
    get_edit_currency_keyboard,
)
from bot.utils.validators import (
    validate_service_name,
    validate_price,
    validate_period_days,
    validate_billing_date,
    validate_cancel_url,
)
from database.requests import (
    add_subscription,
    get_user_subscriptions,
    get_subscription_by_id,
    update_subscription,
    toggle_subscription_status,
    delete_subscription,
    mark_subscription_paid,
)

router = Router(name="subscriptions")

CURRENCY_DISPLAY = {
    "RUB": "₽",
    "BYN": "Br",
    "USD": "$",
    "EUR": "€",
    "PLN": "zł",
}


def format_sub_card(sub) -> str:
    curr = CURRENCY_DISPLAY.get(sub.currency, sub.currency)
    price_str = f"{sub.price:g}" if sub.price.is_integer() else f"{sub.price:.2f}"
    status_str = "🟢 Активна" if sub.is_active else "⏸ Приостановлена"

    today = date.today()
    days_left = (sub.next_billing_date - today).days
    if days_left > 0:
        days_str = f"через {days_left} дн."
    elif days_left == 0:
        days_str = "сегодня!"
    else:
        days_str = f"просрочено на {-days_left} дн."

    date_formatted = sub.next_billing_date.strftime("%d.%m.%Y")

    card = (
        f"💳 <b>Подписка: {sub.service_name}</b>\n\n"
        f"• <b>Стоимость:</b> {price_str} {curr} ({sub.currency})\n"
        f"• <b>Периодичность:</b> каждые {sub.period_days} дн.\n"
        f"• <b>Следующее списание:</b> {date_formatted} (<i>{days_str}</i>)\n"
        f"• <b>Статус:</b> {status_str}\n"
    )
    if sub.cancel_url:
        card += f"• <b>Ссылка отмены:</b> <a href=\"{sub.cancel_url}\">Перейти</a>\n"
    return card


# --- FLOW: ADD SUBSCRIPTION ---

@router.message(Command("add"))
@router.message(F.text == "➕ Добавить подписку")
async def start_add_subscription(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddSubscriptionStates.service_name)
    await message.answer(
        "📝 Шаг 1/5: Введите <b>название сервиса</b>\n(например, <i>Яндекс Плюс</i>, <i>YouTube Premium</i>, <i>Spotify</i>):",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(),
    )


@router.callback_query(F.data == "add_new_sub")
async def cb_add_new_sub(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await state.set_state(AddSubscriptionStates.service_name)
    await callback.message.answer(
        "📝 Шаг 1/5: Введите <b>название сервиса</b>\n(например, <i>Яндекс Плюс</i>, <i>YouTube Premium</i>, <i>Spotify</i>):",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddSubscriptionStates.service_name)
async def process_service_name(message: Message, state: FSMContext) -> None:
    is_valid, name, error = validate_service_name(message.text)
    if not is_valid:
        await message.answer(f"⚠️ {error}", parse_mode="HTML")
        return

    await state.update_data(service_name=name)
    await state.set_state(AddSubscriptionStates.price)
    await message.answer(
        f"💰 Шаг 2/5: Введите <b>стоимость списания</b> для <b>{name}</b>\n(например: <code>299</code> или <code>14.99</code>):",
        parse_mode="HTML",
    )


@router.message(AddSubscriptionStates.price)
async def process_price(message: Message, state: FSMContext) -> None:
    is_valid, price, error = validate_price(message.text)
    if not is_valid:
        await message.answer(f"⚠️ {error}", parse_mode="HTML")
        return

    await state.update_data(price=price)
    await state.set_state(AddSubscriptionStates.currency)
    await message.answer(
        f"💱 Выберите <b>валюту</b> списания:",
        parse_mode="HTML",
        reply_markup=get_currency_keyboard(),
    )


@router.callback_query(AddSubscriptionStates.currency, F.data.startswith("curr_"))
async def process_currency_selection(callback: CallbackQuery, state: FSMContext) -> None:
    currency = callback.data.split("_")[1]
    await state.update_data(currency=currency)
    await state.set_state(AddSubscriptionStates.period)
    await callback.answer()

    curr_symbol = CURRENCY_DISPLAY.get(currency, currency)
    await callback.message.edit_text(
        f"Валюта выбрана: <b>{curr_symbol} ({currency})</b>\n\n"
        "⏱ Шаг 3/5: Выберите <b>периодичность списания</b>:",
        parse_mode="HTML",
        reply_markup=get_period_keyboard(),
    )


@router.callback_query(AddSubscriptionStates.period, F.data.startswith("period_"))
async def process_period_selection(callback: CallbackQuery, state: FSMContext) -> None:
    period_type = callback.data.split("_")[1]
    await callback.answer()

    if period_type == "custom":
        await state.set_state(AddSubscriptionStates.custom_period)
        await callback.message.answer(
            "Введите количество дней между списаниями целым числом (например, <code>14</code> или <code>90</code>):",
            parse_mode="HTML",
        )
        return

    period_days = int(period_type)
    await state.update_data(period_days=period_days)
    await state.set_state(AddSubscriptionStates.billing_date)
    await callback.message.edit_text(
        f"Периодичность: <b>{period_days} дн.</b>\n\n"
        "📅 Шаг 4/5: Введите <b>дату ближайшего списания</b> в формате <code>ДД.ММ.ГГГГ</code>\n"
        "(например: <code>25.10.2026</code>):",
        parse_mode="HTML",
    )


@router.message(AddSubscriptionStates.custom_period)
async def process_custom_period(message: Message, state: FSMContext) -> None:
    is_valid, days, error = validate_period_days(message.text)
    if not is_valid:
        await message.answer(f"⚠️ {error}", parse_mode="HTML")
        return

    await state.update_data(period_days=days)
    await state.set_state(AddSubscriptionStates.billing_date)
    await message.answer(
        f"Интервал сохранен: <b>{days} дн.</b>\n\n"
        "📅 Шаг 4/5: Введите <b>дату ближайшего списания</b> в формате <code>ДД.ММ.ГГГГ</code>\n"
        "(например: <code>25.10.2026</code>):",
        parse_mode="HTML",
    )


@router.message(AddSubscriptionStates.billing_date)
async def process_billing_date(message: Message, state: FSMContext) -> None:
    is_valid, parsed_date, error = validate_billing_date(message.text)
    if not is_valid:
        await message.answer(f"⚠️ {error}", parse_mode="HTML")
        return

    await state.update_data(next_billing_date=parsed_date)
    await state.set_state(AddSubscriptionStates.cancel_url)
    await message.answer(
        f"Дата списания: <b>{parsed_date.strftime('%d.%m.%Y')}</b>\n\n"
        "🔗 Шаг 5/5: Отправьте <b>ссылку на страницу отмены подписки</b> (например, <code>https://plus.yandex.ru</code>)\n"
        "или нажмите кнопку «Пропустить», если ссылки нет:",
        parse_mode="HTML",
        reply_markup=get_skip_cancel_url_keyboard(),
    )


@router.callback_query(AddSubscriptionStates.cancel_url, F.data == "skip_cancel_url")
async def process_skip_cancel_url(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    await callback.answer()
    data = await state.get_data()
    await state.clear()

    sub = await add_subscription(
        session=session,
        user_id=callback.from_user.id,
        service_name=data["service_name"],
        price=data["price"],
        currency=data["currency"],
        period_days=data["period_days"],
        next_billing_date=data["next_billing_date"],
        cancel_url=None,
    )

    await callback.message.answer(
        "🎉 <b>Подписка успешно сохранена!</b>\n\n" + format_sub_card(sub),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(AddSubscriptionStates.cancel_url)
async def process_cancel_url(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    is_valid, clean_url, error = validate_cancel_url(message.text)
    if not is_valid:
        await message.answer(
            f"⚠️ {error}\n\nЕсли хотите пропустить этот шаг, нажмите кнопку ниже:",
            parse_mode="HTML",
            reply_markup=get_skip_cancel_url_keyboard(),
        )
        return

    data = await state.get_data()
    await state.clear()

    sub = await add_subscription(
        session=session,
        user_id=message.from_user.id,
        service_name=data["service_name"],
        price=data["price"],
        currency=data["currency"],
        period_days=data["period_days"],
        next_billing_date=data["next_billing_date"],
        cancel_url=clean_url,
    )

    await message.answer(
        "🎉 <b>Подписка успешно сохранена!</b>\n\n" + format_sub_card(sub),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(),
    )


# --- SUBSCRIPTIONS LIST & MANAGEMENT ---

@router.message(Command("subscriptions"))
@router.message(Command("list"))
@router.message(F.text == "📋 Мои подписки")
async def show_subscriptions_list(
    message: Message,
    session: AsyncSession,
) -> None:
    subs = await get_user_subscriptions(session, message.from_user.id)
    if not subs:
        await message.answer(
            "У вас пока нет добавленных подписок.\n\n"
            "Нажмите кнопку ниже, чтобы добавить первую!",
            reply_markup=get_subscriptions_list_keyboard([]),
        )
        return

    await message.answer(
        f"📋 <b>Ваши подписки ({len(subs)}):</b>\n\n"
        "Нажмите на сервис, чтобы просмотреть подробности или отредактировать:",
        parse_mode="HTML",
        reply_markup=get_subscriptions_list_keyboard(subs),
    )


@router.callback_query(F.data == "list_subs")
async def cb_list_subscriptions(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    await callback.answer()
    subs = await get_user_subscriptions(session, callback.from_user.id)
    if not subs:
        await callback.message.edit_text(
            "У вас пока нет добавленных подписок.",
            reply_markup=get_subscriptions_list_keyboard([]),
        )
        return

    await callback.message.edit_text(
        f"📋 <b>Ваши подписки ({len(subs)}):</b>\n\n"
        "Нажмите на сервис, чтобы просмотреть подробности или отредактировать:",
        parse_mode="HTML",
        reply_markup=get_subscriptions_list_keyboard(subs),
    )


@router.callback_query(F.data.startswith("view_sub_"))
async def cb_view_subscription(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    sub_id = int(callback.data.split("_")[2])
    sub = await get_subscription_by_id(session, sub_id)
    if not sub or sub.user_id != callback.from_user.id:
        await callback.answer("Подписка не найдена.", show_alert=True)
        return

    await callback.answer()
    text = format_sub_card(sub)
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_subscription_card_keyboard(sub.id, sub.is_active, sub.cancel_url),
    )


@router.callback_query(F.data.startswith("toggle_sub_"))
async def cb_toggle_subscription(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    sub_id = int(callback.data.split("_")[2])
    sub = await get_subscription_by_id(session, sub_id)
    if not sub or sub.user_id != callback.from_user.id:
        await callback.answer("Подписка не найдена.", show_alert=True)
        return

    updated_sub = await toggle_subscription_status(session, sub_id)
    status_msg = "активирована" if updated_sub.is_active else "приостановлена"
    await callback.answer(f"Подписка {status_msg}!")

    text = format_sub_card(updated_sub)
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_subscription_card_keyboard(updated_sub.id, updated_sub.is_active, updated_sub.cancel_url),
    )


@router.callback_query(F.data.startswith("delete_sub_"))
async def cb_delete_subscription_prompt(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    sub_id = int(callback.data.split("_")[2])
    sub = await get_subscription_by_id(session, sub_id)
    if not sub or sub.user_id != callback.from_user.id:
        await callback.answer("Подписка не найдена.", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        f"Вы действительно хотите удалить подписку <b>{sub.service_name}</b>?",
        parse_mode="HTML",
        reply_markup=get_delete_confirm_keyboard(sub_id),
    )


@router.callback_query(F.data.startswith("confirm_del_"))
async def cb_confirm_delete(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    sub_id = int(callback.data.split("_")[2])
    deleted = await delete_subscription(session, sub_id)
    if deleted:
        await callback.answer("Подписка удалена.", show_alert=True)
    else:
        await callback.answer("Не удалось удалить подписку.", show_alert=True)

    subs = await get_user_subscriptions(session, callback.from_user.id)
    await callback.message.edit_text(
        f"📋 <b>Ваши подписки ({len(subs)}):</b>",
        parse_mode="HTML",
        reply_markup=get_subscriptions_list_keyboard(subs),
    )


# --- EDIT SUBSCRIPTION ---

@router.callback_query(F.data.startswith("edit_sub_"))
async def cb_edit_subscription(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    sub_id = int(callback.data.split("_")[2])
    sub = await get_subscription_by_id(session, sub_id)
    if not sub or sub.user_id != callback.from_user.id:
        await callback.answer("Подписка не найдена.", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        f"Какое поле для подписки <b>{sub.service_name}</b> вы хотите изменить?",
        parse_mode="HTML",
        reply_markup=get_edit_fields_keyboard(sub_id),
    )


@router.callback_query(F.data.startswith("edit_field_"))
async def cb_edit_field_selected(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    parts = callback.data.split("_")
    sub_id = int(parts[2])
    field = parts[3]

    await callback.answer()

    if field == "currency":
        await callback.message.edit_text(
            "Выберите новую валюту:",
            reply_markup=get_edit_currency_keyboard(sub_id),
        )
        return

    field_prompts = {
        "name": "Введите новое <b>название сервиса</b>:",
        "price": "Введите новую <b>стоимость</b> (число):",
        "period": "Введите новый <b>интервал списания в днях</b> (например, 30 или 365):",
        "date": "Введите новую <b>дату следующего списания</b> (ДД.ММ.ГГГГ):",
        "url": "Введите новую <b>ссылку на отмену</b> (или отправьте '-' чтобы очистить):",
    }

    prompt = field_prompts.get(field, "Введите новое значение:")
    await state.set_state(EditSubscriptionStates.edit_value)
    await state.update_data(edit_sub_id=sub_id, edit_field=field)

    await callback.message.answer(
        f"✏️ {prompt}",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(),
    )


@router.callback_query(F.data.startswith("set_curr_"))
async def cb_set_edit_currency(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    parts = callback.data.split("_")
    sub_id = int(parts[2])
    new_curr = parts[3]

    sub = await update_subscription(session, sub_id, currency=new_curr)
    await callback.answer(f"Валюта изменена на {new_curr}")
    await callback.message.edit_text(
        format_sub_card(sub),
        parse_mode="HTML",
        reply_markup=get_subscription_card_keyboard(sub.id, sub.is_active, sub.cancel_url),
    )


@router.message(EditSubscriptionStates.edit_value)
async def process_edit_value(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    data = await state.get_data()
    sub_id = data.get("edit_sub_id")
    field = data.get("edit_field")

    update_kwargs = {}

    if field == "name":
        valid, val, err = validate_service_name(message.text)
        if not valid:
            await message.answer(f"⚠️ {err}", parse_mode="HTML")
            return
        update_kwargs["service_name"] = val

    elif field == "price":
        valid, val, err = validate_price(message.text)
        if not valid:
            await message.answer(f"⚠️ {err}", parse_mode="HTML")
            return
        update_kwargs["price"] = val

    elif field == "period":
        valid, val, err = validate_period_days(message.text)
        if not valid:
            await message.answer(f"⚠️ {err}", parse_mode="HTML")
            return
        update_kwargs["period_days"] = val

    elif field == "date":
        valid, val, err = validate_billing_date(message.text)
        if not valid:
            await message.answer(f"⚠️ {err}", parse_mode="HTML")
            return
        update_kwargs["next_billing_date"] = val

    elif field == "url":
        clean = message.text.strip()
        if clean == "-":
            update_kwargs["cancel_url"] = None
        else:
            valid, val, err = validate_cancel_url(clean)
            if not valid:
                await message.answer(f"⚠️ {err}", parse_mode="HTML")
                return
            update_kwargs["cancel_url"] = val

    await state.clear()
    updated_sub = await update_subscription(session, sub_id, **update_kwargs)
    await message.answer("✅ <b>Изменения успешно сохранены!</b>", parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    await message.answer(
        format_sub_card(updated_sub),
        parse_mode="HTML",
        reply_markup=get_subscription_card_keyboard(updated_sub.id, updated_sub.is_active, updated_sub.cancel_url),
    )


# --- REMINDER ACTIONS ---

@router.callback_query(F.data.startswith("paid_"))
async def cb_mark_paid(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    sub_id = int(callback.data.split("_")[1])
    sub = await mark_subscription_paid(session, sub_id)
    if not sub:
        await callback.answer("Подписка не найдена.", show_alert=True)
        return

    await callback.answer("Оплата отмечена!")
    new_date_str = sub.next_billing_date.strftime("%d.%m.%Y")
    await callback.message.edit_text(
        f"✅ <b>Оплата отмечена!</b>\n\n"
        f"Сервис <b>{sub.service_name}</b> оплачен.\n"
        f"Следующее списание запланировано на <b>{new_date_str}</b>.",
        parse_mode="HTML",
    )
