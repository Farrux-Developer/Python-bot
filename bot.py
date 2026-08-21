import os
import logging
import telebot
from telebot import types
from dotenv import load_dotenv

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = telebot.TeleBot(TOKEN)

SERVICES = {
    'landing': {'name': 'Landing Page', 'price': 50, 'desc': 'Одностраничный сайт с высокой конверсией.'},
    'corp': {'name': 'Корпоративный сайт', 'price': 150, 'desc': 'Многостраничный сайт компании.'},
    'ecom': {'name': 'E-commerce', 'price': 250, 'desc': 'Полноценный интернет-магазин.'},
    'portfolio': {'name': 'Portfolio', 'price': 40, 'desc': 'Красивый сайт-визитка.'},
    'blog': {'name': 'Blog', 'price': 80, 'desc': 'Платформа для публикаций.'},
    'frontend': {'name': 'Только Frontend', 'price': 50, 'desc': 'Верстка по дизайну.'},
    'custom': {'name': 'Custom Проект', 'price': 100, 'desc': 'Индивидуальная разработка (депозит).'}
}

def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🛒 Заказать сайт", callback_data="menu_order"),
        types.InlineKeyboardButton("💵 Прайс-лист", callback_data="menu_pricing"),
        types.InlineKeyboardButton("📁 Портфолио", callback_data="menu_portfolio"),
        types.InlineKeyboardButton("📞 Контакты", callback_data="menu_contact")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f"User {message.from_user.id} started the bot.")
    text = (
        "👋 <b>Добро пожаловать в WebOrder Bot!</b>\n\n"
        "Я помогу вам быстро и удобно заказать разработку сайта у профессионала. "
        "Выберите нужный раздел в меню ниже."
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # ❗️ СРАЗУ ГАСИМ СКЕЛЕТОН (ответ Telegram)
    bot.answer_callback_query(call.id)
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    logger.info(f"Callback trigger: {call.data} from {chat_id}")

    try:
        if call.data == "menu_pricing":
            text = "💵 <b>Примерная стоимость разработки:</b>\n\n"
            for key, service in SERVICES.items():
                text += f"🔹 <b>{service['name']}</b> — от ${service['price']}\n"
            text += "\n<i>Точная стоимость рассчитывается индивидуально.</i>"
            
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("◀️ Назад в меню", callback_data="menu_main"))
            bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=markup)

        elif call.data == "menu_portfolio":
            text = "📁 <b>Мои работы и проекты</b>\n\nОзнакомьтесь с моим стилем кода на GitHub."
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Перейти на GitHub 🌐", url="https://github.com/Farrux-Developer"))
            markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="menu_main"))
            bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=markup)

        elif call.data == "menu_contact":
            text = "📞 <b>Связь с разработчиком</b>\n\nДля обсуждения ТЗ пишите напрямую."
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Написать ✍️", url="https://t.me/far_rux0"))
            markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="menu_main"))
            bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=markup)

        elif call.data == "menu_order":
            text = "🛒 <b>Выберите тип сайта:</b>"
            markup = types.InlineKeyboardMarkup(row_width=1)
            for key, service in SERVICES.items():
                markup.add(types.InlineKeyboardButton(f"{service['name']} (от ${service['price']})", callback_data=f"buy_{key}"))
            markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="menu_main"))
            bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=markup)

        elif call.data == "menu_main":
            bot.edit_message_text("👋 Выберите нужный раздел:", chat_id, message_id, parse_mode='HTML', reply_markup=get_main_menu())

        elif call.data.startswith("buy_"):
            service_key = call.data.split("_")[1]
            service = SERVICES[service_key]
            text = (
                f"✅ <b>Отличный выбор!</b>\n\n"
                f"<b>Услуга:</b> {service['name']}\n"
                f"<b>Описание:</b> {service['desc']}\n"
                f"<b>Базовая стоимость:</b> ${service['price']}\n\n"
                f"Вы можете оплатить депозит прямо сейчас."
            )
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("💳 Оплатить сейчас", callback_data=f"pay_{service_key}"))
            markup.add(types.InlineKeyboardButton("Обсудить с разработчиком ✍️", url="https://t.me/far_rux0"))
            markup.add(types.InlineKeyboardButton("◀️ Назад к выбору", callback_data="menu_order"))
            bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=markup)

        elif call.data.startswith("pay_"):
            if not PROVIDER_TOKEN or PROVIDER_TOKEN == 'ТВОЙ_ПЛАТЕЖНЫЙ_ТОКЕН_ИЗ_BOTFATHER':
                bot.send_message(chat_id, "Оплата временно недоступна.")
                return

            service_key = call.data.split("_")[1]
            service = SERVICES[service_key]
            price_in_cents = int(service['price'] * 100)
            prices = [types.LabeledPrice(label=f"Разработка: {service['name']}", amount=price_in_cents)]
            
            bot.send_invoice(
                chat_id=chat_id,
                title=f"Заказ: {service['name']}",
                description=service['desc'],
                invoice_payload=f"invoice_{service_key}_{chat_id}",
                provider_token=PROVIDER_TOKEN,
                currency='USD',
                prices=prices,
                start_parameter="web_order",
                is_flexible=False
            )
            
    except Exception as e:
        logger.error(f"Error handling callback: {e}", exc_info=True)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    payment_info = message.successful_payment
    amount_paid = payment_info.total_amount / 100
    currency = payment_info.currency
    
    bot.send_message(
        message.chat.id, 
        f"🎉 <b>Успешно!</b>\n\nОплата {amount_paid} {currency} получена.",
        parse_mode='HTML',
        reply_markup=get_main_menu()
    )
    
    username = message.from_user.username
    contact_link = f"@{username}" if username else f"ID: {message.from_user.id}"
    admin_text = (
        f"💰 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
        f"<b>Сумма:</b> {amount_paid} {currency}\n"
        f"<b>Клиент:</b> {contact_link}"
    )
    try:
        bot.send_message(ADMIN_ID, admin_text, parse_mode='HTML')
        logger.info(f"Payment received: {amount_paid} {currency} from {contact_link}")
    except Exception as e:
        logger.error("Failed to notify admin.", exc_info=True)

if __name__ == '__main__':
    logger.info("Бот запущен и готов к работе...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=90)
        except Exception as e:
            logger.error(f"Бот упал, перезапуск... Ошибка: {e}")