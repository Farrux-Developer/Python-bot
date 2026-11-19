"""Administrator dashboard, order moderation, and direct client messaging.

Features:
- Access restricted exclusively to ADMIN_ID with strict verification.
- Comprehensive statistics dashboard (users, orders, conversion, volume).
- Paginated order catalog with real-time status filtering (All, New, In Progress, Review, etc.).
- Detailed order inspector with inline status toggling and client notifications.
- Direct messaging relay: admin can write a message that the bot sends directly to the client.
"""

from __future__ import annotations

import logging
import telebot
from telebot import types

import config
import database
import keyboards
from states import AdminState
from texts import t
from utils import (
    format_user_mention,
    parse_callback,
    safe_answer_callback,
    safe_edit_message_reply_markup,
    safe_edit_message_text,
    safe_html,
    safe_send_message,
)

logger = logging.getLogger(__name__)


def register_admin_handlers(bot: telebot.TeleBot) -> None:
    """Register all administrator commands and callback actions.

    Args:
        bot: TeleBot instance.
    """

    # --- ADMIN ROOT MENU & STATS ---

    @bot.message_handler(commands=["admin"])
    def cmd_admin_menu(message: types.Message) -> None:
        """Open administrator root menu."""
        if not config.is_admin(message.from_user.id):
            return

        bot.send_message(
            chat_id=message.chat.id,
            text="👑 <b>Панель управления администратора</b>\n\nВыберите действие:",
            parse_mode="HTML",
            reply_markup=keyboards.get_admin_dashboard_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: call.data == "admin:menu")
    def on_admin_menu(call: types.CallbackQuery) -> None:
        """Navigate to admin root menu."""
        if not config.is_admin(call.from_user.id):
            safe_answer_callback(bot, call.id, "Доступ запрещен.", show_alert=True)
            return

        safe_answer_callback(bot, call.id)
        safe_edit_message_text(
            bot=bot,
            text="👑 <b>Панель управления администратора</b>\n\nВыберите действие:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_admin_dashboard_keyboard()
        )

    @bot.message_handler(commands=["stats"])
    @bot.callback_query_handler(func=lambda call: call.data == "admin:stats")
    def on_admin_stats(event: types.Message | types.CallbackQuery) -> None:
        """Display admin dashboard statistics."""
        user_id = event.from_user.id
        if not config.is_admin(user_id):
            return

        stats = database.get_admin_stats()
        text = (
            "📊 <b>Статистика WebOrder Bot</b>\n\n"
            f"👥 <b>Всего пользователей в базе:</b> {stats['total_users']}\n"
            f"📋 <b>Всего заявок:</b> {stats['total_orders']}\n"
            f"🆕 <b>Новых заявок:</b> {stats['new_orders']}\n"
            f"⚙️ <b>В работе:</b> {stats['in_progress_orders']}\n"
            f"✅ <b>Завершенных:</b> {stats['completed_orders']}\n\n"
            f"💵 <b>Сумма полученных оплат:</b> ${stats['total_revenue']:.2f}\n"
            f"📈 <b>Общий объём оценочных заявок:</b> ${stats['total_order_volume']:.2f}\n"
        )
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("◀️ В меню администратора", callback_data="admin:menu")
        )

        if isinstance(event, types.CallbackQuery):
            safe_answer_callback(bot, event.id)
            safe_edit_message_text(
                bot=bot,
                text=text,
                chat_id=event.message.chat.id,
                message_id=event.message.message_id,
                reply_markup=markup
            )
        else:
            bot.send_message(event.chat.id, text, parse_mode="HTML", reply_markup=markup)

    # --- ORDERS LISTING & FILTERING ---

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin:orders:"))
    def on_admin_orders_list(call: types.CallbackQuery) -> None:
        """Display paginated list of orders filtered by status."""
        if not config.is_admin(call.from_user.id):
            return

        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        status_filter = tokens[2] if len(tokens) >= 3 else "all"
        offset = int(tokens[3]) if len(tokens) >= 4 and tokens[3].isdigit() else 0
        limit = 5

        orders = database.get_orders(status_filter=status_filter, limit=limit, offset=offset)
        total_count = database.count_orders(status_filter=status_filter)

        filter_name = database.ORDER_STATUSES.get(status_filter, "Все") if status_filter != "all" else "Все"
        text = (
            f"📋 <b>Список заявок ({filter_name})</b>\n"
            f"Показано: {len(orders)} из {total_count} (Стр. {offset // limit + 1})\n\n"
            "<i>Нажмите на заявку для просмотра и управления:</i>"
        )

        safe_edit_message_text(
            bot=bot,
            text=text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_admin_orders_list_keyboard(
                orders=orders,
                status_filter=status_filter,
                offset=offset,
                total_count=total_count,
                limit=limit
            )
        )

    # --- ORDER DETAIL VIEW ---

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin:view_order:"))
    def on_admin_view_order(call: types.CallbackQuery) -> None:
        """Display detailed single order card."""
        if not config.is_admin(call.from_user.id):
            return

        tokens = parse_callback(call.data)
        if len(tokens) < 3 or not tokens[2].isdigit():
            return

        order_id = int(tokens[2])
        order = database.get_order(order_id)
        if not order:
            safe_answer_callback(bot, call.id, "Заказ не найден.", show_alert=True)
            return

        safe_answer_callback(bot, call.id)
        render_order_card(call.message.chat.id, call.message.message_id, order)

    def render_order_card(chat_id: int, message_id: int, order: dict) -> None:
        """Format and display order card."""
        service = config.SERVICES.get(order["service_type"])
        service_name = service.get_name("ru") if service else order["service_type"]
        status_name = database.ORDER_STATUSES.get(order["status"], order["status"])
        payment_name = database.PAYMENT_STATUSES.get(order.get("payment_status", "unpaid"), "Не оплачено")

        options = order.get("options", [])
        if options:
            opts_formatted = "\n".join(
                f"  • {config.OPTIONS[k].get_name('ru')}" for k in options if k in config.OPTIONS
            )
        else:
            opts_formatted = "  <i>Без доп. опций</i>"

        client_mention = format_user_mention(
            user_id=order["user_id"],
            username=order.get("username"),
            full_name=order.get("full_name")
        )

        card_text = (
            f"📋 <b>КАРТОЧКА ЗАЯВКИ #{order['id']}</b>\n\n"
            f"👤 <b>Клиент:</b> {client_mention}\n"
            f"🆔 <b>ID пользователя:</b> <code>{order['user_id']}</code>\n"
            f"🌐 <b>Тип сайта:</b> {safe_html(service_name)}\n"
            f"📝 <b>ТЗ / Референс:</b>\n{safe_html(order.get('details', 'Не указано'))}\n\n"
            f"🛠 <b>Доп. опции:</b>\n{opts_formatted}\n\n"
            f"💰 <b>Бюджет:</b> {safe_html(order.get('budget', 'По согласованию'))}\n"
            f"💵 <b>Расчётная цена:</b> ${order.get('estimated_price', 0):.2f}\n"
            f"⏱ <b>Расчётный срок:</b> {safe_html(order.get('estimated_days', '3-7 дней'))}\n"
            f"📞 <b>Контакты:</b> {safe_html(order.get('contact_info', 'Не указано'))}\n\n"
            f"📊 <b>Статус заказа:</b> <b>{status_name}</b>\n"
            f"💳 <b>Статус оплаты:</b> <b>{payment_name}</b>\n"
            f"📅 <b>Создана:</b> {order['created_at']}"
        )

        safe_edit_message_text(
            bot=bot,
            text=card_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=keyboards.get_admin_order_card_keyboard(
                order_id=order["id"],
                user_id=order["user_id"],
                username=order.get("username")
            )
        )

    # --- STATUS MANAGEMENT ---

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin:status_menu:"))
    def on_admin_status_menu(call: types.CallbackQuery) -> None:
        """Show status switcher options."""
        if not config.is_admin(call.from_user.id):
            return

        tokens = parse_callback(call.data)
        order_id = int(tokens[2])
        safe_answer_callback(bot, call.id)
        safe_edit_message_reply_markup(
            bot=bot,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_admin_status_choice_keyboard(order_id)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin:set_status:"))
    def on_admin_set_status(call: types.CallbackQuery) -> None:
        """Update order status and notify user."""
        if not config.is_admin(call.from_user.id):
            return

        tokens = parse_callback(call.data)
        if len(tokens) < 4:
            return

        order_id = int(tokens[2])
        new_status = tokens[3]
        order = database.get_order(order_id)
        if not order:
            return

        database.update_order_status(order_id, new_status)
        status_label = database.ORDER_STATUSES.get(new_status, new_status)
        safe_answer_callback(bot, call.id, f"Статус обновлен: {status_label}")

        # Notify user with safe message sending
        client_lang = database.get_user_language(order["user_id"])
        notify_text = t("user_status_changed_notify", client_lang, order_id=order_id, status_label=status_label)
        success, err = safe_send_message(bot, order["user_id"], notify_text)
        if not success:
            logger.warning(f"Could not notify user {order['user_id']} of status change: {err}")

        # Re-render card with updated status
        updated_order = database.get_order(order_id)
        if updated_order:
            render_order_card(call.message.chat.id, call.message.message_id, updated_order)

    # --- PAYMENT STATUS MANAGEMENT ---

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin:pay_menu:"))
    def on_admin_pay_menu(call: types.CallbackQuery) -> None:
        """Show payment status switcher options."""
        if not config.is_admin(call.from_user.id):
            return

        tokens = parse_callback(call.data)
        order_id = int(tokens[2])
        safe_answer_callback(bot, call.id)
        safe_edit_message_reply_markup(
            bot=bot,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboards.get_admin_payment_status_keyboard(order_id)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin:set_pay_status:"))
    def on_admin_set_pay_status(call: types.CallbackQuery) -> None:
        """Update payment status."""
        if not config.is_admin(call.from_user.id):
            return

        tokens = parse_callback(call.data)
        order_id = int(tokens[2])
        new_pay_status = tokens[3]

        database.update_order_payment_status(order_id, new_pay_status)
        pay_label = database.PAYMENT_STATUSES.get(new_pay_status, new_pay_status)
        safe_answer_callback(bot, call.id, f"Статус оплаты: {pay_label}")

        updated_order = database.get_order(order_id)
        if updated_order:
            render_order_card(call.message.chat.id, call.message.message_id, updated_order)

    # --- DIRECT MESSAGE TO CLIENT (RELAY) ---

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin:reply:"))
    def on_admin_reply_requested(call: types.CallbackQuery) -> None:
        """Prompt admin to write a direct message to customer."""
        if not config.is_admin(call.from_user.id):
            return

        tokens = parse_callback(call.data)
        if len(tokens) < 3 or not tokens[2].isdigit():
            return

        order_id = int(tokens[2])
        order = database.get_order(order_id)
        if not order:
            return

        safe_answer_callback(bot, call.id)
        bot.set_state(call.from_user.id, AdminState.reply_message, call.message.chat.id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data["reply_order_id"] = order_id
            data["reply_user_id"] = order["user_id"]

        text = (
            f"✍️ <b>Ответ клиенту по заявке #{order_id}</b>\n\n"
            "Напишите сообщение, которое хотите отправить клиенту. "
            "Бот перешлёт его с официальным заголовком разработчика."
        )
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("◀️ Отмена", callback_data=f"admin:cancel_reply:{order_id}")
        )
        safe_edit_message_text(bot, text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin:cancel_reply:"))
    def on_admin_cancel_reply(call: types.CallbackQuery) -> None:
        """Cancel direct messaging to client."""
        tokens = parse_callback(call.data)
        order_id = int(tokens[2])
        bot.delete_state(call.from_user.id, call.message.chat.id)
        safe_answer_callback(bot, call.id, "Ответ отменен.")

        order = database.get_order(order_id)
        if order:
            render_order_card(call.message.chat.id, call.message.message_id, order)

    @bot.message_handler(state=AdminState.reply_message)
    def on_admin_message_composed(message: types.Message) -> None:
        """Deliver admin's message to client and notify admin of status."""
        if not config.is_admin(message.from_user.id):
            return

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            order_id = data.get("reply_order_id")
            client_user_id = data.get("reply_user_id")

        bot.delete_state(message.from_user.id, message.chat.id)

        if not message.text:
            bot.reply_to(message, "⚠️ Сообщение должно быть текстом. Отправка отменена.")
            return

        reply_content = safe_html(message.text.strip())
        client_lang = database.get_user_language(client_user_id)
        user_notification = t(
            "admin_reply_received_by_user",
            client_lang,
            order_id=order_id,
            message_text=reply_content
        )

        # Send via safe_send_message
        success, err = safe_send_message(bot, client_user_id, user_notification)
        if success:
            bot.reply_to(
                message,
                f"✅ Сообщение по заявке #{order_id} успешно доставлено клиенту!",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton(f"◀️ Вернуться к заявке #{order_id}", callback_data=f"admin:view_order:{order_id}")
                )
            )
        else:
            bot.reply_to(
                message,
                f"❌ Не удалось отправить сообщение: {err}",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton(f"◀️ Вернуться к заявке #{order_id}", callback_data=f"admin:view_order:{order_id}")
                )
            )
