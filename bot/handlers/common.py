from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.keyboards.reply import get_main_menu_keyboard
from bot.utils.cleaner import send_clean_message

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    first_name = message.from_user.first_name if message.from_user else "друг"
    user_id = message.from_user.id if message.from_user else 0

    welcome_text = (
        f" Привет, <b>{first_name}</b>!\n\n"
        "<b>StopPay</b> — контроль ваших подписок.\n\n"
        "• <b>24 часа</b> — алерт до списания\n"
        "• <b>1 тап</b> — прямая ссылка на отмену\n"
        "• <b>Аналитика</b> — прогноз расходов\n"
        "• <b>4 валюты</b> — BYN · RUB · USD · PLN\n\n"
        "Выберите действие:"
    )
    await send_clean_message(message, welcome_text, reply_markup=get_main_menu_keyboard(user_id=user_id))


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message) -> None:
    help_text = (
        " <b>Справка StopPay</b>\n\n"
        "• <b>➕ Добавить подписку</b> — сервис, сумма, период и дата\n"
        "• <b>📋 Мои подписки</b> — список, пауза, редактирование\n"
        "• <b>📊 Аналитика</b> — годовой прогноз и диаграмма\n"
        "• <b>🔔 Уведомление</b> — приходит за 24 часа до оплаты\n\n"
        "Сброс любого шага: <b>❌ Отмена</b>"
    )
    user_id = message.from_user.id if message.from_user else 0
    await send_clean_message(message, help_text, reply_markup=get_main_menu_keyboard(user_id=user_id))


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await send_clean_message(message, "Нет активных действий для отмены.", reply_markup=get_main_menu_keyboard())
        return

    await state.clear()
    await send_clean_message(message, "Действие отменено.", reply_markup=get_main_menu_keyboard())
