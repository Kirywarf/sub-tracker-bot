from typing import Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

SUPPORTED_LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "be": "🇧🇾 Беларуская",
    "en": "🇬🇧 English",
    "pl": "🇵🇱 Polski",
}

DEFAULT_LANGUAGE = "ru"

MESSAGES: Dict[str, Dict[str, str]] = {
    # --- Common ---
    "start_welcome": {
        "ru": (
            " Привет, <b>{name}</b>!\n\n"
            "<b>StopPay</b> — контроль ваших подписок в стиле Apple.\n\n"
            "• <b>Удобный Mini App</b> — управление всеми сервисами в один клик\n"
            "• <b>Кольцо расходов</b> — наглядная диаграмма и годовой прогноз трат\n"
            "• <b>4 валюты</b> — мгновенный пересчет BYN · RUB · USD · PLN\n"
            "• <b>Алерты за 24 часа</b> — бот напомнит до списания денег\n"
            "• <b>Прямая отмена</b> — переход к отмене подписки в 1 тап\n\n"
            "Нажмите кнопку <b>« Открыть StopPay»</b> ниже для входа в приложение:"
        ),
        "be": (
            " Прывітанне, <b>{name}</b>!\n\n"
            "<b>StopPay</b> — кантроль вашых падпісак у стылі Apple.\n\n"
            "• <b>Зручны Mini App</b> — кіраванне ўсімі сэрвісамі ў адзін клік\n"
            "• <b>Кола выдаткаў</b> — наглядная дыяграма і гадавы прагноз трат\n"
            "• <b>4 валюты</b> — імгненны пералік BYN · RUB · USD · PLN\n"
            "• <b>Алерты за 24 гадзіны</b> — бот нагадае перад спісаннем грошай\n"
            "• <b>Простая адмена</b> — пераход да адмены падпіскі ў 1 тап\n\n"
            "Націсніце кнопку <b>« Адкрыць StopPay»</b> ніжэй для ўваходу ў праграму:"
        ),
        "en": (
            " Hello, <b>{name}</b>!\n\n"
            "<b>StopPay</b> — Apple-style subscription tracker.\n\n"
            "• <b>Convenient Mini App</b> — manage all your services in one click\n"
            "• <b>Expense Ring</b> — interactive chart and annual forecast\n"
            "• <b>4 Currencies</b> — instant conversion for BYN · RUB · USD · PLN\n"
            "• <b>24h Alerts</b> — the bot reminds you before money is charged\n"
            "• <b>Direct Cancellation</b> — cancel subscriptions in 1 tap\n\n"
            "Tap the <b>« Open StopPay»</b> button below to launch the app:"
        ),
        "pl": (
            " Cześć, <b>{name}</b>!\n\n"
            "<b>StopPay</b> — kontrola Twoich subskrypcji w stylu Apple.\n\n"
            "• <b>Wygodny Mini App</b> — zarządzanie wszystkimi usługami jednym kliknięciem\n"
            "• <b>Pierścień wydatków</b> — przejrzysty wykres i roczna prognoza kosztów\n"
            "• <b>4 waluty</b> — natychmiastowe przeliczanie BYN · RUB · USD · PLN\n"
            "• <b>Alerty 24h</b> — bot przypomni przed pobraniem środków\n"
            "• <b>Bezpośrednia rezygnacja</b> — przejście do anulowania subskrypcji w 1 tap\n\n"
            "Kliknij przycisk <b>« Otwórz StopPay»</b> poniżej, aby wejść do aplikacji:"
        ),
    },
    "help_text": {
        "ru": (
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
            "• <b>Прямая отмена:</b> кнопка <b>«↗ Отменить»</b> открывает официальную страницу отказа от услуги.\n"
            "• <b>Удаление:</b> кнопка <b>«✕»</b> для удаления подписки из трекера.\n\n"
            "➕ <b>Добавление новых подписок:</b>\n"
            "• Нажмите кнопку <b>«＋ Создать»</b> в нижнем меню приложения.\n"
            "• Используйте быстрый пресет или введите название вручную.\n"
            "• Укажите сумму, валюту, период и дату следующего списания.\n\n"
            "🔔 <b>Умные напоминания:</b>\n"
            "• Бот присылает сообщение в чат ровно за 24 часа до списания средств.\n\n"
            "🌐 <b>Смена языка:</b>\n"
            "• Отправьте команду /language для смены языка бота (Русский, Белорусский, English, Polski).\n\n"
            "<i>Нажмите <b>« Открыть StopPay»</b> ниже для входа в приложение.</i>"
        ),
        "be": (
            " <b>Даведка і кіраўніцтва па праграме StopPay</b>\n\n"
            "StopPay працуе наўпрост унутры Telegram у фармаце хуткай вэб-праграмы (Mini App).\n\n"
            "📱 <b>Як адкрыць:</b>\n"
            "Націсніце кнопку <b>« Адкрыць StopPay»</b> унізе экрана альбо кнопку меню ў левым куце поля ўводу тэксту.\n\n"
            "📊 <b>Укладка «Агляд» (Аналітыка):</b>\n"
            "• <b>Кола выдаткаў:</b> інтэрактыўная кругавая дыяграма ў стылі Apple Card з размеркаваннем долей сэрвісаў.\n"
            "• <b>Прагноз бюджэту:</b> аўтаматычны разлік агульных выдаткаў за год і сярэдняга чэка ў месяц.\n"
            "• <b>Каляндар спісанняў:</b> памесячны графік трат са студзеня па снежань.\n"
            "• <b>Мультывалютнасць:</b> пераключальнік валют у шапцы (<b>Br BYN · ₽ RUB · $ USD · zł PLN</b>) з імгненнай аўтаканвертацыяй.\n\n"
            "📋 <b>Укладка «Падпіскі»:</b>\n"
            "• <b>Спіс сэрвісаў:</b> кошт, перыяд, дата наступнага плацяжу і адлік дзён.\n"
            "• <b>Кіраванне ў 1 тап:</b> тумблер актыўнасці ставіць падпіску на паўзу і аднаўляе назад.\n"
            "• <b>Простая адмена:</b> кнопка <b>«↗ Адмяніць»</b> адкрывае афіцыйную старонку адмовы ад сэрвісу.\n"
            "• <b>Выдаленне:</b> кнопка <b>«✕»</b> для выдалення падпіскі.\n\n"
            "➕ <b>Даданне новых падпісак:</b>\n"
            "• Націсніце кнопку <b>«＋ Стварыць»</b> у ніжнім меню праграмы.\n"
            "• Выкарыстоўвайце хуткі прэсет ці ўвядзіце назву ўручную.\n"
            "• Пазначце суму, валюту, перыяд і дату наступнага спісання.\n\n"
            "🔔 <b>Разумныя напаміны:</b>\n"
            "• Бот дасылае паведамленне ў чат роўна за 24 гадзіны да спісання грошай.\n\n"
            "🌐 <b>Змена мовы:</b>\n"
            "• Адпраўце каманду /language для змены мовы (Русский, Беларуская, English, Polski).\n\n"
            "<i>Націсніце <b>« Адкрыць StopPay»</b> ніжэй для ўваходу ў праграму.</i>"
        ),
        "en": (
            " <b>StopPay User Guide & Help</b>\n\n"
            "StopPay runs directly inside Telegram as a fast Mini App.\n\n"
            "📱 <b>How to Open:</b>\n"
            "Tap the <b>« Open StopPay»</b> button at the bottom or use the menu button in the chat.\n\n"
            "📊 <b>«Overview» Tab (Analytics):</b>\n"
            "• <b>Expense Ring:</b> interactive Apple Card-style donut chart showing your spending breakdown.\n"
            "• <b>Budget Forecast:</b> automated calculation of annual totals and monthly average.\n"
            "• <b>Payment Calendar:</b> monthly spending breakdown from January to December.\n"
            "• <b>Multi-Currency:</b> header switcher (<b>Br BYN · ₽ RUB · $ USD · zł PLN</b>) with instant live conversion.\n\n"
            "📋 <b>«Subscriptions» Tab:</b>\n"
            "• <b>Service List:</b> cost, cycle, next billing date, and countdown timer.\n"
            "• <b>1-Tap Control:</b> active toggle switch pauses and resumes subscriptions without data loss.\n"
            "• <b>Direct Cancel:</b> <b>«↗ Cancel»</b> button opens the official cancellation page.\n"
            "• <b>Delete:</b> <b>«✕»</b> button removes the subscription from the tracker.\n\n"
            "➕ <b>Adding Subscriptions:</b>\n"
            "• Tap <b>«＋ Create»</b> in the bottom app bar.\n"
            "• Use quick presets or enter service name manually.\n"
            "• Specify amount, currency, period, and next billing date.\n\n"
            "🔔 <b>Smart Reminders:</b>\n"
            "• The bot notifies you 24 hours before any charge so you can prepare or cancel.\n\n"
            "🌐 <b>Change Language:</b>\n"
            "• Send /language to switch language anytime (Russian, Belarusian, English, Polish).\n\n"
            "<i>Tap <b>« Open StopPay»</b> below to launch the app.</i>"
        ),
        "pl": (
            " <b>Przewodnik i pomoc StopPay</b>\n\n"
            "StopPay działa bezpośrednio w Telegramie jako szybka aplikacja Mini App.\n\n"
            "📱 <b>Jak otworzyć:</b>\n"
            "Kliknij przycisk <b>« Otwórz StopPay»</b> na dole ekranu lub przycisk menu w czacie.\n\n"
            "📊 <b>Zakładka «Przegląd» (Analityka):</b>\n"
            "• <b>Pierścień wydatków:</b> interaktywny wykres kołowy w stylu Apple Card z podziałem na usługi.\n"
            "• <b>Prognoza budżetu:</b> automatyczne obliczanie rocznych wydatków i średniej miesięcznej.\n"
            "• <b>Kalendarz płatności:</b> miesięczny harmonogram wydatków od stycznia do grudnia.\n"
            "• <b>Wielowalutowość:</b> przełącznik walut (<b>Br BYN · ₽ RUB · $ USD · zł PLN</b>) z natychmiastowym przeliczaniem.\n\n"
            "📋 <b>Zakładka «Subskrypcje»:</b>\n"
            "• <b>Lista usług:</b> koszt, okres, data kolejnej płatności i odliczanie dni.\n"
            "• <b>Zarządzanie 1 kliknięciem:</b> przełącznik aktywności pauzuje i wznawia subskrypcję.\n"
            "• <b>Bezpośrednie anulowanie:</b> przycisk <b>«↗ Anuluj»</b> otwiera oficjalną stronę rezygnacji.\n"
            "• <b>Usuwanie:</b> przycisk <b>«✕»</b> usuwa subskrypcję z listy.\n\n"
            "➕ <b>Dodawanie nowej subskrypcji:</b>\n"
            "• Kliknij przycisk <b>«＋ Utwórz»</b> w dolnym menu aplikacji.\n"
            "• Użyj gotowych szablonów lub wpisz nazwę ręcznie.\n"
            "• Podaj kwotę, walutę, okres i datę kolejnej płatności.\n\n"
            "🔔 <b>Inteligentne przypomnienia:</b>\n"
            "• Bot wysyła powiadomienie dokładnie 24 godziny przed pobraniem środków.\n\n"
            "🌐 <b>Zmiana języka:</b>\n"
            "• Wyślij polecenie /language, aby zmienić język (Rosyjski, Białoruski, Angielski, Polski).\n\n"
            "<i>Kliknij <b>« Otwórz StopPay»</b> poniżej, aby wejść do aplikacji.</i>"
        ),
    },
    "choose_language": {
        "ru": "🌐 <b>Выберите язык интерфейса / Select language:</b>",
        "be": "🌐 <b>Абярыце мову інтэрфейсу / Select language:</b>",
        "en": "🌐 <b>Choose your interface language:</b>",
        "pl": "🌐 <b>Wybierz język interfejsu / Select language:</b>",
    },
    "lang_changed": {
        "ru": "Язык успешно изменён на Русский 🇷🇺",
        "be": "Мова паспяхова зменена на Беларускую 🇧🇾",
        "en": "Language successfully changed to English 🇬🇧",
        "pl": "Język został pomyślnie zmieniony na Polski 🇵🇱",
    },
    "btn_open_app": {
        "ru": " Открыть StopPay",
        "be": " Адкрыць StopPay",
        "en": " Open StopPay",
        "pl": " Otwórz StopPay",
    },
    "btn_help": {
        "ru": "ℹ️ Помощь",
        "be": "ℹ️ Даведка",
        "en": "ℹ️ Help",
        "pl": "ℹ️ Pomoc",
    },
    "btn_cancel": {
        "ru": "❌ Отмена",
        "be": "❌ Адмена",
        "en": "❌ Cancel",
        "pl": "❌ Anuluj",
    },
    "btn_language": {
        "ru": "🌐 Язык",
        "be": "🌐 Мова",
        "en": "🌐 Language",
        "pl": "🌐 Język",
    },
    "cancel_no_active": {
        "ru": "Нет активных действий для отмены.",
        "be": "Няма актыўных дзеянняў для адмены.",
        "en": "No active actions to cancel.",
        "pl": "Brak aktywnych działań do anulowania.",
    },
    "cancel_success": {
        "ru": "Действие отменено.",
        "be": "Дзеянне адменена.",
        "en": "Action canceled.",
        "pl": "Działanie anulowane.",
    },
    "legacy_redirect": {
        "ru": (
            " <b>Управление подписками и аналитика</b>\n\n"
            "Все функции (список подписок, добавление, тумблер паузы и графики расходов) "
            "теперь находятся в приложении <b>StopPay </b>.\n\n"
            "Нажмите кнопку <b>« Открыть StopPay»</b> ниже для перехода:"
        ),
        "be": (
            " <b>Кіраванне падпіскамі і аналітыка</b>\n\n"
            "Усе функцыі (спіс падпісак, даданне, тумблер паўзы і графікі выдаткаў) "
            "цяпер знаходзяцца ў праграме <b>StopPay </b>.\n\n"
            "Націсніце кнопку <b>« Адкрыць StopPay»</b> ніжэй для пераходу:"
        ),
        "en": (
            " <b>Subscription Management & Analytics</b>\n\n"
            "All features (subscription list, adding, pause toggle, and spend charts) "
            "are now inside the <b>StopPay </b> app.\n\n"
            "Tap <b>« Open StopPay»</b> below to proceed:"
        ),
        "pl": (
            " <b>Zarządzanie subskrypcjami i analityka</b>\n\n"
            "Wszystkie funkcje (lista subskrypcji, dodawanie, przełącznik pauzy i wykresy wydatków) "
            "znajdują się teraz w aplikacji <b>StopPay </b>.\n\n"
            "Kliknij <b>« Otwórz StopPay»</b> poniżej, aby przejść:"
        ),
    },
    "fallback_text": {
        "ru": (
            " Для управления подписками и просмотра аналитики откройте приложение <b>StopPay</b>.\n\n"
            "Нажмите <b>« Открыть StopPay»</b> ниже:"
        ),
        "be": (
            " Для кіравання падпіскамі і прагляду аналітыкі адкрыйце праграму <b>StopPay</b>.\n\n"
            "Націсніце <b>« Адкрыць StopPay»</b> ніжэй:"
        ),
        "en": (
            " To manage subscriptions and view analytics, open the <b>StopPay</b> app.\n\n"
            "Tap <b>« Open StopPay»</b> below:"
        ),
        "pl": (
            " Aby zarządzać subskrypcjami i przeglądać analitykę, otwórz aplikację <b>StopPay</b>.\n\n"
            "Kliknij <b>« Otwórz StopPay»</b> poniżej:"
        ),
    },

    # --- Subscriptions Flow ---
    "step_service_name": {
        "ru": "Шаг 1/5: Введите <b>название сервиса</b>\n(например, <i>Яндекс</i> или <i>Netflix</i>):",
        "be": "Крок 1/5: Увядзіце <b>назву сэрвісу</b>\n(напрыклад, <i>Яндэкс</i> ці <i>Netflix</i>):",
        "en": "Step 1/5: Enter the <b>service name</b>\n(e.g., <i>Netflix</i> or <i>Spotify</i>):",
        "pl": "Krok 1/5: Wpisz <b>nazwę usługi</b>\n(np. <i>Netflix</i> lub <i>Spotify</i>):",
    },
    "step_price": {
        "ru": "Шаг 2/5: Введите <b>сумму списания</b> для <b>{name}</b>\n(например: <code>299</code>):",
        "be": "Крок 2/5: Увядзіце <b>суму спісання</b> для <b>{name}</b>\n(напрыклад: <code>299</code>):",
        "en": "Step 2/5: Enter the <b>billing amount</b> for <b>{name}</b>\n(e.g.: <code>299</code>):",
        "pl": "Krok 2/5: Wpisz <b>kwotę płatności</b> dla <b>{name}</b>\n(np.: <code>299</code>):",
    },
    "step_currency": {
        "ru": "Шаг 3/5: Выберите <b>валюту</b> списания:",
        "be": "Крок 3/5: Абярыце <b>валюту</b> спісання:",
        "en": "Step 3/5: Select the billing <b>currency</b>:",
        "pl": "Krok 3/5: Wybierz <b>walutę</b> płatności:",
    },
    "step_period": {
        "ru": "Валюта: <b>{curr_symbol} ({currency})</b>\n\nШаг 3/5: Выберите <b>периодичность</b>:",
        "be": "Валюта: <b>{curr_symbol} ({currency})</b>\n\nКрок 3/5: Абярыце <b>перыядычнасць</b>:",
        "en": "Currency: <b>{curr_symbol} ({currency})</b>\n\nStep 3/5: Select the <b>billing period</b>:",
        "pl": "Waluta: <b>{curr_symbol} ({currency})</b>\n\nKrok 3/5: Wybierz <b>okres rozliczeniowy</b>:",
    },
    "period_monthly": {
        "ru": "📅 Ежемесячно (30 дней)",
        "be": "📅 Штомесяц (30 дзён)",
        "en": "📅 Monthly (30 days)",
        "pl": "📅 Miesięcznie (30 dni)",
    },
    "period_annual": {
        "ru": "📆 Ежегодно (365 дней)",
        "be": "📆 Штогод (365 дзён)",
        "en": "📆 Annually (365 days)",
        "pl": "📆 Rocznie (365 dni)",
    },
    "period_custom": {
        "ru": "⚙️ Свой интервал (в днях)",
        "be": "⚙️ Свой інтэрвал (у днях)",
        "en": "⚙️ Custom interval (days)",
        "pl": "⚙️ Własny okres (dni)",
    },
    "custom_period_prompt": {
        "ru": "Введите количество дней (например, <code>14</code>):",
        "be": "Увядзіце колькасць дзён (напрыклад, <code>14</code>):",
        "en": "Enter the number of days (e.g., <code>14</code>):",
        "pl": "Wpisz liczbę dni (np. <code>14</code>):",
    },
    "step_billing_date": {
        "ru": "Период: <b>{days} дн.</b>\n\nШаг 4/5: Введите <b>дату списания</b> (<code>ДД.ММ.ГГГГ</code>):",
        "be": "Перыяд: <b>{days} дн.</b>\n\nКрок 4/5: Увядзіце <b>дату спісання</b> (<code>ДД.ММ.ГГГГ</code>):",
        "en": "Period: <b>{days} days</b>\n\nStep 4/5: Enter the <b>billing date</b> (<code>DD.MM.YYYY</code>):",
        "pl": "Okres: <b>{days} dni</b>\n\nKrok 4/5: Wpisz <b>datę płatności</b> (<code>DD.MM.RRRR</code>):",
    },
    "step_cancel_url": {
        "ru": "Дата списания: <b>{date}</b>\n\nШаг 5/5: Отправьте <b>ссылку на отмену</b> или пропустите:",
        "be": "Дата спісання: <b>{date}</b>\n\nКрок 5/5: Дашліце <b>спасылку на адмену</b> альбо прапусціце:",
        "en": "Billing date: <b>{date}</b>\n\nStep 5/5: Send the <b>cancellation link</b> or skip:",
        "pl": "Data płatności: <b>{date}</b>\n\nKrok 5/5: Prześlij <b>link do rezygnacji</b> lub pomiń:",
    },
    "btn_skip": {
        "ru": "➡️ Пропустить",
        "be": "➡️ Прапусціць",
        "en": "➡️ Skip",
        "pl": "➡️ Pomiń",
    },
    "sub_saved": {
        "ru": "🎉 <b>Подписка успешно сохранена!</b>\n\n",
        "be": "🎉 <b>Падпіска паспяхова захавана!</b>\n\n",
        "en": "🎉 <b>Subscription successfully saved!</b>\n\n",
        "pl": "🎉 <b>Subskrypcja została pomyślnie zapisana!</b>\n\n",
    },
    "skip_prompt_hint": {
        "ru": "Если хотите пропустить этот шаг, нажмите кнопку ниже:",
        "be": "Калі жадаеце прапусціць гэты крок, націсніце кнопку ніжэй:",
        "en": "If you want to skip this step, click the button below:",
        "pl": "Jeśli chcesz pominąć ten krok, kliknij przycisk poniżej:",
    },

    # --- Sub Card Formatting ---
    "status_active": {
        "ru": "● Активна",
        "be": "● Актыўная",
        "en": "● Active",
        "pl": "● Aktywna",
    },
    "status_paused": {
        "ru": "○ На паузе",
        "be": "○ На паўзе",
        "en": "○ Paused",
        "pl": "○ Wstrzymana",
    },
    "days_left_in": {
        "ru": "через {days} дн.",
        "be": "праз {days} дн.",
        "en": "in {days} d.",
        "pl": "za {days} dni",
    },
    "days_left_today": {
        "ru": "сегодня",
        "be": "сёння",
        "en": "today",
        "pl": "dzisiaj",
    },
    "days_left_overdue": {
        "ru": "просрочено на {days} дн.",
        "be": "пратэрмінавана на {days} дн.",
        "en": "overdue by {days} d.",
        "pl": "przeterminowane o {days} dni",
    },
    "card_amount_line": {
        "ru": "• Сумма: <b>{price} {curr}</b> / {days} дн.",
        "be": "• Сума: <b>{price} {curr}</b> / {days} дн.",
        "en": "• Amount: <b>{price} {curr}</b> / {days} d.",
        "pl": "• Kwota: <b>{price} {curr}</b> / {days} dni",
    },
    "card_billing_line": {
        "ru": "• Списание: <b>{date}</b> ({days_str})",
        "be": "• Спісанне: <b>{date}</b> ({days_str})",
        "en": "• Billing: <b>{date}</b> ({days_str})",
        "pl": "• Płatność: <b>{date}</b> ({days_str})",
    },
    "card_cancel_link_line": {
        "ru": "• Ссылка: <a href=\"{url}\">Отменить подписку</a>",
        "be": "• Спасылка: <a href=\"{url}\">Адмяніць падпіску</a>",
        "en": "• Link: <a href=\"{url}\">Cancel subscription</a>",
        "pl": "• Link: <a href=\"{url}\">Anuluj subskrypcję</a>",
    },

    # --- Subscriptions List ---
    "no_subscriptions": {
        "ru": "У вас пока нет добавленных подписок.\n\nНажмите кнопку ниже, чтобы добавить первую:",
        "be": "У вас пакуль няма дададзеных падпісак.\n\nНацісніце кнопку ніжэй, каб дадаць першую:",
        "en": "You have no subscriptions added yet.\n\nClick the button below to add your first one:",
        "pl": "Nie masz jeszcze dodanych subskrypcji.\n\nKliknij przycisk poniżej, aby dodać pierwszą:",
    },
    "subs_list_title": {
        "ru": "📋 <b>Ваши подписки ({count}):</b>\n\nНажмите на сервис для управления:",
        "be": "📋 <b>Вашы падпіскі ({count}):</b>\n\nНацісніце на сэрвіс для кіравання:",
        "en": "📋 <b>Your subscriptions ({count}):</b>\n\nClick on a service to manage:",
        "pl": "📋 <b>Twoje subskrypcje ({count}):</b>\n\nKliknij usługę, aby nią zarządzać:",
    },
    "btn_add_sub": {
        "ru": "＋ Добавить подписку",
        "be": "＋ Дадаць падпіску",
        "en": "＋ Add subscription",
        "pl": "＋ Dodaj subskrypcję",
    },
    "btn_edit": {
        "ru": "✏️ Редактировать",
        "be": "✏️ Рэдагаваць",
        "en": "✏️ Edit",
        "pl": "✏️ Edytuj",
    },
    "btn_delete": {
        "ru": "✕ Удалить",
        "be": "✕ Выдаліць",
        "en": "✕ Delete",
        "pl": "✕ Usuń",
    },
    "btn_pause": {
        "ru": "○ Приостановить",
        "be": "○ Прыпыніць",
        "en": "○ Pause",
        "pl": "○ Wstrzymaj",
    },
    "btn_activate": {
        "ru": "● Активировать",
        "be": "● Актываваць",
        "en": "● Activate",
        "pl": "● Aktywuj",
    },
    "btn_back_to_list": {
        "ru": "‹ К списку",
        "be": "‹ Да спісу",
        "en": "‹ Back to list",
        "pl": "‹ Do listy",
    },
    "btn_cancel_url_page": {
        "ru": "🔗 Страница отмены сервиса",
        "be": "🔗 Старонка адмены сэрвісу",
        "en": "🔗 Cancellation page",
        "pl": "🔗 Strona rezygnacji",
    },
    "btn_open_stoppay_app": {
        "ru": " Открыть StopPay App",
        "be": " Адкрыць StopPay App",
        "en": " Open StopPay App",
        "pl": " Otwórz StopPay App",
    },
    "delete_prompt": {
        "ru": "Вы действительно хотите удалить подписку <b>{name}</b>?",
        "be": "Вы сапраўды хочаце выдаліць падпіску <b>{name}</b>?",
        "en": "Are you sure you want to delete subscription <b>{name}</b>?",
        "pl": "Czy na pewno chcesz usunąć subskrypcję <b>{name}</b>?",
    },
    "btn_confirm_delete": {
        "ru": "✕ Да, удалить",
        "be": "✕ Так, выдаліць",
        "en": "✕ Yes, delete",
        "pl": "✕ Tak, usuń",
    },
    "btn_cancel_modal": {
        "ru": "Отмена",
        "be": "Адмена",
        "en": "Cancel",
        "pl": "Anuluj",
    },
    "sub_deleted_alert": {
        "ru": "Подписка удалена.",
        "be": "Падпіска выдалена.",
        "en": "Subscription deleted.",
        "pl": "Subskrypcja usunięta.",
    },
    "sub_not_found": {
        "ru": "Подписка не найдена.",
        "be": "Падпіска не знойдзена.",
        "en": "Subscription not found.",
        "pl": "Nie znaleziono subskrypcji.",
    },
    "sub_status_activated": {
        "ru": "Подписка активирована!",
        "be": "Падпіска актывавана!",
        "en": "Subscription activated!",
        "pl": "Subskrypcja aktywowana!",
    },
    "sub_status_paused": {
        "ru": "Подписка приостановлена!",
        "be": "Падпіска прыпынена!",
        "en": "Subscription paused!",
        "pl": "Subskrypcja wstrzymana!",
    },

    # --- Editing ---
    "edit_field_prompt": {
        "ru": "Какое поле для подписки <b>{name}</b> вы хотите изменить?",
        "be": "Якое поле для падпіскі <b>{name}</b> вы хочаце змяніць?",
        "en": "Which field for subscription <b>{name}</b> do you want to edit?",
        "pl": "Które pole dla subskrypcji <b>{name}</b> chcesz zmienić?",
    },
    "field_name": {
        "ru": "Название", "be": "Назва", "en": "Name", "pl": "Nazwa",
    },
    "field_price": {
        "ru": "Сумма", "be": "Сума", "en": "Amount", "pl": "Kwota",
    },
    "field_currency": {
        "ru": "Валюта", "be": "Валюта", "en": "Currency", "pl": "Waluta",
    },
    "field_period": {
        "ru": "Период", "be": "Перыяд", "en": "Period", "pl": "Okres",
    },
    "field_date": {
        "ru": "Дата списания", "be": "Дата спісання", "en": "Billing date", "pl": "Data płatności",
    },
    "field_url": {
        "ru": "Ссылка отмены", "be": "Спасылка адмены", "en": "Cancel link", "pl": "Link rezygnacji",
    },
    "btn_back_to_card": {
        "ru": "‹ Назад к карточке",
        "be": "‹ Назад да карткі",
        "en": "‹ Back to card",
        "pl": "‹ Wróć do karty",
    },
    "prompt_edit_name": {
        "ru": "Введите новое <b>название сервиса</b>:",
        "be": "Увядзіце новую <b>назву сэрвісу</b>:",
        "en": "Enter the new <b>service name</b>:",
        "pl": "Wpisz nową <b>nazwę usługi</b>:",
    },
    "prompt_edit_price": {
        "ru": "Введите новую <b>стоимость</b> (число):",
        "be": "Увядзіце новы <b>кошт</b> (лік):",
        "en": "Enter the new <b>amount</b> (number):",
        "pl": "Wpisz nową <b>kwotę</b> (liczba):",
    },
    "prompt_edit_period": {
        "ru": "Введите новый <b>интервал списания в днях</b> (например, 30 или 365):",
        "be": "Увядзіце новы <b>інтэрвал спісання ў днях</b> (напрыклад, 30 ці 365):",
        "en": "Enter the new <b>billing interval in days</b> (e.g., 30 or 365):",
        "pl": "Wpisz nowy <b>okres rozliczeniowy w dniach</b> (np. 30 lub 365):",
    },
    "prompt_edit_date": {
        "ru": "Введите новую <b>дату следующего списания</b> (ДД.ММ.ГГГГ):",
        "be": "Увядзіце новую <b>дату наступнага спісання</b> (ДД.ММ.ГГГГ):",
        "en": "Enter the new <b>next billing date</b> (DD.MM.YYYY):",
        "pl": "Wpisz nową <b>datę kolejnej płatności</b> (DD.MM.RRRR):",
    },
    "prompt_edit_url": {
        "ru": "Введите новую <b>ссылку на отмену</b> (или отправьте '-' чтобы очистить):",
        "be": "Увядзіце новую <b>спасылку на адмену</b> (альбо дашліце '-' каб ачысціць):",
        "en": "Enter the new <b>cancellation link</b> (or send '-' to clear):",
        "pl": "Wpisz nowy <b>link do rezygnacji</b> (lub wyślij '-' aby wyczyścić):",
    },
    "select_new_currency": {
        "ru": "Выберите новую валюту:",
        "be": "Абярыце новую валюту:",
        "en": "Select new currency:",
        "pl": "Wybierz nową walutę:",
    },
    "currency_changed_alert": {
        "ru": "Валюта изменена на {curr}",
        "be": "Валюта зменена на {curr}",
        "en": "Currency changed to {curr}",
        "pl": "Waluta zmieniona na {curr}",
    },
    "changes_saved": {
        "ru": "✅ <b>Изменения сохранены!</b>\n\n",
        "be": "✅ <b>Змены захаваны!</b>\n\n",
        "en": "✅ <b>Changes saved!</b>\n\n",
        "pl": "✅ <b>Zmiany zapisane!</b>\n\n",
    },

    # --- Reminders ---
    "reminder_alert": {
        "ru": " <b>Напоминание о списании!</b>\nЗавтра: <b>{price}</b> · <b>{service}</b>",
        "be": " <b>Напамін пра спісанне!</b>\nЗаўтра: <b>{price}</b> · <b>{service}</b>",
        "en": " <b>Payment Reminder!</b>\nTomorrow: <b>{price}</b> · <b>{service}</b>",
        "pl": " <b>Przypomnienie o płatności!</b>\nJutro: <b>{price}</b> · <b>{service}</b>",
    },
    "btn_mark_paid": {
        "ru": "✅ Отметить оплаченным",
        "be": "✅ Адзначыць аплачаным",
        "en": "✅ Mark as paid",
        "pl": "✅ Oznacz jako opłacone",
    },
    "btn_reminder_cancel": {
        "ru": "🔗 Отменить подписку",
        "be": "🔗 Адмяніць падпіску",
        "en": "🔗 Cancel subscription",
        "pl": "🔗 Anuluj subskrypcję",
    },
    "paid_marked_alert": {
        "ru": "Оплата отмечена!",
        "be": "Аплата адзначана!",
        "en": "Payment marked!",
        "pl": "Płatność oznaczona!",
    },
    "paid_marked_text": {
        "ru": (
            "✅ <b>Оплата отмечена!</b>\n\n"
            "Сервис <b>{name}</b> оплачен.\n"
            "Следующее списание запланировано на <b>{date}</b>."
        ),
        "be": (
            "✅ <b>Аплата адзначана!</b>\n\n"
            "Сэрвіс <b>{name}</b> аплачаны.\n"
            "Наступнае спісанне запланавана на <b>{date}</b>."
        ),
        "en": (
            "✅ <b>Payment marked!</b>\n\n"
            "Service <b>{name}</b> has been paid.\n"
            "Next billing is scheduled for <b>{date}</b>."
        ),
        "pl": (
            "✅ <b>Płatność oznaczona!</b>\n\n"
            "Usługa <b>{name}</b> została opłacona.\n"
            "Następna płatność zaplanowana na <b>{date}</b>."
        ),
    },

    # --- Analytics ---
    "analytics_title": {
        "ru": " <b>Аналитика регулярных расходов</b>",
        "be": " <b>Аналітыка рэгулярных выдаткаў</b>",
        "en": " <b>Recurring Expense Analytics</b>",
        "pl": " <b>Analityka wydatków cyklicznych</b>",
    },
    "analytics_all_converted": {
        "ru": "Все расходы приведены к: {curr}",
        "be": "Усе выдаткі прыведзены да: {curr}",
        "en": "All expenses converted to: {curr}",
        "pl": "Wszystkie wydatki przeliczone na: {curr}",
    },
    "analytics_in_year": {
        "ru": "• В год: <b>{amount} {curr}</b>",
        "be": "• У год: <b>{amount} {curr}</b>",
        "en": "• Per year: <b>{amount} {curr}</b>",
        "pl": "• Rocznie: <b>{amount} {curr}</b>",
    },
    "analytics_in_month": {
        "ru": "• В месяц: <b>{amount} {curr}</b>",
        "be": "• У месяц: <b>{amount} {curr}</b>",
        "en": "• Per month: <b>{amount} {curr}</b>",
        "pl": "• Miesięcznie: <b>{amount} {curr}</b>",
    },
    "analytics_subs_count": {
        "ru": "• Подписок: <b>{count}</b>",
        "be": "• Падпісак: <b>{count}</b>",
        "en": "• Subscriptions: <b>{count}</b>",
        "pl": "• Subskrypcji: <b>{count}</b>",
    },
    "analytics_top_title": {
        "ru": "<b>Топ затратных сервисов:</b>",
        "be": "<b>Топ самых дарагіх сэрвісаў:</b>",
        "en": "<b>Top expense services:</b>",
        "pl": "<b>Najdroższe usługi:</b>",
    },
    "analytics_year_short": {
        "ru": "/год",
        "be": "/год",
        "en": "/yr",
        "pl": "/rok",
    },
    "analytics_switch_hint": {
        "ru": "<i>Валюту можно переключить ниже:</i>",
        "be": "<i>Валюту можна пераключыць ніжэй:</i>",
        "en": "<i>You can switch currency below:</i>",
        "pl": "<i>Możesz zmienić walutę poniżej:</i>",
    },
    "analytics_btn_interactive": {
        "ru": " Интерактивная аналитика",
        "be": " Інтэрактыўная аналітыка",
        "en": " Interactive analytics",
        "pl": " Interaktywna analityka",
    },
    "analytics_empty": {
        "ru": (
            " <b>Аналитика расходов</b>\n\n"
            "У вас пока нет активных подписок.\n"
            "Добавьте подписку, и здесь появится аналитика."
        ),
        "be": (
            " <b>Аналітыка выдаткаў</b>\n\n"
            "У вас пакуль няма актыўных падпісак.\n"
            "Дадайце падпіску, і тут з'явіцца аналітыка."
        ),
        "en": (
            " <b>Expense Analytics</b>\n\n"
            "You don't have any active subscriptions yet.\n"
            "Add a subscription to see analytics here."
        ),
        "pl": (
            " <b>Analityka wydatków</b>\n\n"
            "Nie masz jeszcze aktywnych subskrypcji.\n"
            "Dodaj subskrypcję, aby zobaczyć analitykę."
        ),
    },
    "analytics_no_active_alert": {
        "ru": "Нет активных подписок для анализа",
        "be": "Няма актыўных падпісак для аналізу",
        "en": "No active subscriptions for analysis",
        "pl": "Brak aktywnych subskrypcji do analizy",
    },
    "analytics_switched_alert": {
        "ru": "Переключено на {curr}",
        "be": "Пераключана на {curr}",
        "en": "Switched to {curr}",
        "pl": "Przełączono na {curr}",
    },

    # --- Validators ---
    "val_err_name_empty": {
        "ru": "Название сервиса не может быть пустым. Пожалуйста, введите название.",
        "be": "Назва сэрвісу не можа быць пустой. Калі ласка, увядзіце назву.",
        "en": "Service name cannot be empty. Please enter a name.",
        "pl": "Nazwa usługi nie może być pusta. Proszę podać nazwę.",
    },
    "val_err_name_toolong": {
        "ru": "Слишком длинное название (максимум 100 символов). Попробуйте сократить.",
        "be": "Занадта доўгая назва (максімум 100 сімвалаў). Паспрабуйце скараціць.",
        "en": "Name is too long (maximum 100 characters). Please shorten it.",
        "pl": "Zbyt długa nazwa (maksymalnie 100 znaków). Proszę ją skrócić.",
    },
    "val_err_price_invalid": {
        "ru": "Некорректный формат суммы. Введите число (например, <code>299</code> или <code>850.50</code>).",
        "be": "Няправільны фармат сумы. Увядзіце лік (напрыклад, <code>299</code> альбо <code>850.50</code>).",
        "en": "Invalid amount format. Enter a number (e.g. <code>299</code> or <code>850.50</code>).",
        "pl": "Nieprawidłowy format kwoty. Wpisz liczbę (np. <code>299</code> lub <code>850.50</code>).",
    },
    "val_err_price_positive": {
        "ru": "Сумма списания должна быть больше нуля.",
        "be": "Сума спісання павінна быць большая за нуль.",
        "en": "Billing amount must be greater than zero.",
        "pl": "Kwota płatności musi być większa od zera.",
    },
    "val_err_price_toobig": {
        "ru": "Слишком большая сумма (максимум 10 000 000). Проверьте введенное значение.",
        "be": "Занадта вялікая сума (максімум 10 000 000). Праверце ўведзенае значэнне.",
        "en": "Amount is too large (maximum 10,000,000). Please check your input.",
        "pl": "Zbyt duża kwota (maksymalnie 10 000 000). Sprawdź wprowadzoną wartość.",
    },
    "val_err_period_digits": {
        "ru": "Интервал должен быть целым положительным числом дней (например, <code>30</code> или <code>14</code>).",
        "be": "Інтэрвал павінен быць цэлым станоўчым лікам дзён (напрыклад, <code>30</code> альбо <code>14</code>).",
        "en": "Interval must be a positive integer number of days (e.g. <code>30</code> or <code>14</code>).",
        "pl": "Okres musi być dodatnią liczbą całkowitą dni (np. <code>30</code> lub <code>14</code>).",
    },
    "val_err_period_min": {
        "ru": "Интервал должен быть не менее 1 дня.",
        "be": "Інтэрвал павінен быць не менш за 1 дзень.",
        "en": "Interval must be at least 1 day.",
        "pl": "Okres musi wynosić co najmniej 1 dzień.",
    },
    "val_err_period_max": {
        "ru": "Интервал не может превышать 3650 дней (10 лет).",
        "be": "Інтэрвал не можа перавышаць 3650 дзён (10 гадоў).",
        "en": "Interval cannot exceed 3650 days (10 years).",
        "pl": "Okres nie może przekraczać 3650 dni (10 lat).",
    },
    "val_err_date_format": {
        "ru": "Неверный формат даты. Пожалуйста, укажите дату в формате <code>ДД.ММ.ГГГГ</code> (например, <code>25.12.2026</code>).",
        "be": "Няправільны фармат даты. Калі ласка, пазначце дату ў фармаце <code>ДД.ММ.ГГГГ</code> (напрыклад, <code>25.12.2026</code>).",
        "en": "Invalid date format. Please specify the date in <code>DD.MM.YYYY</code> format (e.g. <code>25.12.2026</code>).",
        "pl": "Nieprawidłowy format daty. Proszę podać datę w formacie <code>DD.MM.RRRR</code> (np. <code>25.12.2026</code>).",
    },
    "val_err_date_range": {
        "ru": "Год должен быть в диапазоне от 2000 до 2100.",
        "be": "Год павінен быць у дыяпазоне ад 2000 да 2100.",
        "en": "Year must be between 2000 and 2100.",
        "pl": "Rok musi mieścić się w przedziale od 2000 do 2100.",
    },
    "val_err_url": {
        "ru": "Некорректная ссылка! Ссылка должна начинаться с <code>https://</code> или <code>http://</code> (например: <code>https://plus.yandex.ru</code>).",
        "be": "Няправільная спасылка! Спасылка павінна пачынацца з <code>https://</code> ці <code>http://</code> (напрыклад: <code>https://plus.yandex.ru</code>).",
        "en": "Invalid URL! The link must start with <code>https://</code> or <code>http://</code> (e.g.: <code>https://netflix.com</code>).",
        "pl": "Nieprawidłowy link! Link musi zaczynać się od <code>https://</code> lub <code>http://</code> (np.: <code>https://netflix.com</code>).",
    },
}


