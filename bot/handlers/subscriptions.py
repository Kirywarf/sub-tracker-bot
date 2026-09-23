from datetime import date, datetime, timedelta
from typing import Optional
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.subscription_states import AddSubscriptionStates, EditSubscriptionStates
from bot.keyboards.reply import get_main_menu_keyboard, get_cancel_keyboard
from bot.utils.cleaner import send_clean_message
from bot.locales import get_text
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
    renew_subscription,
)

router = Router(name="subscriptions")

CURRENCY_DISPLAY = {
    "RUB": "₽",
    "BYN": "Br",
    "USD": "$",
    "EUR": "€",
    "PLN": "zł",
}


def format_sub_card(sub, lang: str = "ru") -> str:
    curr = CURRENCY_DISPLAY.get(sub.currency, sub.currency)
    price_str = f"{sub.price:g}" if sub.price.is_integer() else f"{sub.price:.2f}"
    status_str = get_text("status_active", lang) if sub.is_active else get_text("status_paused", lang)

    today = date.today()
    days_left = (sub.next_billing_date - today).days
    if days_left > 0:
        days_str = get_text("days_left_in", lang, days=days_left)
    elif days_left == 0:
        days_str = get_text("days_left_today", lang)
    else:
        days_str = get_text("days_left_overdue", lang, days=-days_left)

    date_formatted = sub.next_billing_date.strftime("%d.%m.%Y")

    card = (
        f" <b>{sub.service_name}</b> · {status_str}\n"
        f"────────────────────\n"
        f"{get_text('card_amount_line', lang, price=price_str, curr=curr, days=sub.period_days)}\n"
        f"{get_text('card_billing_line', lang, date=date_formatted, days_str=days_str)}\n"
    )
    if sub.cancel_url:
        card += f"{get_text('card_cancel_link_line', lang, url=sub.cancel_url)}\n"
    return card


# --- FLOW: ADD SUBSCRIPTION ---

@router.message(Command("add"))
@router.message(F.text.in_({"➕ Добавить подписку", "＋ Дадаць падпіску", "＋ Add subscription", "＋ Dodaj subskrypcję"}))
async def start_add_subscription(message: Message, state: FSMContext, user_lang: str = "ru") -> None:
    await state.clear()
    await state.set_state(AddSubscriptionStates.service_name)
    await state.update_data(flow_lang=user_lang)
    await send_clean_message(
        message,
        get_text("step_service_name", user_lang),
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(user_lang),
    )


@router.callback_query(F.data == "add_new_sub")
async def cb_add_new_sub(callback: CallbackQuery, state: FSMContext, user_lang: str = "ru") -> None:
    await callback.answer()
    await state.clear()
    await state.set_state(AddSubscriptionStates.service_name)
    await state.update_data(flow_lang=user_lang)
    await send_clean_message(
        callback.message,
        get_text("step_service_name", user_lang),
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(user_lang),
        delete_trigger=False,
    )


@router.message(AddSubscriptionStates.service_name)
async def process_service_name(message: Message, state: FSMContext, user_lang: str = "ru") -> None:
    data = await state.get_data()
    lang = data.get("flow_lang", user_lang)

    is_valid, name, error = validate_service_name(message.text, lang=lang)
    if not is_valid:
        await send_clean_message(message, f"⚠️ {error}", parse_mode="HTML", clean_previous=False)
        return

    await state.update_data(service_name=name)
    await state.set_state(AddSubscriptionStates.price)
    await send_clean_message(
        message,
        get_text("step_price", lang, name=name),
        parse_mode="HTML",
    )


@router.message(AddSubscriptionStates.price)
async def process_price(message: Message, state: FSMContext, user_lang: str = "ru") -> None:
    data = await state.get_data()
    lang = data.get("flow_lang", user_lang)

    is_valid, price, error = validate_price(message.text, lang=lang)
    if not is_valid:
        await send_clean_message(message, f"⚠️ {error}", parse_mode="HTML", clean_previous=False)
        return

    await state.update_data(price=price)
    await state.set_state(AddSubscriptionStates.currency)
    await send_clean_message(
        message,
        get_text("step_currency", lang),
        parse_mode="HTML",
        reply_markup=get_currency_keyboard(),
    )


@router.callback_query(AddSubscriptionStates.currency, F.data.startswith("curr_"))
async def process_currency_selection(callback: CallbackQuery, state: FSMContext, user_lang: str = "ru") -> None:
    currency = callback.data.split("_")[1]
    data = await state.get_data()
    lang = data.get("flow_lang", user_lang)

    await state.update_data(currency=currency)
    await state.set_state(AddSubscriptionStates.period)
    await callback.answer()

    curr_symbol = CURRENCY_DISPLAY.get(currency, currency)
    await callback.message.edit_text(
        get_text("step_period", lang, curr_symbol=curr_symbol, currency=currency),
        parse_mode="HTML",
        reply_markup=get_period_keyboard(lang=lang),
    )


