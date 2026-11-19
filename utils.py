"""Utility functions and helpers.

Provides safe Telegram API wrappers, HTML escaping against injection/parsing errors,
callback parsing, and project calculation formulas.
"""

from __future__ import annotations

import html
import logging
from typing import Any
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

import config

logger = logging.getLogger(__name__)


def safe_html(text: Any) -> str:
    """Escape text for safe usage in HTML formatted Telegram messages.

    Prevents raw HTML tags (like '<script>' or unclosed '<foo') from breaking
    Telegram's HTML entity parser.

    Args:
        text: Input string or object.

    Returns:
        HTML escaped string.
    """
    if text is None:
        return ""
    return html.escape(str(text))


def safe_send_message(
    bot: telebot.TeleBot,
    chat_id: int | str,
    text: str,
    reply_markup: types.InlineKeyboardMarkup | types.ReplyKeyboardMarkup | None = None,
    parse_mode: str = "HTML"
) -> tuple[bool, str | None]:
    """Safely send a message, catching blocked bot errors and chat unavailability.

    Args:
        bot: TeleBot instance.
        chat_id: Target chat ID.
        text: Message text.
        reply_markup: Optional keyboard markup.
        parse_mode: Formatting mode ('HTML').

    Returns:
        tuple[bool, str | None]: (Success flag, error message if any).
    """
    try:
        bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
        return True, None
    except ApiTelegramException as e:
        err_msg = str(e).lower()
        if "bot was blocked by the user" in err_msg:
            logger.warning(f"Failed to send message: Bot was blocked by user {chat_id}.")
            return False, "Пользователь заблокировал бота."
        if "chat not found" in err_msg or "user not found" in err_msg:
            logger.warning(f"Chat {chat_id} not found.")
            return False, "Чат или пользователь не найден."
        logger.error(f"Telegram API exception sending to {chat_id}: {e}")
        return False, str(e)
    except Exception as e:
        logger.error(f"Unexpected error sending message to {chat_id}: {e}", exc_info=True)
        return False, str(e)


def safe_edit_message_text(
    bot: telebot.TeleBot,
    text: str,
    chat_id: int | str,
    message_id: int,
    reply_markup: types.InlineKeyboardMarkup | None = None,
    parse_mode: str = "HTML"
) -> bool:
    """Safely edit message text handling 'message is not modified' gracefully.

    Args:
        bot: TeleBot instance.
        text: New message text.
        chat_id: Target chat ID.
        message_id: Message ID to edit.
        reply_markup: Optional new inline keyboard.
        parse_mode: Formatting mode.

    Returns:
        bool: True if message was edited, False if unmodified or harmlessly skipped.
    """
    try:
        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        return True
    except ApiTelegramException as e:
        err_msg = str(e).lower()
        if "message is not modified" in err_msg:
            return False
        if "message to edit not found" in err_msg:
            logger.warning(f"Message {message_id} in {chat_id} not found for edit.")
            return False
        logger.error(f"Telegram API exception editing message {message_id} in {chat_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error editing message {message_id} in {chat_id}: {e}", exc_info=True)
        return False


def safe_edit_message_reply_markup(
    bot: telebot.TeleBot,
    chat_id: int | str,
    message_id: int,
    reply_markup: types.InlineKeyboardMarkup | None = None
) -> bool:
    """Safely edit message inline keyboard handling 'message is not modified'."""
    try:
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup
        )
        return True
    except ApiTelegramException as e:
        if "message is not modified" in str(e).lower():
            return False
        logger.error(f"Telegram API exception editing markup {message_id} in {chat_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error editing markup {message_id} in {chat_id}: {e}", exc_info=True)
        return False


def safe_answer_callback(
    bot: telebot.TeleBot,
    callback_query_id: str,
    text: str | None = None,
    show_alert: bool = False
) -> bool:
    """Acknowledge callback query safely, suppressing expired query exceptions."""
    try:
        bot.answer_callback_query(callback_query_id, text=text, show_alert=show_alert)
        return True
    except ApiTelegramException as e:
        logger.debug(f"Harmless callback answer error: {e}")
        return False
    except Exception as e:
        logger.debug(f"Unexpected error answering callback: {e}")
        return False


def parse_callback(call_data: str, delimiter: str = ":") -> list[str]:
    """Safely split callback data tokens using delimiter without corrupting strings with underscores."""
    if not call_data:
        return []
    return call_data.split(delimiter)


def calculate_project_estimate(
    service_key: str,
    selected_options: list[str] | set[str]
) -> tuple[float, int, int]:
    """Calculate total estimated price and delivery timeline."""
    service = config.SERVICES.get(service_key)
    base_price = service.price if service else 50.0
    days_min = service.days_min if service else 3
    days_max = service.days_max if service else 7

    options_price = 0.0
    additional_days = 0
    is_urgent = False

    for opt_key in selected_options:
        opt = config.OPTIONS.get(opt_key)
        if not opt:
            continue
        options_price += opt.price
        if opt_key == "urgent":
            is_urgent = True
        else:
            additional_days += max(0, opt.days)

    total_price = base_price + options_price
    days_min += additional_days
    days_max += additional_days

    # Urgent option shortens timeline
    if is_urgent:
        days_min = max(2, int(days_min * 0.6))
        days_max = max(3, int(days_max * 0.6))

    return total_price, days_min, days_max


def format_user_mention(
    user_id: int,
    username: str | None = None,
    full_name: str | None = None
) -> str:
    """Format user mention into clean, valid HTML link."""
    display_name = safe_html(full_name or "Пользователь")
    if username:
        clean_user = safe_html(username)
        return f'<a href="https://t.me/{clean_user}">{display_name} (@{clean_user})</a>'
    return f'<a href="tg://user?id={user_id}">{display_name}</a>'
