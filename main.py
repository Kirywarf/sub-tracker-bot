import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from typing import Optional
from aiohttp import web

from datetime import date
from config import settings, BASE_DIR
from database.session import async_session_factory, init_models
from database.models import Base
from database.requests import (
    get_user_subscriptions,
    add_subscription,
    toggle_subscription_status,
    delete_subscription,
    get_or_create_user,
)
from bot.handlers.analytics import calculate_unified_metrics
from services.currency import get_exchange_rates
from bot.middlewares import DbSessionMiddleware, UserCheckMiddleware
from bot.handlers import common_router, subscriptions_router, analytics_router
from services.scheduler import setup_scheduler, check_and_send_reminders

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def health_check(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "service": "sub_tracker_bot"})


async def serve_index(request: web.Request) -> web.Response:
    if request.headers.get("Accept") == "application/json":
        return web.json_response({"status": "ok", "service": "sub_tracker_bot"})
    index_path = BASE_DIR / "web" / "index.html"
    if index_path.exists():
        return web.FileResponse(index_path)
    return web.json_response({"status": "ok", "service": "sub_tracker_bot"})


async def api_get_subscriptions(request: web.Request) -> web.Response:
    user_id_param = request.query.get("user_id")
    target_curr = request.query.get("currency", "RUB").upper().strip()

    if not user_id_param:
        demo_subs = [
            {"id": 1, "service_name": "Яндекс Плюс", "price": 299.0, "currency": "RUB", "period_days": 30, "next_billing_date": "2026-10-15", "is_active": True, "cancel_url": "https://plus.yandex.ru"},
            {"id": 2, "service_name": "Netflix", "price": 14.99, "currency": "USD", "period_days": 30, "next_billing_date": "2026-10-25", "is_active": True, "cancel_url": "https://netflix.com/cancel"},
            {"id": 3, "service_name": "Spotify", "price": 19.99, "currency": "PLN", "period_days": 30, "next_billing_date": "2026-11-01", "is_active": True, "cancel_url": "https://spotify.com/account"},
            {"id": 4, "service_name": "Telegram Premium", "price": 14.99, "currency": "BYN", "period_days": 30, "next_billing_date": "2026-10-20", "is_active": True, "cancel_url": "https://telegram.org"},
        ]
        rates = await get_exchange_rates()
        from types import SimpleNamespace
        mock_subs = [SimpleNamespace(**s) for s in demo_subs]
        metrics = calculate_unified_metrics(mock_subs, target_currency=target_curr, rates=rates)
        return web.json_response({
            "status": "ok",
            "is_demo": True,
            "subscriptions": demo_subs,
            "metrics": {
                "total_annual": metrics["total_annual"],
                "monthly_avg": metrics["monthly_avg"],
                "services_count": metrics["services_count"],
                "target_currency": metrics["target_currency"],
                "services": metrics["services"],
            },
        })

    try:
        user_id = int(user_id_param)
    except ValueError:
        return web.json_response({"status": "error", "message": "Invalid user_id"}, status=400)

    async with async_session_factory() as session:
        subs = await get_user_subscriptions(session, user_id=user_id)
        rates = await get_exchange_rates()
        metrics = calculate_unified_metrics(subs, target_currency=target_curr, rates=rates)
        subs_list = [
            {
                "id": s.id,
                "service_name": s.service_name,
                "price": s.price,
                "currency": s.currency,
                "period_days": s.period_days,
                "next_billing_date": s.next_billing_date.isoformat(),
                "is_active": s.is_active,
                "cancel_url": s.cancel_url,
            }
            for s in subs
        ]
        return web.json_response({
            "status": "ok",
            "is_demo": False,
            "subscriptions": subs_list,
            "metrics": {
                "total_annual": metrics["total_annual"],
                "monthly_avg": metrics["monthly_avg"],
                "services_count": metrics["services_count"],
                "target_currency": metrics["target_currency"],
                "services": metrics["services"],
            },
        })


