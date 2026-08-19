import os
import telebot
from telebot import types
from dotenv import load_dotenv

# Загружаем секретные данные из файла .env
load_dotenv()

# --- НАСТРОЙКИ БОТА ---
# Берем данные из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Проверка, что токен загрузился (чтобы бот не падал без причины)
if not TOKEN:
    raise ValueError("ОШИБКА: Токен бота не найден! Проверьте файл .env")

bot = telebot.TeleBot(TOKEN)
# --- БАЗА ДАННЫХ УСЛУГ (Прайс-лист) ---
SERVICES = {
    'landing': {'name': 'Landing Page', 'price': 50, 'desc': 'Одностраничный сайт с высокой конверсией. Идеально для продажи одного продукта или услуги.'},
    'corp': {'name': 'Корпоративный сайт', 'price': 150, 'desc': 'Многостраничный сайт компании. Представительство вашего бизнеса в сети.'},
    'ecom': {'name': 'E-commerce', 'price': 250, 'desc': 'Полноценный интернет-магазин с корзиной, каталогом и системой оплаты.'},
    'portfolio': {'name': 'Portfolio', 'price': 40, 'desc': 'Красивый сайт-визитка для демонстрации ваших работ и навыков.'},
    'blog': {'name': 'Blog', 'price': 80, 'desc': 'Платформа для публикации статей, новостей и взаимодействия с аудиторией.'},
    'frontend': {'name': 'Только Frontend', 'price': 50, 'desc': 'Качественная верстка по вашему дизайну (Figma/Photoshop).'},
    'custom': {'name': 'Custom Проект', 'price': 100, 'desc': 'Индивидуальная разработка. (Цена указана как депозит для старта работы).'}
}

# --- ГЛАВНОЕ МЕНЮ ---
def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🛒 Заказать сайт", callback_data="menu_order")
    btn2 = types.InlineKeyboardButton("💵 Прайс-лист", callback_data="menu_pricing")
    btn3 = types.InlineKeyboardButton("📁 Портфолио", callback_data="menu_portfolio")
    btn4 = types.InlineKeyboardButton("📞 Контакты", callback_data="menu_contact")
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4)
    return markup

# --- ОБРАБОТЧИКИ КОМАНД ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "👋 <b>Добро пожаловать в WebOrder Bot!</b>\n\n"
        "Я помогу вам быстро и удобно заказать разработку сайта у профессионала. "
        "Выберите нужный раздел в меню ниже, чтобы начать."
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_main_menu())

