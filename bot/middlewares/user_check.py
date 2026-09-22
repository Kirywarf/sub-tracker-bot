from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession
from database.requests import get_or_create_user


from bot.locales import normalize_language


class UserCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")
        tg_user: TgUser = data.get("event_from_user")

        if session and tg_user and not tg_user.is_bot:
            detected_lang = normalize_language(tg_user.language_code)
            db_user = await get_or_create_user(
                session=session,
                telegram_id=tg_user.id,
                username=tg_user.username,
                language=detected_lang,
            )
            data["db_user"] = db_user
            data["user_lang"] = getattr(db_user, "language", "ru")
        else:
            data.setdefault("user_lang", "ru")

        return await handler(event, data)
