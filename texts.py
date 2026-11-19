"""Multilingual localization dictionary and helper functions.

Supports Russian (ru), English (en), and Uzbek (uz).
"""

from __future__ import annotations

from typing import Any

TEXTS: dict[str, dict[str, str]] = {
    # --- COMMON & NAVIGATION ---
    "welcome": {
        "ru": (
            "👋 <b>Добро пожаловать в WebOrder Bot!</b>\n\n"
            "Я помогу вам составить ТЗ, рассчитать смету и заказать разработку современного сайта у профессионального разработчика.\n\n"
            "Выберите нужный раздел в меню ниже 👇"
        ),
        "en": (
            "👋 <b>Welcome to WebOrder Bot!</b>\n\n"
            "I will help you prepare specifications, calculate project estimate, and order a high-quality website.\n\n"
            "Select an option from the menu below 👇"
        ),
        "uz": (
            "👋 <b>WebOrder Bot-ga xush kelibsiz!</b>\n\n"
            "Men sizga texnik topshiriq tuzishda, narxni hisoblashda va zamonaviy veb-sayt buyurtma qilishda yordam beraman.\n\n"
            "Quyidagi menyudan kerakli bo'limni tanlang 👇"
        ),
    },
    "choose_section": {
        "ru": "👋 Выберите нужный раздел:",
        "en": "👋 Choose a section:",
        "uz": "👋 Kerakli bo'limni tanlang:",
    },
    "help_text": {
        "ru": (
            "ℹ️ <b>Как пользоваться ботом:</b>\n\n"
            "• Нажмите <b>«🛒 Заказать сайт»</b> для прохождения 4-шагового квиза (выбор типа сайта, доп. опций, расчёт бюджета и контакт).\n"
            "• В разделе <b>«📁 Портфолио»</b> можно посмотреть реальные кейсы с метриками и заказать похожий сайт в 1 клик.\n"
            "• Раздел <b>«❓ FAQ / Как мы работаем»</b> расскажет об этапах, гарантиях и предоплате.\n"
            "• <b>«💵 Прайс-лист»</b> покажет базовые тарифы разработчика.\n"
            "• По всем вопросам можно связаться лично через <b>«📞 Контакты»</b>."
        ),
        "en": (
            "ℹ️ <b>How to use the bot:</b>\n\n"
            "• Click <b>«🛒 Order Website»</b> to complete the 4-step quiz (type, add-ons, budget, contacts).\n"
            "• In <b>«📁 Portfolio»</b> browse real case studies with performance metrics and clone them in 1 click.\n"
            "• In <b>«❓ FAQ & Workflow»</b> read about stages, milestones, and guarantees.\n"
            "• <b>«💵 Price List»</b> displays starting rates.\n"
            "• Direct developer access via <b>«📞 Contacts»</b>."
        ),
        "uz": (
            "ℹ️ <b>Botdan qanday foydalanish mumkin:</b>\n\n"
            "• Sayt buyurtma qilish uchun <b>«🛒 Sayt buyurtma qilish»</b> tugmasini bosing.\n"
            "• <b>«📁 Portfolio»</b> bo'limida tayyor loyihalar va ko'rsatkichlarni ko'rib, 1 bosishda o'xshashini buyurtma qiling.\n"
            "• <b>«❓ FAQ / Ish tartibi»</b> bo'limida bosqichlar va kafolatlar yozilgan.\n"
            "• <b>«💵 Narxlar»</b> bo'limida boshlang'ich narxlar keltirilgan.\n"
            "• Shaxsiy savollar bo'yicha <b>«📞 Aloqa»</b> bo'limidan foydalaning."
        ),
    },
    # Main menu buttons
    "btn_menu_order": {
        "ru": "🛒 Заказать сайт",
        "en": "🛒 Order Website",
        "uz": "🛒 Sayt buyurtma qilish",
    },
    "btn_menu_pricing": {
        "ru": "💵 Прайс-лист",
        "en": "💵 Price List",
        "uz": "💵 Narxlar",
    },
    "btn_menu_portfolio": {
        "ru": "📁 Портфолио & Кейсы",
        "en": "📁 Portfolio & Cases",
        "uz": "📁 Portfolio & Keyslar",
    },
    "btn_menu_faq": {
        "ru": "❓ FAQ / Как мы работаем",
        "en": "❓ FAQ & How We Work",
        "uz": "❓ FAQ / Ish tartibi",
    },
    "btn_menu_contact": {
        "ru": "📞 Контакты",
        "en": "📞 Contact",
        "uz": "📞 Aloqa",
    },
    "btn_menu_lang": {
        "ru": "🌐 Язык / Language",
        "en": "🌐 Language / Язык",
        "uz": "🌐 Til / Language",
    },
    "btn_menu_admin": {
        "ru": "👑 Панель управления",
        "en": "👑 Admin Dashboard",
        "uz": "👑 Boshqaruv paneli",
    },
    "btn_back_main": {
        "ru": "◀️ В главное меню",
        "en": "◀️ Back to menu",
        "uz": "◀️ Bosh menyuga",
    },
    "btn_back": {
        "ru": "◀️ Назад",
        "en": "◀️ Back",
        "uz": "◀️ Orqaga",
    },
    "btn_cancel": {
        "ru": "❌ Отменить заявку",
        "en": "❌ Cancel Order",
        "uz": "❌ Bekor qilish",
    },
    "btn_next": {
        "ru": "➡️ Далее",
        "en": "➡️ Next",
        "uz": "➡️ Keyingisi",
    },
    "btn_skip": {
        "ru": "⏩ Пропустить",
        "en": "⏩ Skip",
        "uz": "⏩ O'tkazib yuborish",
    },
    # --- PRICING & CONTACTS ---
    "pricing_title": {
        "ru": "💵 <b>Примерная стоимость разработки сайтов:</b>\n\n",
        "en": "💵 <b>Estimated development rates:</b>\n\n",
        "uz": "💵 <b>Sayt ishlab chiqish taxminiy narxlari:</b>\n\n",
    },
    "pricing_footer": {
        "ru": "\n<i>💡 Точная стоимость и сроки рассчитываются индивидуально под ваши задачи в квизе.</i>",
        "en": "\n<i>💡 Final cost and timeline are calculated based on your custom requirements in the quiz.</i>",
        "uz": "\n<i>💡 Yakuniy narx va muddat sizning vazifangizga qarab kvisda hisoblanadi.</i>",
    },
    "contact_title": {
        "ru": (
            "📞 <b>Связь с разработчиком</b>\n\n"
            "Для персональной консультации, обсуждения нестандартных ТЗ или сотрудничества напишите напрямую:"
        ),
        "en": (
            "📞 <b>Developer Contacts</b>\n\n"
            "For personal consultations, custom specifications, or business inquiries, feel free to reach out:"
        ),
        "uz": (
            "📞 <b>Dasturchi bilan bog'lanish</b>\n\n"
            "Shaxsiy maslahat, murakkab loyihalarni muhokama qilish yoki hamkorlik uchun to'g'ridan-to'g'ri yozing:"
        ),
    },
    "contact_btn_write": {
        "ru": "Написать разработчику ✍️",
        "en": "Message developer ✍️",
        "uz": "Dasturchiga yozish ✍️",
    },
    "lang_select_title": {
        "ru": "🌐 <b>Выберите язык интерфейса / Select interface language:</b>",
        "en": "🌐 <b>Select interface language / Выберите язык интерфейса:</b>",
        "uz": "🌐 <b>Interfeys tilini tanlang:</b>",
    },
    "lang_changed": {
        "ru": "✅ Язык успешно изменен на <b>Русский</b>.",
        "en": "✅ Language successfully switched to <b>English</b>.",
        "uz": "✅ Til muvaffaqiyatli <b>O'zbekcha</b>ga o'zgartirildi.",
    },
    # --- FAQ & HOW WE WORK ---
    "faq_title": {
        "ru": (
            "❓ <b>Как мы работаем и гарантии:</b>\n\n"
            "<b>1. Брифинг и ТЗ:</b>\n"
            "Вы проходите опрос в боте или отправляете референсы. Мы фиксируем структуру, функции и смету.\n\n"
            "<b>2. Прототип и дизайн:</b>\n"
            "Разрабатываем кликабельный макет в Figma с учетом адаптивности под смартфоны.\n\n"
            "<b>3. Разработка и оптимизация:</b>\n"
            "Пишем чистый, масштабируемый код (Next.js/React/Tailwind/FastAPI). Обеспечиваем скорость загрузки 90+ в Google PageSpeed.\n\n"
            "<b>4. Запуск и передача:</b>\n"
            "Подключаем домен, SSL, настраиваем сервер, обучаем управлению контентом.\n\n"
            "─────────────\n"
            "🛡 <b>Гарантии и условия:</b>\n"
            "• <b>Предоплата:</b> Депозит 30% или 50% перед стартом, остаток — после демонстрации готового сайта.\n"
            "• <b>Правки:</b> До 3 кругов правок включены бесплатно.\n"
            "• <b>Поддержка:</b> 30 дней бесплатного гарантийного обслуживания после сдачи проекта."
        ),
        "en": (
            "❓ <b>Workflow, Milestones & Guarantees:</b>\n\n"
            "<b>1. Briefing & Specifications:</b>\n"
            "You submit requirements via bot quiz. We lock down structure, features, and timeline.\n\n"
            "<b>2. Prototyping & UX/UI:</b>\n"
            "We design responsive layouts in Figma optimized for mobile conversions.\n\n"
            "<b>3. Development & Performance:</b>\n"
            "Modern clean architecture (Next.js/React/Tailwind). 90+ Google PageSpeed score.\n\n"
            "<b>4. Launch & Handoff:</b>\n"
            "Domain setup, SSL certificate, server deploy, CMS onboarding.\n\n"
            "─────────────\n"
            "🛡 <b>Terms & Guarantees:</b>\n"
            "• <b>Payment:</b> 30% or 50% deposit to commence work, balance upon final client signoff.\n"
            "• <b>Revisions:</b> Up to 3 revision iterations included free of charge.\n"
            "• <b>Support:</b> 30 days of complimentary warranty maintenance post-launch."
        ),
        "uz": (
            "❓ <b>Ish tartibi va kafolatlar:</b>\n\n"
            "<b>1. Brifing va Texnik topshiriq:</b>\n"
            "Bot orqali talablarni kiritasiz. Biz sayt tuzilishi, funksiyalari va smetasini kelishamiz.\n\n"
            "<b>2. Prototip va Dizayn:</b>\n"
            "Smartfonlar uchun qulay Figma maketini tayyorlaymiz va tasdiqlaymiz.\n\n"
            "<b>3. Dasturlash va Optimizatsiya:</b>\n"
            "Zamonaviy texnologiyalar (Next.js/React/FastAPI). Google PageSpeed 90+ tezlik.\n\n"
            "<b>4. Ishga tushirish:</b>\n"
            "Domen, SSL, server sozlash va boshqarishni o'rgatish.\n\n"
            "─────────────\n"
            "🛡 <b>Shartlar va kafolatlar:</b>\n"
            "• <b>Oldindan to'lov:</b> 30% yoki 50% depozit, qolgani sayt tayyor bo'lgach.\n"
            "• <b>Tahrirlar:</b> 3 martagacha o'zgartirishlar bepul.\n"
            "• <b>Kafolat:</b> Sayt topshirilgach 30 kun davomida bepul qo'llab-quvvatlash."
        ),
    },
    # --- PORTFOLIO SHOWCASE ---
    "portfolio_menu_title": {
        "ru": (
            "📁 <b>Портфолио разработчика</b>\n\n"
            "Выберите интересующую категорию проектов, чтобы изучить стек, реальные метрики и сразу заказать похожий сайт:"
        ),
        "en": (
            "📁 <b>Developer Portfolio</b>\n\n"
            "Select a project category to view real case studies, performance metrics, and order a similar site:"
        ),
        "uz": (
            "📁 <b>Dasturchi Portfoliosi</b>\n\n"
            "Loyiha toifasini tanlang, texnologiyalar va natijalar bilan tanishing:"
        ),
    },
    "portfolio_btn_want_similar": {
        "ru": "🔥 Хочу похожий сайт!",
        "en": "🔥 I want a similar website!",
        "uz": "🔥 Menga ham shunday sayt kerak!",
    },
    # --- QUIZ FLOW ---
    "quiz_step1_title": {
        "ru": "🛒 <b>Шаг 1 из 4: Выберите тип сайта</b>\n\nКакой проект вы планируете реализовать?",
        "en": "🛒 <b>Step 1 of 4: Select website type</b>\n\nWhat kind of project are you planning?",
        "uz": "🛒 <b>1-bosqich (4 tadan): Sayt turini tanlang</b>\n\nQanday loyihani amalga oshirmoqchisiz?",
    },
    "quiz_step1_desc_prompt": {
        "ru": (
            "📝 <b>Шаг 1 (продолжение): Описание задачи</b>\n\n"
            "Вы выбрали: <b>{service_name}</b>\n\n"
            "Отправьте текстом краткое описание вашего проекта, пожелания или ссылки на сайты-примеры (референсы).\n\n"
            "<i>Если у вас пока нет готового описания, просто нажмите «⏩ Пропустить».</i>"
        ),
        "en": (
            "📝 <b>Step 1 (cont.): Project Description</b>\n\n"
            "Selected: <b>{service_name}</b>\n\n"
            "Send a brief summary of your project, preferences, or reference links.\n\n"
            "<i>If you don't have specifications ready yet, simply click «⏩ Skip».</i>"
        ),
        "uz": (
            "📝 <b>1-bosqich (davomi): Vazifa tavsifi</b>\n\n"
            "Tanlandi: <b>{service_name}</b>\n\n"
            "Loyihangiz haqida qisqacha ma'lumot, talablar yoki misol (referens) havolalarini yuboring.\n\n"
            "<i>Agar tayyor tavsifingiz bo'lmasa, «⏩ O'tkazib yuborish» tugmasini bosing.</i>"
        ),
    },
    "quiz_desc_not_specified": {
        "ru": "Не указано (обсудим лично)",
        "en": "Not specified (to discuss directly)",
        "uz": "Ko'rsatilmadi (shaxsan muhokama qilinadi)",
    },
    "quiz_step2_title": {
        "ru": (
            "🛠 <b>Шаг 2 из 4: Дополнительные опции</b>\n\n"
            "Нажимайте на кнопки ниже, чтобы включить (✅) или выключить (⬜) нужные опции.\n"
            "Когда закончите выбор, нажмите <b>«➡️ Далее»</b>."
        ),
        "en": (
            "🛠 <b>Step 2 of 4: Additional Options</b>\n\n"
            "Click the buttons below to toggle (✅ / ⬜) required add-ons.\n"
            "When finished, click <b>«➡️ Next»</b>."
        ),
        "uz": (
            "🛠 <b>2-bosqich (4 tadan): Qo'shimcha opsiyalar</b>\n\n"
            "Kerakli opsiyalarni yoqish (✅) yoki o'chirish (⬜) uchun tugmalarni bosing.\n"
            "Tanlab bo'lgach, <b>«➡️ Keyingisi»</b> tugmasini bosing."
        ),
    },
    "quiz_step3_title": {
        "ru": (
            "📊 <b>Шаг 3 из 4: Расчёт стоимости и выбор бюджета</b>\n\n"
            "🔹 <b>Тип проекта:</b> {service_name} (базово от ${base_price})\n"
            "🔹 <b>Выбранные опции:</b>\n{options_list}\n\n"
            "💵 <b>Предварительная расчётная стоимость:</b> от <b>${total_price}</b>\n"
            "⏱ <b>Ориентировочные сроки:</b> <b>{days_min}–{days_max} рабочих дней</b>\n\n"
            "Выберите желаемый бюджет или укажите свою сумму:"
        ),
        "en": (
            "📊 <b>Step 3 of 4: Cost Calculation & Budget</b>\n\n"
            "🔹 <b>Project type:</b> {service_name} (base from ${base_price})\n"
            "🔹 <b>Selected options:</b>\n{options_list}\n\n"
            "💵 <b>Estimated preliminary price:</b> from <b>${total_price}</b>\n"
            "⏱ <b>Estimated timeline:</b> <b>{days_min}–{days_max} business days</b>\n\n"
            "Choose a budget tier or enter your custom amount:"
        ),
        "uz": (
            "📊 <b>3-bosqich (4 tadan): Narx hisobi va budjet tanlash</b>\n\n"
            "🔹 <b>Loyiha turi:</b> {service_name} (boshlang'ich ${base_price} dan)\n"
            "🔹 <b>Tanlangan opsiyalar:</b>\n{options_list}\n\n"
            "💵 <b>Dastlabki hisoblangan narx:</b> <b>${total_price}</b> dan\n"
            "⏱ <b>Taxminiy muddat:</b> <b>{days_min}–{days_max} ish kuni</b>\n\n"
            "Qulay budjetni tanlang yoki o'z sumangizni kiriting:"
        ),
    },
    "quiz_btn_calc_price": {
        "ru": "✅ Расчётный бюджет (от ${total_price})",
        "en": "✅ Calculated budget (from ${total_price})",
        "uz": "✅ Hisoblangan budjet (${total_price} dan)",
    },
    "quiz_btn_custom_budget": {
        "ru": "✏️ Указать свой бюджет",
        "en": "✏️ Enter custom budget",
        "uz": "✏️ O'z budjetimni yozish",
    },
    "quiz_prompt_custom_budget": {
        "ru": (
            "💰 <b>Введите ваш планируемый бюджет:</b>\n\n"
            "Например: <code>$250</code>, <code>2 500 000 сум</code> или напишите комментарий."
        ),
        "en": (
            "💰 <b>Enter your planned budget:</b>\n\n"
            "For example: <code>$250</code>, <code>200-400 USD</code>, or leave a note."
        ),
        "uz": (
            "💰 <b>Rejalashtirgan budjetingizni kiriting:</b>\n\n"
            "Masalan: <code>$250</code>, <code>2 500 000 so'm</code> yoki matn ko'rinishida yozing."
        ),
    },
    "quiz_step4_title": {
        "ru": (
            "📞 <b>Шаг 4 из 4: Контактные данные</b>\n\n"
            "Как с вами удобнее связаться?\n"
            "Напишите ваше <b>имя</b>, <b>номер телефона</b> или <b>@username</b> в Telegram."
        ),
        "en": (
            "📞 <b>Step 4 of 4: Contact Details</b>\n\n"
            "How should we reach you?\n"
            "Please send your <b>name</b>, <b>phone number</b>, or <b>@username</b>."
        ),
        "uz": (
            "📞 <b>4-bosqich (4 tadan): Aloqa ma'lumotlari</b>\n\n"
            "Siz bilan qanday bog'lanish qulay?\n"
            "Ismingiz, <b>telefon raqamingiz</b> yoki <b>@username</b>ni yozing."
        ),
    },
    "quiz_btn_use_tg": {
        "ru": "👤 Использовать мой Telegram ({username})",
        "en": "👤 Use my Telegram ({username})",
        "uz": "👤 Telegramimdan foydalanish ({username})",
    },
    "quiz_confirm_screen": {
        "ru": (
            "📋 <b>Проверьте вашу заявку перед отправкой:</b>\n\n"
            "🌐 <b>Тип сайта:</b> {service_name}\n"
            "📝 <b>ТЗ / Референс:</b> {description}\n"
            "🛠 <b>Опции:</b> {options}\n"
            "💵 <b>Бюджет:</b> {budget}\n"
            "⏱ <b>Сроки:</b> {terms}\n"
            "👤 <b>Контакты:</b> {contacts}\n\n"
            "<i>Все данные верны? Нажмите кнопку отправки ниже.</i>"
        ),
        "en": (
            "📋 <b>Review your order before submitting:</b>\n\n"
            "🌐 <b>Website Type:</b> {service_name}\n"
            "📝 <b>Requirements / Reference:</b> {description}\n"
            "🛠 <b>Options:</b> {options}\n"
            "💵 <b>Budget:</b> {budget}\n"
            "⏱ <b>Timeline:</b> {terms}\n"
            "👤 <b>Contacts:</b> {contacts}\n\n"
            "<i>Everything correct? Click the button below to submit.</i>"
        ),
        "uz": (
            "📋 <b>Yuborishdan oldin arizangizni tekshiring:</b>\n\n"
            "🌐 <b>Sayt turi:</b> {service_name}\n"
            "📝 <b>Texnik topshiriq / Havola:</b> {description}\n"
            "🛠 <b>Opsiyalar:</b> {options}\n"
            "💵 <b>Budjet:</b> {budget}\n"
            "⏱ <b>Muddat:</b> {terms}\n"
            "👤 <b>Aloqa:</b> {contacts}\n\n"
            "<i>Barchasi to'g'rimi? Quyidagi tasdiqlash tugmasini bosing.</i>"
        ),
    },
    "quiz_btn_confirm": {
        "ru": "✅ Подтвердить и отправить заявку",
        "en": "✅ Confirm & Submit Order",
        "uz": "✅ Tasdiqlash va arizani yuborish",
    },
    "quiz_btn_deposit_menu": {
        "ru": "💳 Внести аванс (онлайн)",
        "en": "💳 Pay Deposit Online",
        "uz": "💳 Avans to'lash (onlayn)",
    },
    "quiz_success": {
        "ru": (
            "🎉 <b>Ваша заявка #{order_id} успешно оформлена!</b>\n\n"
            "Разработчик получил подробное ТЗ и свяжется с вами в ближайшее время для согласования деталей."
        ),
        "en": (
            "🎉 <b>Your order #{order_id} has been submitted!</b>\n\n"
            "The developer has received your specifications and will contact you shortly to finalize details."
        ),
        "uz": (
            "🎉 <b>#{order_id}-raqamli arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
            "Dasturchi barcha ma'lumotlarni oldi va tafsilotlarni kelishish uchun tez orada siz bilan bog'lanadi."
        ),
    },
    "quiz_cancelled": {
        "ru": "❌ Оформление заявки отменено. Вы всегда можете начать заново из главного меню.",
        "en": "❌ Order submission cancelled. You can start over anytime from the main menu.",
        "uz": "❌ Ariza berish bekor qilindi. Bosh menyudan istalgan vaqtda qaytadan boshlashingiz mumkin.",
    },
    "prompt_text_only": {
        "ru": "⚠️ Пожалуйста, отправьте текстовое сообщение или нажмите кнопку.",
        "en": "⚠️ Please send a text message or click a button.",
        "uz": "⚠️ Iltimos, matnli xabar yuboring yoki tugmani bosing.",
    },
    # --- ADMIN NOTIFICATIONS & INTERFACES ---
    "admin_new_order_card": {
        "ru": (
            "🚀 <b>НОВАЯ ЗАЯВКА НА САЙТ #{order_id}!</b>\n\n"
            "👤 <b>Клиент:</b> {user_link}\n"
            "🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n"
            "🌐 <b>Тип сайта:</b> {service_name}\n"
            "📝 <b>ТЗ / Референс:</b>\n{description}\n\n"
            "🛠 <b>Доп. опции:</b>\n{options}\n\n"
            "💰 <b>Бюджет:</b> {budget}\n"
            "⏱ <b>Расчётные сроки:</b> {terms}\n"
            "📞 <b>Контакты для связи:</b> {contacts}\n"
            "📅 <b>Дата:</b> {created_at}\n"
            "📊 <b>Статус:</b> 🆕 Новая"
        ),
        "en": (
            "🚀 <b>NEW WEBSITE ORDER #{order_id}!</b>\n\n"
            "👤 <b>Client:</b> {user_link}\n"
            "🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n"
            "🌐 <b>Type:</b> {service_name}\n"
            "📝 <b>Brief / Reference:</b>\n{description}\n\n"
            "🛠 <b>Options:</b>\n{options}\n\n"
            "💰 <b>Budget:</b> {budget}\n"
            "⏱ <b>Estimated Timeline:</b> {terms}\n"
            "📞 <b>Contacts:</b> {contacts}\n"
            "📅 <b>Date:</b> {created_at}\n"
            "📊 <b>Status:</b> 🆕 New"
        ),
        "uz": (
            "🚀 <b>YANGI SAYT BUYURTMASI #{order_id}!</b>\n\n"
            "👤 <b>Mijoz:</b> {user_link}\n"
            "🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n"
            "🌐 <b>Sayt turi:</b> {service_name}\n"
            "📝 <b>Texnik topshiriq / Havola:</b>\n{description}\n\n"
            "🛠 <b>Opsiyalar:</b>\n{options}\n\n"
            "💰 <b>Budjet:</b> {budget}\n"
            "⏱ <b>Hisoblangan muddat:</b> {terms}\n"
            "📞 <b>Aloqa ma'lumotlari:</b> {contacts}\n"
            "📅 <b>Sana:</b> {created_at}\n"
            "📊 <b>Status:</b> 🆕 Yangi"
        ),
    },
    "user_status_changed_notify": {
        "ru": (
            "🔔 <b>Обновление по вашей заявке #{order_id}</b>\n\n"
            "Текущий статус: <b>{status_label}</b>\n\n"
            "<i>Если у вас есть вопросы, вы всегда можете написать разработчику напрямую.</i>"
        ),
        "en": (
            "🔔 <b>Update on your order #{order_id}</b>\n\n"
            "Current status: <b>{status_label}</b>\n\n"
            "<i>Feel free to contact the developer directly if you have questions.</i>"
        ),
        "uz": (
            "🔔 <b>#{order_id}-raqamli arizangiz bo'yicha yangilanish</b>\n\n"
            "Joriy holat: <b>{status_label}</b>\n\n"
            "<i>Savollaringiz bo'lsa, to'g'ridan-to'g'ri dasturchiga yozishingiz mumkin.</i>"
        ),
    },
    "admin_reply_received_by_user": {
        "ru": (
            "💬 <b>Сообщение от разработчика по заявке #{order_id}:</b>\n\n"
            "{message_text}\n\n"
            "<i>Вы можете ответить разработчику в личные сообщения или через бота.</i>"
        ),
        "en": (
            "💬 <b>Message from developer regarding order #{order_id}:</b>\n\n"
            "{message_text}"
        ),
        "uz": (
            "💬 <b>#{order_id}-raqamli buyurtma bo'yicha dasturchidan xabar:</b>\n\n"
            "{message_text}"
        ),
    },
    # Payments
    "payment_unavailable": {
        "ru": "⚠️ Онлайн-оплата через бота временно недоступна. Вы можете оформить заявку и договориться об оплате лично.",
        "en": "⚠️ Online payment is currently unavailable. You can submit the brief and arrange payment directly.",
        "uz": "⚠️ Bot orqali onlayn to'lov vaqtincha mavjud emas. Buyurtma berib, to'lovni shaxsan kelishishingiz mumkin.",
    },
    "payment_received_user": {
        "ru": (
            "🎉 <b>Оплата успешно получена!</b>\n\n"
            "🧾 <b>Чек заказа #{order_id}</b>\n"
            "💵 <b>Сумма:</b> {amount} {currency}\n"
            "💳 <b>Статус оплаты:</b> {payment_status}\n\n"
            "Спасибо за доверие! Разработчик приступил к работе над вашим проектом."
        ),
        "en": (
            "🎉 <b>Payment successfully received!</b>\n\n"
            "🧾 <b>Receipt for order #{order_id}</b>\n"
            "💵 <b>Amount:</b> {amount} {currency}\n"
            "💳 <b>Payment status:</b> {payment_status}\n\n"
            "Thank you! The developer has started working on your project."
        ),
        "uz": (
            "🎉 <b>To'lov muvaffaqiyatli qabul qilindi!</b>\n\n"
            "🧾 <b>#{order_id}-raqamli buyurtma cheki</b>\n"
            "💵 <b>Miqdor:</b> {amount} {currency}\n"
            "💳 <b>To'lov holati:</b> {payment_status}\n\n"
            "Rahmat! Dasturchi loyihangiz ustida ish boshladi."
        ),
    },
}


def t(key: str, lang: str = "ru", **kwargs: Any) -> str:
    """Retrieve localized text by key and format with kwargs.

    Args:
        key: Text translation identifier.
        lang: Language code ('ru', 'en', 'uz'). Defaults to 'ru'.
        **kwargs: Values to substitute into format string.

    Returns:
        Formatted translated string.
    """
    key_dict = TEXTS.get(key)
    if not key_dict:
        return key

    text_template = key_dict.get(lang) or key_dict.get("ru") or list(key_dict.values())[0]

    if kwargs:
        try:
            return text_template.format(**kwargs)
        except (KeyError, ValueError, IndexError):
            return text_template

    return text_template
