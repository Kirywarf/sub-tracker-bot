# Sub Tracker Bot (Telegram-бот для учета регулярных платежей и подписок)

Telegram-бот на базе **aiogram 3.x**, **SQLAlchemy 2.0 (async)**, **SQLite**, **APScheduler** и **matplotlib**, предназначенный для ведения учета подписок, напоминания о предстоящих списаниях за 24 часа и наглядного анализа расходов.

---

## 🚀 Возможности

1. **Добавление и управление подписками (FSM):**
   - Пошаговый сценарий добавления:
     1. Название сервиса (*Яндекс Плюс*, *YouTube Premium*, *Spotify* и др.)
     2. Стоимость и валюта: **RUB (₽)**, **BYN (Br - белорусские рубли)**, **USD ($)**, **EUR (€)**
     3. Периодичность: кнопки *Ежемесячно (30 дн.)*, *Ежегодно (365 дн.)* или произвольный интервал в днях
     4. Дата ближайшего списания в формате `ДД.ММ.ГГГГ` с валидацией
     5. Прямая ссылка на отмену подписки (опционально с валидацией URL)
   - Управление списком: просмотр карточки подписки, переключение статуса (активна / приостановлена), редактирование любого поля, удаление.

2. **Напоминания за 24 часа (APScheduler):**
   - Фоновый планировщик запускается ежедневно в 10:00 (настраивается в `.env`).
   - При `next_billing_date == tomorrow` отправляет пользователю уведомление:
     > ⚠️ **Напоминание о списании!**  
     > Завтра спишется **800 ₽** за сервис **Иви**.
   - Кнопки к уведомлению:
     - `[🔗 Отменить подписку]` — прямая ссылка на страницу отмены сервиса.
     - `[✅ Отметить оплаченным]` — переносит дату списания на следующий период (`+ period_days`).

3. **Аналитика трат за год (matplotlib):**
   - Расчет общей прогнозируемой суммы расходов за календарный год с учетом периодичности сервисов.
   - Топ-3 самых затратных сервиса.
   - Генерация круговой диаграммы (Pie Chart) структуры расходов без утечек файловых дескрипторов и памяти (`io.BytesIO` + `plt.close()`).

---

## 🛠 Стек технологий

- **Python:** 3.11+ (протестировано на Python 3.12)
- **Telegram Framework:** `aiogram 3.x`
- **База данных:** SQLite + `SQLAlchemy 2.0 (async)` (`aiosqlite`)
- **Миграции:** `Alembic`
- **Планировщик:** `APScheduler (AsyncIOScheduler)`
- **Визуализация:** `matplotlib`
- **Конфигурация:** `pydantic-settings`
- **Тесты:** `pytest`, `pytest-asyncio`, `pytest-mock`

---

## 📂 Структура проекта

```text
sub_tracker_bot/
├── bot/
│   ├── handlers/            # Обработчики команд, FSM и инлайн-кнопок
│   │   ├── common.py        # /start, /help, /cancel
│   │   ├── subscriptions.py # Добавление, просмотр, редактирование, удаление
│   │   └── analytics.py     # Аналитика и отправка графиков
│   ├── keyboards/           # Клавиатуры
│   │   ├── reply.py         # Главное меню бота
│   │   └── inline.py        # Инлайн-кнопки (валюты, периоды, карточки)
│   ├── middlewares/         # Промежуточные слои
│   │   ├── db_session.py    # Внедрение асинхронной сессии БД
│   │   └── user_check.py    # Автоматическая регистрация пользователя
│   ├── states/              # FSM состояния
│   │   └── subscription_states.py
│   └── utils/               # Валидаторы пользовательского ввода
│       └── validators.py
├── database/
│   ├── models.py            # SQLAlchemy модели (User, Subscription)
│   ├── requests.py          # CRUD операции с базой данных
│   └── session.py           # Асинхронный движок и фабрика сессий
├── services/
│   ├── scheduler.py         # Напоминания за 24 часа через APScheduler
│   └── chart_builder.py     # Построение диаграмм через matplotlib
├── alembic/                 # Миграции структуры базы данных
│   ├── versions/
│   └── env.py
├── tests/                   # Набор автоматических тестов
│   ├── test_database.py
│   ├── test_validation.py
│   ├── test_analytics.py
│   ├── test_chart_builder.py
│   ├── test_scheduler.py
│   └── test_handlers.py
├── config.py                # Загрузка конфигурации из .env
├── main.py                  # Точка входа для запуска бота
├── alembic.ini              # Конфиг Alembic
├── requirements.txt         # Зависимости проекта
├── .env.example             # Пример конфигурационного файла
└── README.md
```

---

## ⚙️ Установка и запуск

### 1. Клонирование и создание виртуального окружения
```bash
# Через uv:
uv venv .venv --python 3.12
.venv\Scripts\activate

# Или стандартный python venv:
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
# или через uv:
uv pip install -r requirements.txt
```

### 3. Настройка переменных окружения
Скопируйте `.env.example` в `.env` и укажите ваш токен бота:
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
DB_URL=sqlite+aiosqlite:///subscriptions.db
DEFAULT_TIMEZONE=UTC+3
REMINDER_HOUR=10
REMINDER_MINUTE=0
```

### 4. Применение миграций Alembic
```bash
alembic upgrade head
```

### 5. Запуск бота
```bash
python main.py
```

---

## 🧪 Запуск тестов
Все критерии готовности (DoD) покрыты автоматическими тестами:
```bash
pytest -v
```
Результат тестирования:
- 26/26 тестов успешно пройдены (база данных, валидация сумм/дат/ссылок, FSM флоу, сдвиг дат при оплате, APScheduler напоминания, генерация графиков без утечки дескрипторов).