@router.callback_query(AddSubscriptionStates.period, F.data.startswith("period_"))
async def process_period_selection(callback: CallbackQuery, state: FSMContext, user_lang: str = "ru") -> None:
    period_type = callback.data.split("_")[1]
    data = await state.get_data()
    lang = data.get("flow_lang", user_lang)
    await callback.answer()

    if period_type == "custom":
        await state.set_state(AddSubscriptionStates.custom_period)
        await callback.message.edit_text(
            get_text("custom_period_prompt", lang),
            parse_mode="HTML",
        )
        return

    period_days = int(period_type)
    await state.update_data(period_days=period_days)
    await state.set_state(AddSubscriptionStates.billing_date)
    await callback.message.edit_text(
        get_text("step_billing_date", lang, days=period_days),
        parse_mode="HTML",
    )


@router.message(AddSubscriptionStates.custom_period)
async def process_custom_period(message: Message, state: FSMContext, user_lang: str = "ru") -> None:
    data = await state.get_data()
    lang = data.get("flow_lang", user_lang)

    is_valid, days, error = validate_period_days(message.text, lang=lang)
    if not is_valid:
        await send_clean_message(message, f"⚠️ {error}", parse_mode="HTML", clean_previous=False)
        return

    await state.update_data(period_days=days)
    await state.set_state(AddSubscriptionStates.billing_date)
    await send_clean_message(
        message,
        get_text("step_billing_date", lang, days=days),
        parse_mode="HTML",
    )


@router.message(AddSubscriptionStates.billing_date)
async def process_billing_date(message: Message, state: FSMContext, user_lang: str = "ru") -> None:
    data = await state.get_data()
    lang = data.get("flow_lang", user_lang)

    is_valid, parsed_date, error = validate_billing_date(message.text, lang=lang)
    if not is_valid:
        await send_clean_message(message, f"⚠️ {error}", parse_mode="HTML", clean_previous=False)
        return

    await state.update_data(next_billing_date=parsed_date)
    await state.set_state(AddSubscriptionStates.cancel_url)
    await send_clean_message(
        message,
        get_text("step_cancel_url", lang, date=parsed_date.strftime("%d.%m.%Y")),
        parse_mode="HTML",
        reply_markup=get_skip_cancel_url_keyboard(lang=lang),
    )


@router.callback_query(AddSubscriptionStates.cancel_url, F.data == "skip_cancel_url")
async def process_skip_cancel_url(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    await callback.answer()
    data = await state.get_data()
    lang = data.get("flow_lang", user_lang)
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

    await send_clean_message(
        callback.message,
        get_text("sub_saved", lang) + format_sub_card(sub, lang=lang),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang=lang),
        delete_trigger=False,
    )


@router.message(AddSubscriptionStates.cancel_url)
async def process_cancel_url(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    data = await state.get_data()
    lang = data.get("flow_lang", user_lang)

    is_valid, clean_url, error = validate_cancel_url(message.text, lang=lang)
    if not is_valid:
        await send_clean_message(
            message,
            f"⚠️ {error}\n\n{get_text('skip_prompt_hint', lang)}",
            parse_mode="HTML",
            reply_markup=get_skip_cancel_url_keyboard(lang=lang),
            clean_previous=False,
        )
        return

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

    await send_clean_message(
        message,
        get_text("sub_saved", lang) + format_sub_card(sub, lang=lang),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang=lang),
    )


# --- SUBSCRIPTIONS LIST & MANAGEMENT ---