def normalize_language(lang: str) -> str:
    """Normalizes language code to one of the supported ones, falling back to 'ru'."""
    if not lang:
        return DEFAULT_LANGUAGE
    code = lang.strip().lower()
    if code in SUPPORTED_LANGUAGES:
        return code
    if code.startswith("be"):
        return "be"
    if code.startswith("en"):
        return "en"
    if code.startswith("pl"):
        return "pl"
    if code.startswith("ru"):
        return "ru"
    return DEFAULT_LANGUAGE


def get_text(key: str, lang: str = "ru", **kwargs: Any) -> str:
    """Retrieves localized text by key and language code with fallback to Russian."""
    norm_lang = normalize_language(lang)
    entry = MESSAGES.get(key)
    if not entry:
        return f"[{key}]"
    text = entry.get(norm_lang) or entry.get(DEFAULT_LANGUAGE) or next(iter(entry.values()))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def get_language_keyboard(current_lang: str = "ru") -> InlineKeyboardMarkup:
    """Returns an inline keyboard with the 4 supported languages."""
    norm_lang = normalize_language(current_lang)
    buttons = []
    row = []
    for code, title in SUPPORTED_LANGUAGES.items():
        label = f"• {title} •" if code == norm_lang else title
        row.append(InlineKeyboardButton(text=label, callback_data=f"set_lang_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)