# --- ОБРАБОТКА НАЖАТИЙ НА КНОПКИ (CALLBACK) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # 1. Раздел: Прайс-лист
    if call.data == "menu_pricing":
        text = "💵 <b>Примерная стоимость разработки:</b>\n\n"
        for key, service in SERVICES.items():
            text += f"🔹 <b>{service['name']}</b> — от ${service['price']}\n"
        
        text += "\n<i>Точная стоимость рассчитывается индивидуально. Вы можете сразу заказать сайт или оплатить депозит.</i>"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("◀️ Назад в меню", callback_data="menu_main"))
        bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=markup)

    # 2. Раздел: Портфолио
    elif call.data == "menu_portfolio":
        text = "📁 <b>Мои работы и проекты</b>\n\nВы можете ознакомиться с моим стилем кода и готовыми проектами на GitHub."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Перейти на GitHub 🌐", url="https://github.com/Farrux-Developer"))
        markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="menu_main"))
        bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=markup)

    # 3. Раздел: Контакты
    elif call.data == "menu_contact":
        text = "📞 <b>Связь с разработчиком</b>\n\nЕсли у вас есть техническое задание, вопросы или нестандартный проект — пишите мне напрямую."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Написать разработчику ✍️", url="https://t.me/far_rux0"))
        markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="menu_main"))
        bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=markup)

    # 4. Раздел: Оформление заказа (Выбор типа)
    elif call.data == "menu_order":
        text = "🛒 <b>Выберите тип сайта, который вам нужен:</b>"
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, service in SERVICES.items():
            markup.add(types.InlineKeyboardButton(f"{service['name']} (от ${service['price']})", callback_data=f"buy_{key}"))
        markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="menu_main"))
        bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=markup)

    # 5. Возврат в главное меню
    elif call.data == "menu_main":
        text = "👋 Выберите нужный раздел:"
        bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=get_main_menu())

    # 6. Подготовка к оплате конкретной услуги
    elif call.data.startswith("buy_"):
        service_key = call.data.split("_")[1]
        service = SERVICES[service_key]
        
        text = (
            f"✅ <b>Отличный выбор!</b>\n\n"
            f"<b>Услуга:</b> {service['name']}\n"
            f"<b>Описание:</b> {service['desc']}\n"
            f"<b>Базовая стоимость:</b> ${service['price']}\n\n"
            f"Вы можете оплатить базовую стоимость прямо сейчас через Telegram. "
            f"Сразу после оплаты я свяжусь с вами для обсуждения дизайна и деталей."
        )
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("💳 Оплатить сейчас", callback_data=f"pay_{service_key}"))
        markup.add(types.InlineKeyboardButton("Сначала обсудить с разработчиком ✍️", url="https://t.me/far_rux0"))
        markup.add(types.InlineKeyboardButton("◀️ Назад к выбору", callback_data="menu_order"))
        
        bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=markup)

    # 7. Выставление счета (Invoice)
    elif call.data.startswith("pay_"):
        if PROVIDER_TOKEN == 'ТВОЙ_ПЛАТЕЖНЫЙ_ТОКЕН_ИЗ_BOTFATHER':
            bot.answer_callback_query(call.id, "Оплата временно недоступна. Не настроен токен провайдера.", show_alert=True)
            return

        service_key = call.data.split("_")[1]
        service = SERVICES[service_key]
        
        # Переводим доллары в центы (Telegram принимает копейки/центы)
        price_in_cents = int(service['price'] * 100) 
        prices = [types.LabeledPrice(label=f"Разработка: {service['name']}", amount=price_in_cents)]
        
        bot.send_invoice(
            chat_id=chat_id,
            title=f"Заказ: {service['name']}",
            description=service['desc'],
            invoice_payload=f"invoice_{service_key}_{chat_id}",
            provider_token=PROVIDER_TOKEN,
            currency='USD', # Можно поменять на UZS или RUB в зависимости от провайдера
            prices=prices,
            start_parameter="web_order",
            is_flexible=False
        )
        bot.answer_callback_query(call.id)

# --- ПРОВЕРКА ПЛАТЕЖА (ОБЯЗАТЕЛЬНЫЙ ЭТАП TELEGRAM API) ---
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    # Здесь бот подтверждает, что готов принять платеж
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# --- УСПЕШНАЯ ОПЛАТА ---
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    payment_info = message.successful_payment
    amount_paid = payment_info.total_amount / 100
    currency = payment_info.currency
    
    # 1. Сообщаем клиенту
    bot.send_message(
        message.chat.id, 
        f"🎉 <b>Успешно!</b>\n\nОплата в размере {amount_paid} {currency} получена.\n"
        f"Огромное спасибо за заказ! Я уже получил уведомление и свяжусь с вами в ближайшее время.",
        parse_mode='HTML',
        reply_markup=get_main_menu()
    )
    
    # 2. Уведомляем администратора (тебя)
    username = message.from_user.username
    contact_link = f"@{username}" if username else f"ID: {message.from_user.id}"
    
    admin_text = (
        f"💰 <b>НОВЫЙ ЗАКАЗ И ОПЛАТА!</b>\n\n"
        f"<b>Сумма:</b> {amount_paid} {currency}\n"
        f"<b>Payload:</b> {payment_info.invoice_payload}\n"
        f"<b>Клиент:</b> {contact_link}\n\n"
        f"Свяжись с клиентом для начала работы!"
    )
    try:
        bot.send_message(ADMIN_ID, admin_text, parse_mode='HTML')
    except Exception as e:
        print("Не удалось отправить уведомление админу. Проверь ADMIN_ID.")

# Запуск
if __name__ == '__main__':
    print("Бот запущен и готов к работе с платежами...")
    bot.polling(none_stop=True)