import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from typing import Optional
from aiohttp import web

from config import settings
from database.session import async_session_factory, init_models
from database.models import Base
from bot.middlewares import DbSessionMiddleware, UserCheckMiddleware
from bot.handlers import common_router, subscriptions_router, analytics_router
from services.scheduler import setup_scheduler, check_and_send_reminders

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def health_check(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "service": "sub_tracker_bot"})


async def start_health_server(port: int) -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info(f"Health check HTTP server listening on port {port}")
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