async def api_create_subscription(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        user_id = int(data.get("user_id", 0))
        if not user_id:
            return web.json_response({"status": "error", "message": "user_id is required"}, status=400)

        billing_date = date.fromisoformat(data["next_billing_date"])
        async with async_session_factory() as session:
            await get_or_create_user(session, telegram_id=user_id, username=data.get("username"))
            sub = await add_subscription(
                session=session,
                user_id=user_id,
                service_name=data["service_name"],
                price=float(data["price"]),
                currency=data.get("currency", "RUB").upper().strip(),
                period_days=int(data.get("period_days", 30)),
                next_billing_date=billing_date,
                cancel_url=data.get("cancel_url") or None,
            )
            return web.json_response({"status": "ok", "sub_id": sub.id})
    except Exception as e:
        logger.error(f"Error creating subscription via API: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=400)


async def api_toggle_subscription(request: web.Request) -> web.Response:
    try:
        sub_id = int(request.match_info["id"])
        async with async_session_factory() as session:
            updated = await toggle_subscription_status(session, sub_id)
            if not updated:
                return web.json_response({"status": "error", "message": "Not found"}, status=404)
            return web.json_response({"status": "ok", "is_active": updated.is_active})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=400)


async def api_delete_subscription(request: web.Request) -> web.Response:
    try:
        sub_id = int(request.match_info["id"])
        async with async_session_factory() as session:
            success = await delete_subscription(session, sub_id)
            return web.json_response({"status": "ok" if success else "not_found"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=400)


@web.middleware
async def cors_middleware(request: web.Request, handler):
    if request.method == "OPTIONS":
        resp = web.Response(status=200)
    else:
        resp = await handler(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
    return resp


async def start_health_server(port: int) -> web.AppRunner:
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get("/", serve_index)
    app.router.add_get("/health", health_check)
    app.router.add_get("/app", serve_index)
    app.router.add_get("/api/subscriptions", api_get_subscriptions)
    app.router.add_post("/api/subscriptions", api_create_subscription)
    app.router.add_post("/api/subscriptions/{id}/toggle", api_toggle_subscription)
    app.router.add_delete("/api/subscriptions/{id}", api_delete_subscription)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info(f"Health check & WebApp HTTP server listening on port {port}")
    return runner


async def main() -> None:
    logger.info("Initializing Sub Tracker Bot...")

    # Start health check server if PORT is specified (e.g. Render Web Service)
    health_runner: Optional[web.AppRunner] = None
    if settings.PORT > 0:
        health_runner = await start_health_server(settings.PORT)

    # Check BOT_TOKEN configuration
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz":
        logger.error(
            "CRITICAL: BOT_TOKEN is missing or set to default placeholder! "
            "Please configure BOT_TOKEN in Render Environment variables."
        )

    # Ensure database schema is ready (with retry for Neon serverless cold starts)
    import re
    masked_db = re.sub(r':([^@]+)@', ':****@', settings.DB_URL)
    logger.info(f"Target database: {masked_db}")
    logger.info("Connecting to database and verifying schema...")
    for attempt in range(1, 4):
        try:
            await init_models()
            logger.info("Database schema initialized successfully.")
            break
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt}/3 failed: {e}")
            if attempt < 3:
                await asyncio.sleep(2)
            else:
                logger.error("=" * 60)
                logger.error(f"CRITICAL: Failed to connect to database: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Database target was: {masked_db}")
                logger.error("=" * 60)
                raise

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register Middlewares
    db_middleware = DbSessionMiddleware(async_session_factory)
    user_middleware = UserCheckMiddleware()

    # Outer middleware for database session across all messages and callbacks
    dp.message.outer_middleware(db_middleware)
    dp.callback_query.outer_middleware(db_middleware)

    # Middleware for user check & registration
    dp.message.middleware(user_middleware)
    dp.callback_query.middleware(user_middleware)

    # Register Routers
    dp.include_router(common_router)
    dp.include_router(subscriptions_router)
    dp.include_router(analytics_router)

    # Setup APScheduler
    scheduler = setup_scheduler(bot, async_session_factory)
    scheduler.start()
    logger.info("APScheduler started successfully.")

    try:
        if settings.WEBAPP_URL:
            try:
                from aiogram.types import MenuButtonWebApp, WebAppInfo
                await bot.set_chat_menu_button(
                    menu_button=MenuButtonWebApp(
                        text="StopPay ",
                        web_app=WebAppInfo(url=settings.WEBAPP_URL),
                    )
                )
                logger.info(f"Telegram chat menu button configured: {settings.WEBAPP_URL}")
            except Exception as mb_err:
                logger.warning(f"Could not set chat menu button: {mb_err}")

        logger.info("Bot is polling for updates...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down...")
        if health_runner:
            await health_runner.cleanup()
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
