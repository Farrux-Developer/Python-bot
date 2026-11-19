"""User navigation and informational handlers.

Handles /start, /help, language switcher, price list, interactive portfolio showcase,
FAQ/workflow milestones, and direct developer contact channels.
"""

from __future__ import annotations

import logging
import telebot
from telebot import types

import config
import database
import keyboards
from texts import t
from utils import parse_callback, safe_answer_callback, safe_edit_message_text, safe_html

logger = logging.getLogger(__name__)


def register_user_handlers(bot: telebot.TeleBot) -> None:
    """Register all general user and navigation handlers.

    Args:
        bot: TeleBot instance.
    """

    @bot.message_handler(commands=["start"])
    def cmd_start(message: types.Message) -> None:
        """Handle /start command: register user and display main menu."""
        user = message.from_user
        database.get_or_create_user(
            user_id=user.id,
            username=user.username,
            full_name=f"{user.first_name or ''} {user.last_name or ''}".strip()
        )
        lang = database.get_user_language(user.id)
        is_admin_user = config.is_admin(user.id)
        logger.info(f"User {user.id} (@{user.username}) started bot. Lang: {lang}")

        # Reset any active FSM state
        bot.delete_state(user.id, message.chat.id)

        welcome_text = t("welcome", lang)
        bot.send_message(
            chat_id=message.chat.id,
            text=welcome_text,
            parse_mode="HTML",
            reply_markup=keyboards.get_main_menu(lang, is_admin_user=is_admin_user)
        )

    @bot.message_handler(commands=["help"])
    def cmd_help(message: types.Message) -> None:
        """Handle /help command: display bot instructions."""
        lang = database.get_user_language(message.from_user.id)
        is_admin_user = config.is_admin(message.from_user.id)
        help_text = t("help_text", lang)
        bot.send_message(
            chat_id=message.chat.id,
            text=help_text,
            parse_mode="HTML",
            reply_markup=keyboards.get_main_menu(lang, is_admin_user=is_admin_user)
        )

    @bot.message_handler(commands=["lang"])
    def cmd_lang(message: types.Message) -> None:
        """Handle /lang command: show language switcher."""
        lang = database.get_user_language(message.from_user.id)
        bot.send_message(
            chat_id=message.chat.id,
            text=t("lang_select_title", lang),
            parse_mode="HTML",
            reply_markup=keyboards.get_language_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: call.data == "menu:main")
    def on_menu_main(call: types.CallbackQuery) -> None:
        """Return to main menu screen."""
        safe_answer_callback(bot, call.id)
        user_id = call.from_user.id
        lang = database.get_user_language(user_id)
        is_admin_user = config.is_admin(user_id)

        bot.delete_state(user_id, call.message.chat.id)

        text = t("choose_section", lang)
        safe_edit_message_text(
            bot=bot,
            text=text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_main_menu(lang, is_admin_user=is_admin_user)
        )

    @bot.callback_query_handler(func=lambda call: call.data == "menu:pricing")
    def on_menu_pricing(call: types.CallbackQuery) -> None:
        """Show dynamic price list generated from catalog."""
        safe_answer_callback(bot, call.id)
        lang = database.get_user_language(call.from_user.id)

        text_parts = [t("pricing_title", lang)]
        for _, s in config.SERVICES.items():
            text_parts.append(
                f"🔹 <b>{s.get_name(lang)}</b> — от ${int(s.price)}\n"
                f"   <i>{s.get_desc(lang)}</i>\n"
            )
        text_parts.append(t("pricing_footer", lang))

        safe_edit_message_text(
            bot=bot,
            text="".join(text_parts),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_pricing_keyboard(lang)
        )

    @bot.callback_query_handler(func=lambda call: call.data == "menu:faq")
    def on_menu_faq(call: types.CallbackQuery) -> None:
        """Display FAQ, milestones, and development guarantees."""
        safe_answer_callback(bot, call.id)
        lang = database.get_user_language(call.from_user.id)
        safe_edit_message_text(
            bot=bot,
            text=t("faq_title", lang),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_faq_keyboard(lang)
        )

    # --- INTERACTIVE PORTFOLIO & CASE STUDIES ---

    @bot.callback_query_handler(func=lambda call: call.data == "menu:portfolio")
    def on_menu_portfolio(call: types.CallbackQuery) -> None:
        """Show portfolio categories."""
        safe_answer_callback(bot, call.id)
        lang = database.get_user_language(call.from_user.id)
        safe_edit_message_text(
            bot=bot,
            text=t("portfolio_menu_title", lang),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_portfolio_categories_keyboard(lang)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("portfolio:cat:"))
    def on_portfolio_category(call: types.CallbackQuery) -> None:
        """Show case studies for selected category."""
        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        if len(tokens) < 3:
            return

        cat_key = tokens[2]
        lang = database.get_user_language(call.from_user.id)
        cat_name = config.PORTFOLIO_CATEGORIES.get(cat_key, {}).get(lang, cat_key)

        text = f"📁 <b>Категория: {cat_name}</b>\n\nВыберите проект для изучения стека и результатов:"
        safe_edit_message_text(
            bot=bot,
            text=text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_portfolio_cases_keyboard(cat_key, lang)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("portfolio:case:"))
    def on_portfolio_case_detail(call: types.CallbackQuery) -> None:
        """Display single case study card."""
        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        if len(tokens) < 3:
            return

        case_id = tokens[2]
        case = next((c for c in config.PORTFOLIO_CASES if c.id == case_id), None)
        if not case:
            return

        lang = database.get_user_language(call.from_user.id)
        card_text = (
            f"📌 <b>Кейс: {safe_html(case.get_title(lang))}</b>\n\n"
            f"🛠 <b>Стек технологий:</b>\n<code>{safe_html(case.stack)}</code>\n\n"
            f"📝 <b>Задача:</b>\n{safe_html(case.get_desc(lang))}\n\n"
            f"📊 <b>Результаты и метрики:</b>\n{safe_html(case.get_metrics(lang))}"
        )
        safe_edit_message_text(
            bot=bot,
            text=card_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_case_detail_keyboard(case, lang)
        )

    # --- CONTACT & LANGUAGE ---

    @bot.callback_query_handler(func=lambda call: call.data == "menu:contact")
    def on_menu_contact(call: types.CallbackQuery) -> None:
        """Show developer contact info."""
        safe_answer_callback(bot, call.id)
        lang = database.get_user_language(call.from_user.id)
        safe_edit_message_text(
            bot=bot,
            text=t("contact_title", lang),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_contact_keyboard(lang)
        )

    @bot.callback_query_handler(func=lambda call: call.data == "menu:lang")
    def on_menu_lang(call: types.CallbackQuery) -> None:
        """Show language selection inline menu."""
        safe_answer_callback(bot, call.id)
        lang = database.get_user_language(call.from_user.id)
        safe_edit_message_text(
            bot=bot,
            text=t("lang_select_title", lang),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_language_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("lang:set:"))
    def on_set_language(call: types.CallbackQuery) -> None:
        """Process language change selection."""
        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        if len(tokens) >= 3:
            new_lang = tokens[2]
            if new_lang in config.SUPPORTED_LANGUAGES:
                database.set_user_language(call.from_user.id, new_lang)
                is_admin_user = config.is_admin(call.from_user.id)
                logger.info(f"User {call.from_user.id} switched language to {new_lang}")
                safe_edit_message_text(
                    bot=bot,
                    text=f"{t('lang_changed', new_lang)}\n\n{t('choose_section', new_lang)}",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=keyboards.get_main_menu(new_lang, is_admin_user=is_admin_user)
                )
