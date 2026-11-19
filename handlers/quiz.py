"""Interactive 5-step website ordering quiz flow (FSM).

Step 1: Website type selection + task description / reference link.
Step 2: Additional options multiselection with real-time toggle (✅ / ⬜).
Step 3: Budget selection and transparent cost & delivery timeline calculation.
Step 4: Contact details (name, phone or @username, notes).
Step 5: Review summary screen & submission with database persistence and admin notification.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
import telebot
from telebot import types

import config
import database
import keyboards
from states import OrderQuiz
from texts import t
from utils import (
    calculate_project_estimate,
    format_user_mention,
    parse_callback,
    safe_answer_callback,
    safe_edit_message_reply_markup,
    safe_edit_message_text,
    safe_html,
)

logger = logging.getLogger(__name__)


def register_quiz_handlers(bot: telebot.TeleBot) -> None:
    """Register all handlers related to the website ordering quiz.

    Args:
        bot: TeleBot instance.
    """

    # --- ENTRY POINT & CANCELLATION ---

    @bot.message_handler(commands=["order"])
    def cmd_order(message: types.Message) -> None:
        """Command /order shortcut to start quiz."""
        start_quiz(user_id=message.from_user.id, chat_id=message.chat.id, message_id=None)

    @bot.callback_query_handler(func=lambda call: call.data == "menu:order")
    def on_menu_order(call: types.CallbackQuery) -> None:
        """Start quiz from main menu button."""
        safe_answer_callback(bot, call.id)
        start_quiz(
            user_id=call.from_user.id,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("quiz:start_with_service:"))
    def on_start_with_service(call: types.CallbackQuery) -> None:
        """Hook from portfolio: 'Хочу похожий сайт' pre-selecting site type."""
        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        service_key = tokens[2] if len(tokens) >= 3 else "landing"

        user_id = call.from_user.id
        chat_id = call.message.chat.id
        database.get_or_create_user(user_id)
        lang = database.get_user_language(user_id)

        bot.set_state(user_id, OrderQuiz.input_description, chat_id)
        with bot.retrieve_data(user_id, chat_id) as data:
            data.clear()
            data["service"] = service_key
            data["options"] = []
            data["lang"] = lang

        service = config.SERVICES.get(service_key, list(config.SERVICES.values())[0])
        text = t("quiz_step1_desc_prompt", lang, service_name=service.get_name(lang))
        safe_edit_message_text(
            bot=bot,
            text=text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_description_step_keyboard(lang)
        )

    def start_quiz(user_id: int, chat_id: int, message_id: int | None = None) -> None:
        """Initialize quiz state and display Step 1."""
        database.get_or_create_user(user_id)
        lang = database.get_user_language(user_id)

        bot.set_state(user_id, OrderQuiz.select_service, chat_id)
        with bot.retrieve_data(user_id, chat_id) as data:
            data.clear()
            data["options"] = []
            data["lang"] = lang

        prompt_text = t("quiz_step1_title", lang)
        markup = keyboards.get_services_keyboard(lang)

        if message_id:
            safe_edit_message_text(bot, prompt_text, chat_id, message_id, reply_markup=markup)
        else:
            bot.send_message(chat_id, prompt_text, parse_mode="HTML", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == "quiz:cancel", state="*")
    def on_quiz_cancel(call: types.CallbackQuery) -> None:
        """Cancel quiz at any stage and return to main menu."""
        safe_answer_callback(bot, call.id)
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)
        is_admin_user = config.is_admin(user_id)

        bot.delete_state(user_id, chat_id)
        cancel_text = f"{t('quiz_cancelled', lang)}\n\n{t('choose_section', lang)}"
        safe_edit_message_text(
            bot=bot,
            text=cancel_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_main_menu(lang, is_admin_user=is_admin_user)
        )

    # --- STEP 1: SERVICE SELECTION & DESCRIPTION ---

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("quiz:service:"),
        state=OrderQuiz.select_service
    )
    def on_service_selected(call: types.CallbackQuery) -> None:
        """Handle site type selection and prompt for description/reference."""
        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        if len(tokens) < 3:
            return

        service_key = tokens[2]
        if service_key not in config.SERVICES:
            return

        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)

        with bot.retrieve_data(user_id, chat_id) as data:
            data["service"] = service_key

        bot.set_state(user_id, OrderQuiz.input_description, chat_id)
        service = config.SERVICES[service_key]

        text = t("quiz_step1_desc_prompt", lang, service_name=service.get_name(lang))
        safe_edit_message_text(
            bot=bot,
            text=text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_description_step_keyboard(lang)
        )

    @bot.callback_query_handler(
        func=lambda call: call.data == "quiz:skip_desc",
        state=OrderQuiz.input_description
    )
    def on_skip_description(call: types.CallbackQuery) -> None:
        """Handle skipping description input."""
        safe_answer_callback(bot, call.id)
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)

        with bot.retrieve_data(user_id, chat_id) as data:
            data["description"] = t("quiz_desc_not_specified", lang)
            selected_options = data.get("options", [])

        # Move to Step 2 (Options)
        bot.set_state(user_id, OrderQuiz.select_options, chat_id)
        text = t("quiz_step2_title", lang)
        safe_edit_message_text(
            bot=bot,
            text=text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_options_keyboard(selected_options, lang)
        )

    @bot.message_handler(state=OrderQuiz.input_description, content_types=["text", "photo", "document"])
    def on_description_text_entered(message: types.Message) -> None:
        """Handle custom description/reference text or captioned files."""
        user_id = message.from_user.id
        chat_id = message.chat.id
        lang = database.get_user_language(user_id)

        text_content = message.text or message.caption
        if not text_content:
            bot.reply_to(message, t("prompt_text_only", lang))
            return

        desc_text = safe_html(text_content.strip())

        with bot.retrieve_data(user_id, chat_id) as data:
            data["description"] = desc_text
            selected_options = data.get("options", [])

        # Move to Step 2 (Options)
        bot.set_state(user_id, OrderQuiz.select_options, chat_id)
        text = t("quiz_step2_title", lang)
        bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            reply_markup=keyboards.get_options_keyboard(selected_options, lang)
        )

    # --- STEP 2: ADDITIONAL OPTIONS (MULTI-TOGGLE) ---

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("quiz:opt:"),
        state=OrderQuiz.select_options
    )
    def on_toggle_option(call: types.CallbackQuery) -> None:
        """Toggle an option on/off with instant checkmark update."""
        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        if len(tokens) < 3:
            return

        opt_key = tokens[2]
        if opt_key not in config.OPTIONS:
            return

        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)

        with bot.retrieve_data(user_id, chat_id) as data:
            options_set = set(data.get("options", []))
            if opt_key in options_set:
                options_set.remove(opt_key)
            else:
                options_set.add(opt_key)
            data["options"] = list(options_set)
            current_options = data["options"]

        # Smoothly update reply markup with modified checkboxes
        safe_edit_message_reply_markup(
            bot=bot,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_options_keyboard(current_options, lang)
        )

    @bot.callback_query_handler(
        func=lambda call: call.data == "quiz:options_done",
        state=OrderQuiz.select_options
    )
    def on_options_done(call: types.CallbackQuery) -> None:
        """Calculate estimates and transition to Step 3 (Budget)."""
        safe_answer_callback(bot, call.id)
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)

        with bot.retrieve_data(user_id, chat_id) as data:
            service_key = data.get("service", "landing")
            selected_options = data.get("options", [])
            total_price, min_days, max_days = calculate_project_estimate(service_key, selected_options)

            data["calc_price"] = total_price
            data["calc_days_min"] = min_days
            data["calc_days_max"] = max_days
            data["calc_terms"] = f"{min_days}–{max_days} дн."

            service = config.SERVICES[service_key]
            if selected_options:
                opt_lines = [
                    f"  • {config.OPTIONS[k].get_name(lang)} (+${int(config.OPTIONS[k].price)})"
                    for k in selected_options if k in config.OPTIONS
                ]
                options_list_str = "\n".join(opt_lines)
            else:
                options_list_str = "  <i>— Без дополнительных опций</i>"

            text = t(
                "quiz_step3_title",
                lang,
                service_name=service.get_name(lang),
                base_price=int(service.price),
                options_list=options_list_str,
                total_price=int(total_price),
                days_min=min_days,
                days_max=max_days
            )

        bot.set_state(user_id, OrderQuiz.select_budget, chat_id)
        safe_edit_message_text(
            bot=bot,
            text=text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_budget_keyboard(total_price, lang)
        )

    # --- STEP 3: BUDGET SELECTION ---

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("quiz:budget:"),
        state=OrderQuiz.select_budget
    )
    def on_budget_selected(call: types.CallbackQuery) -> None:
        """Handle budget tier selection or custom budget request."""
        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        if len(tokens) < 3:
            return

        choice = tokens[2]
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)

        if choice == "custom":
            bot.set_state(user_id, OrderQuiz.input_custom_budget, chat_id)
            prompt_text = t("quiz_prompt_custom_budget", lang)
            markup = types.InlineKeyboardMarkup().row(
                types.InlineKeyboardButton(t("btn_back", lang), callback_data="quiz:back:budget_tiers"),
                types.InlineKeyboardButton(t("btn_cancel", lang), callback_data="quiz:cancel"),
            )
            safe_edit_message_text(bot, prompt_text, chat_id, call.message.message_id, reply_markup=markup)
            return

        with bot.retrieve_data(user_id, chat_id) as data:
            if choice == "calc":
                data["budget"] = f"От ${int(data.get('calc_price', 50))} (расчётный)"
            elif choice == "tier_under_100":
                data["budget"] = "До $100"
            elif choice == "tier_100_300":
                data["budget"] = "$100 – $300"
            elif choice == "tier_300_600":
                data["budget"] = "$300 – $600"
            elif choice == "tier_600_plus":
                data["budget"] = "$600+"
            else:
                data["budget"] = choice

        proceed_to_contacts(user_id, chat_id, call.message.message_id, lang, call.from_user.username)

    @bot.message_handler(state=OrderQuiz.input_custom_budget)
    def on_custom_budget_entered(message: types.Message) -> None:
        """Handle custom budget entered by message."""
        user_id = message.from_user.id
        chat_id = message.chat.id
        lang = database.get_user_language(user_id)

        if not message.text:
            bot.reply_to(message, t("prompt_text_only", lang))
            return

        custom_budget = safe_html(message.text.strip())
        with bot.retrieve_data(user_id, chat_id) as data:
            data["budget"] = custom_budget

        proceed_to_contacts(user_id, chat_id, None, lang, message.from_user.username)

    def proceed_to_contacts(
        user_id: int,
        chat_id: int,
        message_id: int | None,
        lang: str,
        username: str | None
    ) -> None:
        """Display Step 4 (Contact details prompt)."""
        bot.set_state(user_id, OrderQuiz.input_contact, chat_id)
        text = t("quiz_step4_title", lang)
        markup = keyboards.get_contact_step_keyboard(
            has_tg_username=bool(username),
            username=username,
            lang=lang
        )
        if message_id:
            safe_edit_message_text(bot, text, chat_id, message_id, reply_markup=markup)
        else:
            bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

    # --- STEP 4: CONTACT INFORMATION ---

    @bot.callback_query_handler(
        func=lambda call: call.data == "quiz:contact:use_tg",
        state=OrderQuiz.input_contact
    )
    def on_contact_use_tg(call: types.CallbackQuery) -> None:
        """Use Telegram username/link as contact."""
        safe_answer_callback(bot, call.id)
        user = call.from_user
        contact = f"{safe_html(user.first_name or 'Клиент')} (@{user.username})" if user.username else f"ID: {user.id}"
        render_confirmation_screen(
            user_id=user.id,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            contact_info=contact
        )

    @bot.message_handler(state=OrderQuiz.input_contact)
    def on_contact_text_entered(message: types.Message) -> None:
        """Handle manually entered contact details."""
        user_id = message.from_user.id
        chat_id = message.chat.id
        lang = database.get_user_language(user_id)

        if not message.text:
            bot.reply_to(message, t("prompt_text_only", lang))
            return

        contact_info = safe_html(message.text.strip())
        render_confirmation_screen(
            user_id=user_id,
            chat_id=chat_id,
            message_id=None,
            contact_info=contact_info
        )

    def render_confirmation_screen(
        user_id: int,
        chat_id: int,
        message_id: int | None,
        contact_info: str
    ) -> None:
        """Display Step 5 (Order review and confirmation card)."""
        bot.set_state(user_id, OrderQuiz.confirm_order, chat_id)
        lang = database.get_user_language(user_id)

        with bot.retrieve_data(user_id, chat_id) as data:
            data["contact_info"] = contact_info
            service_key = data.get("service", "landing")
            service = config.SERVICES.get(service_key, list(config.SERVICES.values())[0])
            options_keys = data.get("options", [])
            options_str = ", ".join(
                config.OPTIONS[k].get_name(lang) for k in options_keys if k in config.OPTIONS
            ) or "—"
            budget = data.get("budget", "По согласованию")
            terms = data.get("calc_terms", "3–7 дней")
            desc = data.get("description", "Не указано")

            summary_text = t(
                "quiz_confirm_screen",
                lang,
                service_name=service.get_name(lang),
                description=desc,
                options=options_str,
                budget=budget,
                terms=terms,
                contacts=contact_info
            )

            markup = keyboards.get_confirmation_keyboard(
                can_pay_deposit=bool(config.PROVIDER_TOKEN),
                lang=lang
            )

        if message_id:
            safe_edit_message_text(bot, summary_text, chat_id, message_id, reply_markup=markup)
        else:
            bot.send_message(chat_id, summary_text, parse_mode="HTML", reply_markup=markup)

    # --- STEP 5: DEPOSIT TIERS & CONFIRMATION ---

    @bot.callback_query_handler(
        func=lambda call: call.data == "quiz:deposit_tiers",
        state=OrderQuiz.confirm_order
    )
    def on_quiz_deposit_tiers(call: types.CallbackQuery) -> None:
        """Show deposit options (30%, 50%, 100%)."""
        safe_answer_callback(bot, call.id)
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)

        with bot.retrieve_data(user_id, chat_id) as data:
            base_price = data.get("calc_price", 100.0)

        prompt = "💳 <b>Выберите размер предоплаты для бронирования очереди:</b>"
        safe_edit_message_text(
            bot=bot,
            text=prompt,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_deposit_tiers_keyboard(base_price, lang)
        )

    @bot.callback_query_handler(
        func=lambda call: call.data == "quiz:back:confirm",
        state=OrderQuiz.confirm_order
    )
    def on_quiz_back_to_confirm(call: types.CallbackQuery) -> None:
        """Return from deposit tiers back to confirmation screen."""
        safe_answer_callback(bot, call.id)
        user_id = call.from_user.id
        with bot.retrieve_data(user_id, call.message.chat.id) as data:
            contact = data.get("contact_info", f"ID: {user_id}")
        render_confirmation_screen(user_id, call.message.chat.id, call.message.message_id, contact)

    @bot.callback_query_handler(
        func=lambda call: call.data == "quiz:confirm",
        state=OrderQuiz.confirm_order
    )
    def on_quiz_confirm_order(call: types.CallbackQuery) -> None:
        """Persist order in DB and notify admin and user."""
        safe_answer_callback(bot, call.id)
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)
        is_admin_user = config.is_admin(user_id)

        with bot.retrieve_data(user_id, chat_id) as data:
            service_key = data.get("service", "landing")
            service = config.SERVICES.get(service_key, list(config.SERVICES.values())[0])
            desc = data.get("description", "Не указано")
            options_keys = data.get("options", [])
            budget = data.get("budget", "По согласованию")
            calc_price = data.get("calc_price", service.price)
            calc_terms = data.get("calc_terms", "3-7 дней")
            contact_info = data.get("contact_info", f"ID: {user_id}")

        # Save order into SQLite database
        order_id = database.create_order(
            user_id=user_id,
            service_type=service_key,
            details=desc,
            options=options_keys,
            budget=budget,
            estimated_price=calc_price,
            estimated_days=calc_terms,
            contact_info=contact_info
        )
        logger.info(f"Order #{order_id} created by user {user_id}")

        # Clear FSM state
        bot.delete_state(user_id, chat_id)

        # Notify user of successful submission
        success_text = t("quiz_success", lang, order_id=order_id)
        safe_edit_message_text(
            bot=bot,
            text=success_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_main_menu(lang, is_admin_user=is_admin_user)
        )

        # Send detailed notification card to admin
        if config.ADMIN_ID:
            options_formatted = "\n".join(
                f"  • {config.OPTIONS[k].get_name('ru')}" for k in options_keys if k in config.OPTIONS
            ) or "  <i>Без доп. опций</i>"

            user_mention = format_user_mention(
                user_id=user_id,
                username=call.from_user.username,
                full_name=f"{call.from_user.first_name or ''} {call.from_user.last_name or ''}".strip()
            )

            admin_text = t(
                "admin_new_order_card",
                "ru",
                order_id=order_id,
                user_link=user_mention,
                user_id=user_id,
                service_name=service.get_name("ru"),
                description=desc,
                options=options_formatted,
                budget=budget,
                terms=calc_terms,
                contacts=contact_info,
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            try:
                bot.send_message(
                    chat_id=config.ADMIN_ID,
                    text=admin_text,
                    parse_mode="HTML",
                    reply_markup=keyboards.get_admin_order_card_keyboard(
                        order_id=order_id,
                        user_id=user_id,
                        username=call.from_user.username
                    )
                )
                logger.info(f"Admin {config.ADMIN_ID} notified of order #{order_id}")
            except Exception as e:
                logger.error(f"Failed to send admin notification for order #{order_id}: {e}", exc_info=True)

    # --- STEP-BY-STEP BACK NAVIGATION ---

    @bot.callback_query_handler(func=lambda call: call.data.startswith("quiz:back:"), state="*")
    def on_quiz_back(call: types.CallbackQuery) -> None:
        """Handle step-by-step backward navigation."""
        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        if len(tokens) < 3:
            return

        target = tokens[2]
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)

        if target == "service":
            bot.set_state(user_id, OrderQuiz.select_service, chat_id)
            safe_edit_message_text(
                bot=bot,
                text=t("quiz_step1_title", lang),
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=keyboards.get_services_keyboard(lang)
            )

        elif target == "desc":
            with bot.retrieve_data(user_id, chat_id) as data:
                service_key = data.get("service", "landing")
            bot.set_state(user_id, OrderQuiz.input_description, chat_id)
            service = config.SERVICES.get(service_key, list(config.SERVICES.values())[0])
            safe_edit_message_text(
                bot=bot,
                text=t("quiz_step1_desc_prompt", lang, service_name=service.get_name(lang)),
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=keyboards.get_description_step_keyboard(lang)
            )

        elif target == "options":
            with bot.retrieve_data(user_id, chat_id) as data:
                current_opts = data.get("options", [])
            bot.set_state(user_id, OrderQuiz.select_options, chat_id)
            safe_edit_message_text(
                bot=bot,
                text=t("quiz_step2_title", lang),
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=keyboards.get_options_keyboard(current_opts, lang)
            )

        elif target in ("budget", "budget_tiers"):
            with bot.retrieve_data(user_id, chat_id) as data:
                service_key = data.get("service", "landing")
                selected_options = data.get("options", [])
                calc_price = data.get("calc_price", 50.0)
                service = config.SERVICES[service_key]

                if selected_options:
                    opt_lines = [
                        f"  • {config.OPTIONS[k].get_name(lang)} (+${int(config.OPTIONS[k].price)})"
                        for k in selected_options if k in config.OPTIONS
                    ]
                    options_list_str = "\n".join(opt_lines)
                else:
                    options_list_str = "  <i>— Без дополнительных опций</i>"

                text = t(
                    "quiz_step3_title",
                    lang,
                    service_name=service.get_name(lang),
                    base_price=int(service.price),
                    options_list=options_list_str,
                    total_price=int(calc_price),
                    days_min=data.get("calc_days_min", 3),
                    days_max=data.get("calc_days_max", 7)
                )

            bot.set_state(user_id, OrderQuiz.select_budget, chat_id)
            safe_edit_message_text(
                bot=bot,
                text=text,
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=keyboards.get_budget_keyboard(calc_price, lang)
            )

        elif target == "contact":
            proceed_to_contacts(
                user_id=user_id,
                chat_id=chat_id,
                message_id=call.message.message_id,
                lang=lang,
                username=call.from_user.username
            )
