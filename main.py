"""Main entry point for WebOrder Telegram Bot.

Initializes logging, database, FSM storage, custom filters, registers handlers,
sets Telegram commands menu, and runs resilient polling with exponential backoff.
"""

from __future__ import annotations

import logging
import sys
import time
from logging.handlers import RotatingFileHandler

import requests
import telebot
from telebot import custom_filters, types
from telebot.apihelper import ApiTelegramException
from telebot.storage import StateMemoryStorage

import config
import database
from handlers.admin import register_admin_handlers
from handlers.payment import register_payment_handlers
from handlers.quiz import register_quiz_handlers
from handlers.user import register_user_handlers

# --- LOGGING SETUP ---
logger = logging.getLogger("weborder_bot")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# File handler with rotation (max 5 MB, 3 backups)
file_handler = RotatingFileHandler("bot.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Console stream handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def setup_bot_commands(bot: telebot.TeleBot) -> None:
    """Register default slash commands menu in Telegram UI.

    Args:
        bot: TeleBot instance.
    """
    commands = [
        types.BotCommand("start", "🚀 Запустить бота / Start"),
        types.BotCommand("order", "🛒 Заказать сайт / Order website"),
        types.BotCommand("help", "ℹ️ Инструкция / Help"),
        types.BotCommand("lang", "🌐 Выбрать язык / Language"),
    ]
    try:
        bot.set_my_commands(commands)
        logger.info("Bot commands menu registered successfully.")
    except Exception as e:
        logger.warning(f"Could not register bot commands menu: {e}")


def create_bot() -> telebot.TeleBot:
    """Create and configure TeleBot instance with FSM and all handlers.

    Returns:
        telebot.TeleBot: Configured bot instance.
    """
    if not config.BOT_TOKEN or config.BOT_TOKEN.startswith("ТВОЙ_") or "PASTE" in config.BOT_TOKEN:
        logger.critical("BOT_TOKEN is missing or not set in .env! Please check your .env configuration.")

    # Initialize FSM in-memory storage
    storage = StateMemoryStorage()
    bot = telebot.TeleBot(token=config.BOT_TOKEN, state_storage=storage, parse_mode="HTML")

    # Add StateFilter for FSM support in handlers
    bot.add_custom_filter(custom_filters.StateFilter(bot))

    # Register modular handlers
    register_user_handlers(bot)
    register_quiz_handlers(bot)
    register_payment_handlers(bot)
    register_admin_handlers(bot)

    return bot


def run_bot() -> None:
    """Run bot polling loop with graceful exponential backoff and error recovery."""
    # 1. Initialize SQLite database
    try:
        database.init_db()
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}", exc_info=True)
        sys.exit(1)

    # 2. Check token
    if not config.BOT_TOKEN:
        logger.critical("BOT_TOKEN is empty! Aborting bot launch.")
        sys.exit(1)

    # 3. Instantiate bot
    bot = create_bot()
    setup_bot_commands(bot)

    logger.info("==========================================")
    logger.info("🚀 WebOrder Bot успешно сконфигурирован!")
    logger.info(f"🔑 Admin ID: {config.ADMIN_ID or 'Не задан'}")
    logger.info(f"💳 Payment provider: {'Включен' if config.PROVIDER_TOKEN else 'Выключен'}")
    logger.info("==========================================")

    retry_delay = 3
    max_delay = 60

    while True:
        try:
            logger.info("Подключение к Telegram API (polling)...")
            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=30,
                skip_pending=False
            )
            # Normal completion
            break

        except ApiTelegramException as e:
            if e.error_code in (401, 404):
                logger.critical(
                    f"Критическая ошибка Telegram API ({e.error_code}): {e.description}. "
                    "Проверьте корректность BOT_TOKEN в .env. Работа остановлена."
                )
                break
            logger.error(f"Ошибка Telegram API ({e.error_code}): {e.description}. Перезапуск через {retry_delay} сек...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning(f"Сетевая ошибка соединения: {e}. Переподключение через {retry_delay} сек...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)

        except (KeyboardInterrupt, SystemExit):
            logger.info("Остановка бота по сигналу пользователя (Ctrl+C). До свидания!")
            break

        except Exception as e:
            logger.error(f"Непредвиденное исключение в polling: {e}. Перезапуск через {retry_delay} сек...", exc_info=True)
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)


if __name__ == "__main__":
    run_bot()
