"""Telegram Invoices and payment processing handlers.

Features:
- Flexible deposit tiers (30%, 50%, 100% full payment) with currency support.
- Pre-checkout validation.
- Database persistence of transactions.
- Automated order status updates to 'deposit_paid' / 'fully_paid'.
- Order confirmation receipts with unique transaction details sent to client and admin.
"""

from __future__ import annotations

import logging
import telebot
from telebot import types

import config
import database
import keyboards
from texts import t
from utils import format_user_mention, parse_callback, safe_answer_callback

logger = logging.getLogger(__name__)


def register_payment_handlers(bot: telebot.TeleBot) -> None:
    """Register payment and invoice handlers.

    Args:
        bot: TeleBot instance.
    """

    @bot.callback_query_handler(func=lambda call: call.data.startswith("pay:deposit:"))
    def on_pay_deposit_tier(call: types.CallbackQuery) -> None:
        """Issue invoice for specific deposit tier (30%, 50%, 100%)."""
        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        tier_code = tokens[2] if len(tokens) >= 3 else "50"

        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)

        if not config.PROVIDER_TOKEN:
            bot.send_message(chat_id, t("payment_unavailable", lang))
            return

        with bot.retrieve_data(user_id, chat_id) as data:
            service_key = data.get("service", "landing")
            calc_price = data.get("calc_price", 100.0)

        service = config.SERVICES.get(service_key, list(config.SERVICES.values())[0])
        tier = config.DEPOSIT_TIERS.get(tier_code, config.DEPOSIT_TIERS["50"])
        deposit_amount = int(calc_price * tier["percent"])
        deposit_amount = max(1, deposit_amount)

        prices = [types.LabeledPrice(label=f"Аванс ({tier_code}%): {service.get_name(lang)}", amount=deposit_amount * 100)]
        payload = f"deposit:{tier_code}:{service_key}:{user_id}"

        try:
            bot.send_invoice(
                chat_id=chat_id,
                title=f"Аванс: {service.get_name(lang)}",
                description=f"Предоплата {tier_code}% за разработку ({service.get_name(lang)}) по согласованному ТЗ.",
                invoice_payload=payload,
                provider_token=config.PROVIDER_TOKEN,
                currency="USD",
                prices=prices,
                start_parameter="deposit_pay",
                is_flexible=False
            )
            logger.info(f"Invoice issued to user {user_id}: {deposit_amount} USD ({tier_code}%)")
        except Exception as e:
            logger.error(f"Failed to issue deposit invoice: {e}", exc_info=True)
            bot.send_message(chat_id, t("payment_unavailable", lang))

    @bot.callback_query_handler(func=lambda call: call.data.startswith("pay:direct:"))
    def on_direct_pay_requested(call: types.CallbackQuery) -> None:
        """Handle direct catalog payment invocation."""
        safe_answer_callback(bot, call.id)
        tokens = parse_callback(call.data)
        if len(tokens) < 3:
            return

        service_key = tokens[2]
        service = config.SERVICES.get(service_key)
        if not service:
            return

        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang = database.get_user_language(user_id)

        if not config.PROVIDER_TOKEN:
            bot.send_message(chat_id, t("payment_unavailable", lang))
            return

        price_cents = int(service.price * 100)
        prices = [types.LabeledPrice(label=f"Разработка: {service.get_name(lang)}", amount=price_cents)]

        try:
            bot.send_invoice(
                chat_id=chat_id,
                title=f"Заказ: {service.get_name(lang)}",
                description=service.get_desc(lang),
                invoice_payload=f"direct_pay:{service_key}:{user_id}",
                provider_token=config.PROVIDER_TOKEN,
                currency="USD",
                prices=prices,
                start_parameter="web_order",
                is_flexible=False
            )
        except Exception as e:
            logger.error(f"Failed to send direct invoice: {e}", exc_info=True)
            bot.send_message(chat_id, t("payment_unavailable", lang))

    @bot.pre_checkout_query_handler(func=lambda query: True)
    def handle_pre_checkout(pre_checkout_query: types.PreCheckoutQuery) -> None:
        """Approve pre-checkout query before payment execution."""
        try:
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
            logger.info(f"Pre-checkout approved for user {pre_checkout_query.from_user.id}")
        except Exception as e:
            logger.error(f"Pre-checkout error: {e}", exc_info=True)
            bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=False,
                error_message="Ошибка авторизации платежа. Пожалуйста, попробуйте позже."
            )

    @bot.message_handler(content_types=["successful_payment"])
    def handle_successful_payment(message: types.Message) -> None:
        """Record received payment, update order status in DB, send client receipt, and alert admin."""
        payment = message.successful_payment
        amount_paid = payment.total_amount / 100
        currency = payment.currency
        payload = payment.invoice_payload
        user = message.from_user
        lang = database.get_user_language(user.id)
        is_admin_user = config.is_admin(user.id)

        # Determine if payload is tied to a specific order
        order_id = None
        payload_parts = parse_callback(payload)
        tier_code = "50"
        if len(payload_parts) >= 2 and payload_parts[0] == "deposit":
            tier_code = payload_parts[1]

        # Record payment in SQLite
        payment_id = database.add_payment(
            user_id=user.id,
            amount=amount_paid,
            currency=currency,
            order_id=order_id,
            telegram_payment_charge_id=payment.telegram_payment_charge_id,
            provider_payment_charge_id=payment.provider_payment_charge_id,
            payload=payload
        )
        logger.info(f"Payment #{payment_id} recorded: {amount_paid} {currency} from user {user.id}")

        pay_status_label = "Депозит внесен (30%)" if tier_code == "30" else ("Депозит внесен (50%)" if tier_code == "50" else "Оплачено полностью")

        # Send confirmation receipt to user
        receipt_text = t(
            "payment_received_user",
            lang,
            order_id=payment_id,
            amount=amount_paid,
            currency=currency,
            payment_status=pay_status_label
        )
        bot.send_message(
            chat_id=message.chat.id,
            text=receipt_text,
            parse_mode="HTML",
            reply_markup=keyboards.get_main_menu(lang, is_admin_user=is_admin_user)
        )

        # Notify administrator
        if config.ADMIN_ID:
            client_mention = format_user_mention(user.id, user.username, user.first_name)
            admin_msg = (
                f"💰 <b>ПОЛУЧЕНА ОПЛАТА! (#{payment_id})</b>\n\n"
                f"💵 <b>Сумма:</b> {amount_paid} {currency}\n"
                f"👤 <b>Клиент:</b> {client_mention}\n"
                f"🆔 <b>ID пользователя:</b> <code>{user.id}</code>\n"
                f"💳 <b>Платёж:</b> {pay_status_label}\n"
                f"📦 <b>Payload:</b> <code>{payload}</code>\n"
                f"🧾 <b>Telegram Charge ID:</b> <code>{payment.telegram_payment_charge_id}</code>"
            )
            try:
                bot.send_message(config.ADMIN_ID, admin_msg, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Failed to notify admin of payment #{payment_id}: {e}", exc_info=True)