@router.message(Command("subscriptions"))
@router.message(Command("list"))
@router.message(F.text.in_({"📋 Мои подписки", "📋 Вашы падпіскі", "📋 Subscriptions", "📋 Subskrypcje"}))
async def show_subscriptions_list(
    message: Message,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    subs = await get_user_subscriptions(session, message.from_user.id)
    if not subs:
        await send_clean_message(
            message,
            get_text("no_subscriptions", user_lang),
            reply_markup=get_subscriptions_list_keyboard([], user_id=message.from_user.id, lang=user_lang),
        )
        return

    await send_clean_message(
        message,
        get_text("subs_list_title", user_lang, count=len(subs)),
        parse_mode="HTML",
        reply_markup=get_subscriptions_list_keyboard(subs, user_id=message.from_user.id, lang=user_lang),
    )


@router.callback_query(F.data == "list_subs")
async def cb_list_subscriptions(
    callback: CallbackQuery,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    await callback.answer()
    subs = await get_user_subscriptions(session, callback.from_user.id)
    if not subs:
        await callback.message.edit_text(
            get_text("no_subscriptions", user_lang),
            reply_markup=get_subscriptions_list_keyboard([], user_id=callback.from_user.id, lang=user_lang),
        )
        return

    await callback.message.edit_text(
        get_text("subs_list_title", user_lang, count=len(subs)),
        parse_mode="HTML",
        reply_markup=get_subscriptions_list_keyboard(subs, user_id=callback.from_user.id, lang=user_lang),
    )


@router.callback_query(F.data.startswith("view_sub_"))
async def cb_view_subscription(
    callback: CallbackQuery,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    sub_id = int(callback.data.split("_")[2])
    sub = await get_subscription_by_id(session, sub_id)
    if not sub or sub.user_id != callback.from_user.id:
        await callback.answer(get_text("sub_not_found", user_lang), show_alert=True)
        return

    await callback.answer()
    text = format_sub_card(sub, lang=user_lang)
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_subscription_card_keyboard(sub.id, sub.is_active, sub.cancel_url, lang=user_lang),
    )


@router.callback_query(F.data.startswith("toggle_sub_"))
async def cb_toggle_subscription(
    callback: CallbackQuery,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    sub_id = int(callback.data.split("_")[2])
    sub = await get_subscription_by_id(session, sub_id)
    if not sub or sub.user_id != callback.from_user.id:
        await callback.answer(get_text("sub_not_found", user_lang), show_alert=True)
        return

    updated_sub = await toggle_subscription_status(session, sub_id)
    status_msg = get_text("sub_status_activated", user_lang) if updated_sub.is_active else get_text("sub_status_paused", user_lang)
    await callback.answer(status_msg)

    text = format_sub_card(updated_sub, lang=user_lang)
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_subscription_card_keyboard(updated_sub.id, updated_sub.is_active, updated_sub.cancel_url, lang=user_lang),
    )


@router.callback_query(F.data.startswith("renew_sub_"))
async def cb_renew_subscription(
    callback: CallbackQuery,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    sub_id = int(callback.data.split("_")[2])
    sub = await get_subscription_by_id(session, sub_id)
    if not sub or sub.user_id != callback.from_user.id:
        await callback.answer(get_text("sub_not_found", user_lang), show_alert=True)
        return

    updated_sub = await renew_subscription(session, sub_id)
    new_date_str = updated_sub.next_billing_date.strftime("%d.%m.%Y")
    await callback.answer(get_text("sub_renewed_alert", user_lang, date=new_date_str))

    text = format_sub_card(updated_sub, lang=user_lang)
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_subscription_card_keyboard(updated_sub.id, updated_sub.is_active, updated_sub.cancel_url, lang=user_lang),
    )



@router.callback_query(F.data.startswith("delete_sub_"))
async def cb_delete_subscription_prompt(
    callback: CallbackQuery,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    sub_id = int(callback.data.split("_")[2])
    sub = await get_subscription_by_id(session, sub_id)
    if not sub or sub.user_id != callback.from_user.id:
        await callback.answer(get_text("sub_not_found", user_lang), show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        get_text("delete_prompt", user_lang, name=sub.service_name),
        parse_mode="HTML",
        reply_markup=get_delete_confirm_keyboard(sub_id, lang=user_lang),
    )


@router.callback_query(F.data.startswith("confirm_del_"))
async def cb_confirm_delete(
    callback: CallbackQuery,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    sub_id = int(callback.data.split("_")[2])
    deleted = await delete_subscription(session, sub_id)
    if deleted:
        await callback.answer(get_text("sub_deleted_alert", user_lang), show_alert=True)
    else:
        await callback.answer(get_text("sub_not_found", user_lang), show_alert=True)

    subs = await get_user_subscriptions(session, callback.from_user.id)
    await callback.message.edit_text(
        get_text("subs_list_title", user_lang, count=len(subs)),
        parse_mode="HTML",
        reply_markup=get_subscriptions_list_keyboard(subs, lang=user_lang),
    )


# --- EDIT SUBSCRIPTION ---

@router.callback_query(F.data.startswith("edit_sub_"))
async def cb_edit_subscription(
    callback: CallbackQuery,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    sub_id = int(callback.data.split("_")[2])
    sub = await get_subscription_by_id(session, sub_id)
    if not sub or sub.user_id != callback.from_user.id:
        await callback.answer(get_text("sub_not_found", user_lang), show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        get_text("edit_field_prompt", user_lang, name=sub.service_name),
        parse_mode="HTML",
        reply_markup=get_edit_fields_keyboard(sub_id, lang=user_lang),
    )


@router.callback_query(F.data.startswith("edit_field_"))
async def cb_edit_field_selected(
    callback: CallbackQuery,
    state: FSMContext,
    user_lang: str = "ru",
) -> None:
    parts = callback.data.split("_")
    sub_id = int(parts[2])
    field = parts[3]

    await callback.answer()

    if field == "currency":
        await callback.message.edit_text(
            get_text("select_new_currency", user_lang),
            reply_markup=get_edit_currency_keyboard(sub_id, lang=user_lang),
        )
        return

    field_prompts = {
        "name": get_text("prompt_edit_name", user_lang),
        "price": get_text("prompt_edit_price", user_lang),
        "period": get_text("prompt_edit_period", user_lang),
        "date": get_text("prompt_edit_date", user_lang),
        "url": get_text("prompt_edit_url", user_lang),
    }

    prompt = field_prompts.get(field, "...")
    await state.set_state(EditSubscriptionStates.edit_value)
    await state.update_data(edit_sub_id=sub_id, edit_field=field, flow_lang=user_lang)

    await callback.message.answer(
        f"✏️ {prompt}",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(user_lang),
    )


@router.callback_query(F.data.startswith("set_curr_"))
async def cb_set_edit_currency(
    callback: CallbackQuery,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    parts = callback.data.split("_")
    sub_id = int(parts[2])
    new_curr = parts[3]

    sub = await update_subscription(session, sub_id, currency=new_curr)
    await callback.answer(get_text("currency_changed_alert", user_lang, curr=new_curr))
    await callback.message.edit_text(
        format_sub_card(sub, lang=user_lang),
        parse_mode="HTML",
        reply_markup=get_subscription_card_keyboard(sub.id, sub.is_active, sub.cancel_url, lang=user_lang),
    )


@router.message(EditSubscriptionStates.edit_value)
async def process_edit_value(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    data = await state.get_data()
    sub_id = data.get("edit_sub_id")
    field = data.get("edit_field")
    lang = data.get("flow_lang", user_lang)

    update_kwargs = {}

    if field == "name":
        valid, val, err = validate_service_name(message.text, lang=lang)
        if not valid:
            await message.answer(f"⚠️ {err}", parse_mode="HTML")
            return
        update_kwargs["service_name"] = val

    elif field == "price":
        valid, val, err = validate_price(message.text, lang=lang)
        if not valid:
            await message.answer(f"⚠️ {err}", parse_mode="HTML")
            return
        update_kwargs["price"] = val

    elif field == "period":
        valid, val, err = validate_period_days(message.text, lang=lang)
        if not valid:
            await message.answer(f"⚠️ {err}", parse_mode="HTML")
            return
        update_kwargs["period_days"] = val

    elif field == "date":
        valid, val, err = validate_billing_date(message.text, lang=lang)
        if not valid:
            await message.answer(f"⚠️ {err}", parse_mode="HTML")
            return
        update_kwargs["next_billing_date"] = val

    elif field == "url":
        clean = message.text.strip()
        if clean == "-":
            update_kwargs["cancel_url"] = None
        else:
            valid, val, err = validate_cancel_url(clean, lang=lang)
            if not valid:
                await message.answer(f"⚠️ {err}", parse_mode="HTML")
                return
            update_kwargs["cancel_url"] = val

    await state.clear()
    updated_sub = await update_subscription(session, sub_id, **update_kwargs)
    await send_clean_message(
        message,
        get_text("changes_saved", lang) + format_sub_card(updated_sub, lang=lang),
        parse_mode="HTML",
        reply_markup=get_subscription_card_keyboard(updated_sub.id, updated_sub.is_active, updated_sub.cancel_url, lang=lang),
    )


# --- REMINDER ACTIONS ---

@router.callback_query(F.data.startswith("paid_"))
async def cb_mark_paid(
    callback: CallbackQuery,
    session: AsyncSession,
    user_lang: str = "ru",
) -> None:
    sub_id = int(callback.data.split("_")[1])
    sub = await mark_subscription_paid(session, sub_id)
    if not sub:
        await callback.answer(get_text("sub_not_found", user_lang), show_alert=True)
        return

    await callback.answer(get_text("paid_marked_alert", user_lang))
    new_date_str = sub.next_billing_date.strftime("%d.%m.%Y")
    await callback.message.edit_text(
        get_text("paid_marked_text", user_lang, name=sub.service_name, date=new_date_str),
        parse_mode="HTML",
    )
