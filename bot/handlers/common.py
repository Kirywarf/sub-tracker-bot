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
        f" Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "<b>StopPay</b> — персональный трекер регулярных подписок.\n\n"
        "<b>Возможности:</b>\n"
        "• <b>Уведомления за 24 часа</b> до списания средств\n"
        "• <b>Быстрая ссылка</b> на страницу отмены любого сервиса\n"
        "• <b>Аналитика расходов</b> в стиле Apple Card с кольцевой диаграммой\n"
        "• <b>Мультивалютность:</b> BYN (Br), RUB (₽), USD ($), PLN (zł)\n\n"
        "Выберите действие ниже:"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message) -> None:
    help_text = (
        " <b>Справка по StopPay</b>\n\n"
        "• <b>➕ Добавить подписку</b> — пошаговый мастер добавления:\n"
        "  1. Сервис (например, <i>Яндекс Плюс</i>, <i>Netflix</i>)\n"
        "  2. Стоимость и валюта (BYN, RUB, USD, PLN)\n"
        "  3. Периодичность (30 дней, 365 дней или свой интервал)\n"
        "  4. Дата следующего списания (<code>ДД.ММ.ГГГГ</code>)\n"
        "  5. Прямая ссылка для быстрой отмены сервиса\n\n"
        "• <b>📋 Мои подписки</b> — список ваших сервисов, статус активности, редактирование и удаление.\n\n"
        "• <b>📊 Аналитика</b> — годовой прогноз, средние траты в месяц и кольцевая диаграмма.\n\n"
        "• <b>🔔 Уведомления:</b>\n"
        "За 24 часа до списания бот пришлет карточку с кнопкой перехода к отмене и кнопкой отметки оплаты.\n\n"
        "Для отмены текущего действия нажмите <b>❌ Отмена</b>."
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
