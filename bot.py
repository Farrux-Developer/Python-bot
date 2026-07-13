import telebot
from telebot import types

# Ваш токен от BotFather
TOKEN = '7652251280:AAED0e482EhSbiD6jnIyduDOZbXQMsqTNUo'
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "👋 Welcome to WebOrder Bot!\n"
        "I can help you order custom websites.\n\n"
        "📋 Commands:\n"
        "/order - Start a new website order\n"
        "/portfolio - View our work\n"
        "/pricing - See pricing options\n"
        "/contact - Contact information"
    )
    bot.send_message(message.chat.id, text)

# Обработчик команды /portfolio
@bot.message_handler(commands=['portfolio'])
def send_portfolio(message):
    text = "Мои работы и проекты вы можете посмотреть на моем GitHub аккаунте: \n👉 https://github.com/Farrux-Developer"
    bot.send_message(message.chat.id, text, disable_web_page_preview=True)

# Обработчик команды /pricing
@bot.message_handler(commands=['pricing'])
def send_pricing(message):
    # Цены примерные, вы сможете поменять их в любой момент
    text = (
        "💵 Примерная стоимость сайтов:\n\n"
        "1️⃣ Landing Page - от $50\n"
        "2️⃣ Корпоративный сайт - от $150\n"
        "3️⃣ E-commerce - от $250\n"
        "4️⃣ Portfolio - от $40\n"
        "5️⃣ Blog - от $80\n"
        "6️⃣ Frontend - от $50\n"
        "7️⃣ Custom - обсуждается индивидуально\n\n"
        "Точная стоимость рассчитывается после обсуждения деталей проекта. Используйте /order для заказа."
    )
    bot.send_message(message.chat.id, text)

# Обработчик команды /contact
@bot.message_handler(commands=['contact'])
def send_contact(message):
    text = "Для связи со мной и обсуждения проектов пишите мне напрямую: \n👉 @far_rux0"
    bot.send_message(message.chat.id, text)

# Обработчик команды /order
@bot.message_handler(commands=['order'])
def order_website(message):
    text = (
        "🛒 Заказ сайта\n"
        "Выберите тип сайта:\n"
        "1️⃣ Landing Page - одностраничный сайт\n"
        "2️⃣ Корпоративный сайт - многостраничный сайт компании\n"
        "3️⃣ E-commerce - интернет-магазин\n"
        "4️⃣ Portfolio - портфолио\n"
        "5️⃣ Blog - блог\n"
        "6️⃣ Frontend - только фронтенд\n"
        "7️⃣ Custom - индивидуальный проект\n\n"
        "Отправьте номер выбранного типа (1-7):"
    )
    msg = bot.send_message(message.chat.id, text)
    # Переходим к следующему шагу — ожиданию ввода номера от пользователя
    bot.register_next_step_handler(msg, process_order_step)

# Функция для обработки выбора пользователя (цифры 1-7)
def process_order_step(message):
    # Проверяем, что введена цифра от 1 до 7
    if message.text in ['1', '2', '3', '4', '5', '6', '7']:
        text = (
            "✅ Отличный выбор!\n\n"
            "Для обсуждения технического задания, сроков и финальной стоимости напишите мне лично: 👉 @far_rux0\n\n"
            "После того как мы договоримся обо всех деталях и утвердим цену, я скину вам номер своего крипто-кошелька/карты для оплаты.\n"
            "Сразу после получения оплаты я приступлю к разработке вашего сайта! 🚀"
        )
        bot.send_message(message.chat.id, text)
    else:
        # Если ввели что-то другое
        msg = bot.send_message(message.chat.id, "❌ Пожалуйста, отправьте только цифру от 1 до 7. Попробуйте еще раз:")
        bot.register_next_step_handler(msg, process_order_step)

# Запуск бота на постоянную работу (polling)
if __name__ == '__main__':
    print("Бот запущен и готов к работе...")
    # non_stop=True позволяет боту не падать при мелких ошибках сети
    bot.polling(none_stop=True)