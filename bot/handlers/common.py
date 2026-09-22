from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.reply import get_main_menu_keyboard, get_webapp_url
from bot.locales import get_text, get_language_keyboard, normalize_language
from bot.utils.cleaner import send_clean_message
from database.requests import update_user_language
from config import settings

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user_lang: str = "ru") -> None:
    await state.clear()
    first_name = message.from_user.first_name if message.from_user else "друг"
    user_id = message.from_user.id if message.from_user else 0

    welcome_text = get_text("start_welcome", user_lang, name=first_name)

    webapp_url = getattr(settings, "WEBAPP_URL", "")
    if webapp_url and user_id and getattr(message, "bot", None):
        try:
            from aiogram.types import MenuButtonWebApp, WebAppInfo
            target_url = get_webapp_url(user_id=user_id, first_name=first_name, lang=user_lang)
            await message.bot.set_chat_menu_button(
                chat_id=message.chat.id,
                menu_button=MenuButtonWebApp(
                    text="StopPay ",
                    web_app=WebAppInfo(url=target_url),
                ),
            )
        except Exception:
            pass

    await send_clean_message(
        message,
        welcome_text,
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name, lang=user_lang),
    )


@router.message(Command("language", "lang"))
@router.message(F.text.in_({"🌐 Язык", "🌐 Мова", "🌐 Language", "🌐 Język"}))
async def cmd_language(message: Message, user_lang: str = "ru") -> None:
    text = get_text("choose_language", user_lang)
    await send_clean_message(
        message,
        text,
        reply_markup=get_language_keyboard(current_lang=user_lang),
    )


@router.callback_query(F.data.startswith("set_lang_"))
async def cb_set_language(callback: CallbackQuery, session: AsyncSession) -> None:
    new_lang = normalize_language(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    first_name = callback.from_user.first_name or ""

    await update_user_language(session, telegram_id=user_id, language=new_lang)
    confirm_text = get_text("lang_changed", new_lang)
    await callback.answer(confirm_text)

    # Update chat menu button with new language parameter
    if getattr(settings, "WEBAPP_URL", "") and getattr(callback, "bot", None):
        try:
            from aiogram.types import MenuButtonWebApp, WebAppInfo
            target_url = get_webapp_url(user_id=user_id, first_name=first_name, lang=new_lang)
            await callback.bot.set_chat_menu_button(
                chat_id=callback.message.chat.id,
                menu_button=MenuButtonWebApp(
                    text="StopPay ",
                    web_app=WebAppInfo(url=target_url),
                ),
            )
        except Exception:
            pass

    await callback.message.edit_text(
        confirm_text,
        reply_markup=get_language_keyboard(current_lang=new_lang),
    )

    # Also send clean message with refreshed main menu
    await send_clean_message(
        callback.message,
        confirm_text,
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name, lang=new_lang),
        delete_trigger=False,
    )


@router.message(Command("help"))
@router.message(F.text.in_({"ℹ️ Помощь", "ℹ️ Даведка", "ℹ️ Help", "ℹ️ Pomoc"}))
async def cmd_help(message: Message, user_lang: str = "ru") -> None:
    first_name = message.from_user.first_name if message.from_user else ""
    user_id = message.from_user.id if message.from_user else 0
    help_text = get_text("help_text", user_lang)

    await send_clean_message(
        message,
        help_text,
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name, lang=user_lang),
    )


@router.message(Command("add", "subscriptions", "analytics"))
@router.message(F.text.in_({
    "➕ Добавить подписку", "📋 Мои подписки", "📊 Аналитика",
    "＋ Дадаць падпіску", "📋 Вашы падпіскі", "📊 Аналітыка",
    "＋ Add subscription", "📋 Subscriptions", "📊 Analytics",
    "＋ Dodaj subskrypcję", "📋 Subskrypcje", "📊 Analityka",
}))
async def cmd_legacy_redirect(message: Message, state: FSMContext, user_lang: str = "ru") -> None:
    await state.clear()
    first_name = message.from_user.first_name if message.from_user else ""
    user_id = message.from_user.id if message.from_user else 0
    text = get_text("legacy_redirect", user_lang)
    await send_clean_message(
        message,
        text,
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name, lang=user_lang),
    )


@router.message(Command("cancel"))
@router.message(F.text.in_({"❌ Отмена", "❌ Адмена", "❌ Cancel", "❌ Anuluj"}))
async def cmd_cancel(message: Message, state: FSMContext, user_lang: str = "ru") -> None:
    first_name = message.from_user.first_name if message.from_user else ""
    user_id = message.from_user.id if message.from_user else 0
    current_state = await state.get_state()
    if current_state is None:
        await send_clean_message(
            message,
            get_text("cancel_no_active", user_lang),
            reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name, lang=user_lang),
        )
        return

    await state.clear()
    await send_clean_message(
        message,
        get_text("cancel_success", user_lang),
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name, lang=user_lang),
    )


@router.message(F.text)
async def fallback_text_handler(message: Message, user_lang: str = "ru") -> None:
    first_name = message.from_user.first_name if message.from_user else ""
    user_id = message.from_user.id if message.from_user else 0
    text = get_text("fallback_text", user_lang)
    await send_clean_message(
        message,
        text,
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name, lang=user_lang),
    )
