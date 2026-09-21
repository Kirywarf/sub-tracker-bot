import logging
from typing import Dict, List, Optional, Any
from aiogram import Bot
from aiogram.types import Message

logger = logging.getLogger(__name__)

# Map chat_id -> list of message IDs to clean up on the next screen/action
_chat_active_messages: Dict[int, List[int]] = {}


async def safe_delete(bot: Optional[Bot], chat_id: int, message_id: int) -> None:
    """Safely deletes a message by id without raising exceptions if already deleted or forbidden."""
    if not bot:
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.debug(f"Could not delete message {message_id} in {chat_id}: {e}")


async def delete_user_message(message: Message) -> None:
    """Safely deletes the user's incoming message to keep the chat history spotless."""
    try:
        await message.delete()
    except Exception as e:
        logger.debug(f"Could not delete user message {getattr(message, 'message_id', None)}: {e}")


async def cleanup_previous_bot_messages(bot: Optional[Bot], chat_id: int) -> None:
    """Deletes all previously tracked bot messages in the specified chat."""
    if not bot:
        return
    msg_ids = _chat_active_messages.pop(chat_id, [])
    for mid in msg_ids:
        await safe_delete(bot, chat_id, mid)


def track_message(chat_id: int, message_id: int) -> None:
    """Registers a message ID to be removed when a new screen is presented."""
    if chat_id not in _chat_active_messages:
        _chat_active_messages[chat_id] = []
    _chat_active_messages[chat_id].append(message_id)


async def send_clean_message(
    message: Message,
    text: str,
    reply_markup=None,
    parse_mode: str = "HTML",
    delete_trigger: bool = True,
    clean_previous: bool = True,
) -> Message:
    """
    Deletes the trigger message and previous messages, sends a new message,
    and registers it for future auto-cleanup.
    """
    bot = getattr(message, "bot", None)
    chat_id = getattr(getattr(message, "chat", None), "id", 0)

    if delete_trigger:
        await delete_user_message(message)

    if clean_previous and bot and chat_id:
        await cleanup_previous_bot_messages(bot, chat_id)

    sent = await message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)

    if sent and hasattr(sent, "message_id") and chat_id:
        try:
            mid = int(sent.message_id)
            track_message(chat_id, mid)
        except (ValueError, TypeError):
            pass

    return sent


async def send_clean_photo(
    message: Message,
    photo: Any,
    caption: str = "",
    reply_markup=None,
    parse_mode: str = "HTML",
    delete_trigger: bool = True,
    clean_previous: bool = True,
) -> Message:
    """
    Deletes the trigger message and previous messages, sends a new photo message,
    and registers it for future auto-cleanup.
    """
    bot = getattr(message, "bot", None)
    chat_id = getattr(getattr(message, "chat", None), "id", 0)

    if delete_trigger:
        await delete_user_message(message)

    if clean_previous and bot and chat_id:
        await cleanup_previous_bot_messages(bot, chat_id)

    sent = await message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )

    if sent and hasattr(sent, "message_id") and chat_id:
        try:
            mid = int(sent.message_id)
            track_message(chat_id, mid)
        except (ValueError, TypeError):
            pass

    return sent
