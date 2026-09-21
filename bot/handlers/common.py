from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.reply import get_main_menu_keyboard, get_webapp_url
from bot.utils.cleaner import send_clean_message
from config import settings

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    first_name = message.from_user.first_name if message.from_user else "друг"
    user_id = message.from_user.id if message.from_user else 0

    welcome_text = (
        f" Привет, <b>{first_name}</b>!\n\n"
        "<b>StopPay</b> — контроль ваших подписок в стиле Apple.\n\n"
        "• <b>Удобный Mini App</b> — управление всеми сервисами в один клик\n"
        "• <b>Кольцо расходов</b> — наглядная диаграмма и годовой прогноз трат\n"
        "• <b>4 валюты</b> — мгновенный пересчет BYN · RUB · USD · PLN\n"
        "• <b>Алерты за 24 часа</b> — бот напомнит до списания денег\n"
        "• <b>Прямая отмена</b> — переход к отмене подписки в 1 тап\n\n"
        "Нажмите кнопку <b>« Открыть StopPay»</b> ниже для входа в приложение:"
    )

    webapp_url = getattr(settings, "WEBAPP_URL", "")
    if webapp_url and user_id and getattr(message, "bot", None):
        try:
            from aiogram.types import MenuButtonWebApp, WebAppInfo
            target_url = get_webapp_url(user_id=user_id, first_name=first_name)
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
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name),
    )


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message) -> None:
    first_name = message.from_user.first_name if message.from_user else ""
    user_id = message.from_user.id if message.from_user else 0

    help_text = (
        " <b>Справка и руководство по приложению StopPay</b>\n\n"
        "StopPay работает прямо внутри Telegram в формате быстрого веб-приложения (Mini App).\n\n"
        "📱 <b>Как открыть:</b>\n"
        "Нажмите кнопку <b>« Открыть StopPay»</b> внизу экрана или кнопку меню в левом углу поля ввода текста.\n\n"
        "📊 <b>Вкладка «Обзор» (Аналитика):</b>\n"
        "• <b>Кольцо расходов:</b> интерактивная круговая диаграмма в стиле Apple Card с распределением долей сервисов.\n"
        "• <b>Прогноз бюджета:</b> автоматический расчет общих расходов за год и среднего чека в месяц.\n"
        "• <b>Календарь списаний:</b> помесячный график трат с января по декабрь.\n"
        "• <b>Мультивалютность:</b> переключатель валют в шапке (<b>Br BYN · ₽ RUB · $ USD · zł PLN</b>) с мгновенной автоконвертацией по актуальному курсу.\n\n"
        "📋 <b>Вкладка «Подписки»:</b>\n"
        "• <b>Список сервисов:</b> стоимость, период, дата следующего платежа и таймер обратного отсчета дней.\n"
        "• <b>Управление в 1 тап:</b> тумблер активности ставит подписку на паузу и возобновляет обратно без потери данных.\n"
        "• <b>Прямая отмена:</b> кнопка <b>«↗ Отменить»</b> открывает официальную страницу отказа от услуги (Яндекс, Netflix, Spotify, YouTube и др.).\n"
        "• <b>Удаление:</b> кнопка <b>«✕»</b> для удаления подписки из трекера.\n\n"
        "➕ <b>Добавление новых подписок:</b>\n"
        "• Нажмите кнопку <b>«＋ Создать»</b> в нижнем меню приложения.\n"
        "• Используйте быстрый пресет (<i>Яндекс Плюс, TG Premium, Spotify, Netflix, YouTube Premium, iCloud+</i>) или введите название вручную.\n"
        "• Укажите сумму, валюту, период (месяц, год или свое число дней) и дату следующего списания.\n\n"
        "🔔 <b>Умные напоминания:</b>\n"
        "• Бот присылает сообщение в чат ровно за 24 часа до списания средств, чтобы вы успели пополнить карту или отменить услугу.\n\n"
        "<i>Нажмите <b>« Открыть StopPay»</b> ниже для входа в приложение.</i>"
    )
    await send_clean_message(
        message,
        help_text,
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name),
    )


@router.message(Command("add", "subscriptions", "analytics"))
@router.message(F.text.in_({"➕ Добавить подписку", "📋 Мои подписки", "📊 Аналитика"}))
async def cmd_legacy_redirect(message: Message, state: FSMContext) -> None:
    await state.clear()
    first_name = message.from_user.first_name if message.from_user else ""
    user_id = message.from_user.id if message.from_user else 0
    text = (
        " <b>Управление подписками и аналитика</b>\n\n"
        "Все функции (список подписок, добавление, тумблер паузы и графики расходов) "
        "теперь находятся в приложении <b>StopPay </b>.\n\n"
        "Нажмите кнопку <b>« Открыть StopPay»</b> ниже для перехода:"
    )
    await send_clean_message(
        message,
        text,
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name),
    )


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    first_name = message.from_user.first_name if message.from_user else ""
    user_id = message.from_user.id if message.from_user else 0
    current_state = await state.get_state()
    if current_state is None:
        await send_clean_message(
            message,
            "Нет активных действий для отмены.",
            reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name),
        )
        return

    await state.clear()
    await send_clean_message(
        message,
        "Действие отменено.",
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name),
    )


@router.message(F.text)
async def fallback_text_handler(message: Message) -> None:
    first_name = message.from_user.first_name if message.from_user else ""
    user_id = message.from_user.id if message.from_user else 0
    text = (
        " Для управления подписками и просмотра аналитики откройте приложение <b>StopPay</b>.\n\n"
        "Нажмите <b>« Открыть StopPay»</b> ниже:"
    )
    await send_clean_message(
        message,
        text,
        reply_markup=get_main_menu_keyboard(user_id=user_id, first_name=first_name),
    )
