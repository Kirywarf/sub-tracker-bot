from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.keyboards.reply import get_main_menu_keyboard

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    welcome_text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Я бот для учета ваших регулярных платежей и подписок.\n\n"
        "✨ <b>Что я умею:</b>\n"
        "• 🔔 <b>Напоминать за 24 часа</b> до списания средств\n"
        "• 🔗 Хранить прямую ссылку на отмену подписки\n"
        "• 📊 Считать <b>аналитику трат за год</b> и строить наглядные графики\n"
        "• 💵 Поддерживать валюты: <b>RUB (₽)</b>, <b>BYN (Br)</b>, <b>USD ($)</b>, <b>EUR (€)</b>\n\n"
        "Выберите действие в меню ниже 👇"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message) -> None:
    help_text = (
        "📖 <b>Справка по работе с ботом</b>\n\n"
        "• <b>➕ Добавить подписку</b> — запускает пошаговый мастер создания:\n"
        "  1. Название сервиса (например, <i>Яндекс Плюс</i>, <i>Netflix</i>)\n"
        "  2. Сумму и валюту (RUB, BYN, USD, EUR)\n"
        "  3. Период списания (ежемесячно 30 дней, ежегодно 365 дней или свой интервал)\n"
        "  4. Дату следующего списания в формате <code>ДД.ММ.ГГГГ</code> (например, <code>25.10.2026</code>)\n"
        "  5. Ссылку на страницу отмены подписки (по желанию)\n\n"
        "• <b>📋 Мои подписки</b> — просмотр всех добавленных сервисов, управление статусом (активна/приостановлена), редактирование и удаление.\n\n"
        "• <b>📊 Аналитика</b> — сводка прогноза расходов на год с распределением по сервисам и красивой диаграммой.\n\n"
        "• <b>🔔 Напоминания:</b>\n"
        "За 24 часа до даты списания бот пришлет уведомление с кнопками быстрой отмены сервиса и отметки платежа выполненным (с автоматическим переносом даты на следующий период).\n\n"
        "Если вы находитесь в процессе заполнения формы, нажмите <b>❌ Отмена</b> для сброса."
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных действий для отмены.", reply_markup=get_main_menu_keyboard())
        return

    await state.clear()
    await message.answer("Действие отменено.", reply_markup=get_main_menu_keyboard())
