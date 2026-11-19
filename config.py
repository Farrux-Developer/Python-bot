"""Application configuration, constants, and data catalogs.

Loads environment variables, validates settings, and defines catalogs for:
- Services and add-on options
- Portfolio showcase categories and case studies with auto-order hooks
- FAQ stages and development terms
- Currencies and deposit tiers
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# --- BOT & API CREDENTIALS ---
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
PROVIDER_TOKEN: str = os.getenv("PROVIDER_TOKEN", "").strip()

# --- ADMIN ID PARSING & VALIDATION ---
_raw_admin_id = os.getenv("ADMIN_ID", "").strip()
ADMIN_ID: int | None = None

if _raw_admin_id:
    try:
        ADMIN_ID = int(_raw_admin_id)
    except ValueError:
        logger.warning(
            f"Invalid ADMIN_ID in .env: '{_raw_admin_id}'. Expected an integer user ID. "
            "Admin features will be disabled until a valid ID is provided."
        )
else:
    logger.info("ADMIN_ID not configured in .env. Admin notifications will be skipped.")


def is_admin(user_id: int | None) -> bool:
    """Check if given user ID matches configured admin ID."""
    if user_id is None or ADMIN_ID is None:
        return False
    return user_id == ADMIN_ID


# --- GENERAL SETTINGS ---
DB_PATH: str = os.getenv("DB_PATH", "weborder_bot.db")
DEFAULT_LANGUAGE: str = "ru"
SUPPORTED_LANGUAGES: tuple[str, ...] = ("ru", "en", "uz")

# External links & developer contacts
GITHUB_URL: str = os.getenv("GITHUB_URL", "https://github.com/Farrux-Developer")
DEVELOPER_TG: str = os.getenv("DEVELOPER_TG", "https://t.me/farrux_igamberdiev")
DEVELOPER_USERNAME: str = os.getenv("DEVELOPER_USERNAME", "@farrux_igamberdiev")


# --- CATALOG: SERVICES ---
@dataclass(frozen=True)
class ServiceItem:
    """Represents a website development service."""
    key: str
    price: float
    days_min: int
    days_max: int
    name_ru: str
    name_en: str
    name_uz: str
    desc_ru: str
    desc_en: str
    desc_uz: str

    def get_name(self, lang: str = "ru") -> str:
        if lang == "en":
            return self.name_en
        if lang == "uz":
            return self.name_uz
        return self.name_ru

    def get_desc(self, lang: str = "ru") -> str:
        if lang == "en":
            return self.desc_en
        if lang == "uz":
            return self.desc_uz
        return self.desc_ru


SERVICES: dict[str, ServiceItem] = {
    "landing": ServiceItem(
        key="landing",
        price=50.0,
        days_min=3,
        days_max=5,
        name_ru="Landing Page",
        name_en="Landing Page",
        name_uz="Landing Page",
        desc_ru="Одностраничный сайт с высокой конверсией для лидогенерации.",
        desc_en="High-converting single-page website for lead generation.",
        desc_uz="Yuqori konversiyali bir sahifali veb-sayt."
    ),
    "corp": ServiceItem(
        key="corp",
        price=150.0,
        days_min=7,
        days_max=14,
        name_ru="Корпоративный сайт",
        name_en="Corporate Website",
        name_uz="Korporativ sayt",
        desc_ru="Многостраничный сайт компании с презентацией услуг и каталогом.",
        desc_en="Multi-page company website showcasing services and catalog.",
        desc_uz="Kompaniyaning xizmatlari va katalogi bilan ko'p sahifali sayt."
    ),
    "ecom": ServiceItem(
        key="ecom",
        price=250.0,
        days_min=14,
        days_max=25,
        name_ru="E-commerce",
        name_en="E-commerce Store",
        name_uz="Internet-do'kon",
        desc_ru="Полноценный интернет-магазин с корзиной, оплатой и заказами.",
        desc_en="Full-featured online store with shopping cart and online payments.",
        desc_uz="Savat, to'lov tizimlari va buyurtmalar bilan to'liq internet-do'kon."
    ),
    "portfolio": ServiceItem(
        key="portfolio",
        price=40.0,
        days_min=2,
        days_max=4,
        name_ru="Portfolio",
        name_en="Portfolio Website",
        name_uz="Portfolio sayt",
        desc_ru="Стильный сайт-визитка для демонстрации работ специалиста или студии.",
        desc_en="Stylish portfolio website to showcase specialist or studio works.",
        desc_uz="Mutaxassis yoki studiya ishlarini ko'rsatish uchun zamonaviy sayt."
    ),
    "blog": ServiceItem(
        key="blog",
        price=80.0,
        days_min=5,
        days_max=8,
        name_ru="Blog / Медиа",
        name_en="Blog / Media",
        name_uz="Blog / Media sayt",
        desc_ru="Удобная платформа для публикаций статей, новостей и контента.",
        desc_en="Convenient platform for articles, news, and digital content.",
        desc_uz="Maqolalar, yangiliklar va kontent chop etish uchun qulay platforma."
    ),
    "frontend": ServiceItem(
        key="frontend",
        price=50.0,
        days_min=3,
        days_max=6,
        name_ru="Только Frontend",
        name_en="Frontend Only",
        name_uz="Faqat Frontend",
        desc_ru="Качественная адаптивная вёрстка готового дизайна (Figma / PSD).",
        desc_en="Pixel-perfect responsive coding of Figma / design layouts.",
        desc_uz="Figma yoki tayyor dizayn asosida sifatli frontend dasturlash."
    ),
    "custom": ServiceItem(
        key="custom",
        price=100.0,
        days_min=10,
        days_max=30,
        name_ru="Custom Проект",
        name_en="Custom Project",
        name_uz="Maxsus loyiha",
        desc_ru="Индивидуальная разработка под нестандартные задачи (авансовый депозит).",
        desc_en="Bespoke custom development for tailored tasks (deposit).",
        desc_uz="Nostandart vazifalar uchun individual ishlab chiqish (depozit)."
    ),
}


# --- CATALOG: ADDITIONAL OPTIONS ---
@dataclass(frozen=True)
class OptionItem:
    """Represents an optional add-on feature in the quiz."""
    key: str
    price: float
    days: int
    name_ru: str
    name_en: str
    name_uz: str
    desc_ru: str
    desc_en: str
    desc_uz: str

    def get_name(self, lang: str = "ru") -> str:
        if lang == "en":
            return self.name_en
        if lang == "uz":
            return self.name_uz
        return self.name_ru


OPTIONS: dict[str, OptionItem] = {
    "responsive": OptionItem(
        key="responsive",
        price=25.0,
        days=1,
        name_ru="Адаптив под мобильные",
        name_en="Mobile Responsive",
        name_uz="Mobil moslashuvchanlik",
        desc_ru="Идеальное отображение на смартфонах и планшетах",
        desc_en="Seamless display across all smartphones and tablets",
        desc_uz="Smartfon va planshetlarda a'lo darajada ko'rinish"
    ),
    "seo": OptionItem(
        key="seo",
        price=30.0,
        days=1,
        name_ru="SEO-база",
        name_en="Basic SEO Setup",
        name_uz="Asosiy SEO",
        desc_ru="Метатеги, микроразметка, Open Graph и фавикон",
        desc_en="Meta tags, schema markup, Open Graph, and favicon",
        desc_uz="Meta teglar, Open Graph va qidiruv tizimlariga moslashtirish"
    ),
    "crm": OptionItem(
        key="crm",
        price=40.0,
        days=2,
        name_ru="CRM / Telegram уведомления",
        name_en="CRM / Telegram Alerts",
        name_uz="CRM / Telegram bildirishnomalar",
        desc_ru="Моментальная отправка заявок с сайта в Telegram-чат или CRM",
        desc_en="Instant lead notifications to Telegram chat or CRM system",
        desc_uz="Saytdan kelgan buyurtmalarni Telegram yoki CRM ga yuborish"
    ),
    "copywriting": OptionItem(
        key="copywriting",
        price=35.0,
        days=2,
        name_ru="Копирайтинг текстов",
        name_en="Copywriting",
        name_uz="Kopirayting (matnlar)",
        desc_ru="Продающие тексты и структурирование информации",
        desc_en="High-converting sales copy and structured content",
        desc_uz="Sotuvchi matnlar va ma'lumotlarni to'g'ri joylashtirish"
    ),
    "branding": OptionItem(
        key="branding",
        price=45.0,
        days=2,
        name_ru="Логотип / Айдентика",
        name_en="Logo / Brand Identity",
        name_uz="Logotip / Brend aydentikasi",
        desc_ru="Разработка логотипа, подбор шрифтов и цветовой палитры",
        desc_en="Logo creation, font pairings, and custom color palette",
        desc_uz="Logotip yaratish, shriftlar va ranglar uyg'unligi"
    ),
    "urgent": OptionItem(
        key="urgent",
        price=50.0,
        days=-1,
        name_ru="Срочная разработка ⚡",
        name_en="Urgent Delivery ⚡",
        name_uz="Tezkor ishlab chiqish ⚡",
        desc_ru="Приоритетное выполнение в ускоренные сроки",
        desc_en="Priority rush delivery with shortened turnaround",
        desc_uz="Birinchi darajali tezkor navbat bilan topshirish"
    ),
}


# --- CATALOG: PORTFOLIO CASE STUDIES ---
@dataclass(frozen=True)
class PortfolioCase:
    """Represents a real-world case study in the portfolio showcase."""
    id: str
    category: str
    service_key: str
    title_ru: str
    title_en: str
    title_uz: str
    stack: str
    desc_ru: str
    desc_en: str
    desc_uz: str
    metrics_ru: str
    metrics_en: str
    metrics_uz: str
    demo_url: str

    def get_title(self, lang: str = "ru") -> str:
        if lang == "en":
            return self.title_en
        if lang == "uz":
            return self.title_uz
        return self.title_ru

    def get_desc(self, lang: str = "ru") -> str:
        if lang == "en":
            return self.desc_en
        if lang == "uz":
            return self.desc_uz
        return self.desc_ru

    def get_metrics(self, lang: str = "ru") -> str:
        if lang == "en":
            return self.metrics_en
        if lang == "uz":
            return self.metrics_uz
        return self.metrics_ru


PORTFOLIO_CATEGORIES = {
    "landing": {"ru": "🚀 Лендинги", "en": "🚀 Landing Pages", "uz": "🚀 Lendinglar"},
    "ecom": {"ru": "🛒 Интернет-магазины", "en": "🛒 E-commerce", "uz": "🛒 Internet-do'konlar"},
    "corp": {"ru": "🏢 Корпоративные сайты", "en": "🏢 Corporate Sites", "uz": "🏢 Korporativ saytlar"},
    "frontend": {"ru": "💻 UI & Вёрстка", "en": "💻 UI & Frontend", "uz": "💻 UI & Frontend"},
}

PORTFOLIO_CASES: list[PortfolioCase] = [
    PortfolioCase(
        id="case_ai_saas",
        category="landing",
        service_key="landing",
        title_ru="SaaS Платформа AI-Ассистента",
        title_en="AI Assistant SaaS Platform",
        title_uz="AI Yordamchi SaaS Platformasi",
        stack="Next.js 14, TailwindCSS, TypeScript, Framer Motion",
        desc_ru="Высококонверсионный промо-лендинг для подписочного AI-продукта с интерактивным калькулятором выгоды.",
        desc_en="High-converting promo landing page for an AI subscription product featuring interactive ROI calculator.",
        desc_uz="Interaktiv foyda kalkulyatori bilan obunali AI-mahsulot uchun yuqori konversiyali lending.",
        metrics_ru="📈 Конверсия в регистрацию: 8.4% (в 2.5 раза выше рынка)\n⚡ Google PageSpeed: 99/100, время первой отрисовки 0.7с.",
        metrics_en="📈 Conversion rate: 8.4% (2.5x industry average)\n⚡ Google PageSpeed: 99/100, FCP 0.7s.",
        metrics_uz="📈 Ro'yxatdan o'tish konversiyasi: 8.4%\n⚡ Google PageSpeed: 99/100, FCP 0.7s.",
        demo_url="https://github.com/Farrux-Developer"
    ),
    PortfolioCase(
        id="case_concept_store",
        category="ecom",
        service_key="ecom",
        title_ru="Concept Store Дизайнерской Одежды",
        title_en="Designer Clothing Concept Store",
        title_uz="Dizaynerlik Kiyimlari Internet-Do'koni",
        stack="React, Python / FastAPI, PostgreSQL, Telegram WebApp",
        desc_ru="Интернет-магазин с каталогом, фильтрами по размерам, корзиной и моментальным оформлением через Telegram.",
        desc_en="Online store with catalog, size filters, cart, and instant Telegram checkout.",
        desc_uz="Katalog, o'lchamlar bo'yicha filtrlar, savat va Telegram orqali tezkor buyurtma tizimi.",
        metrics_ru="🛍 450+ заказов в первый месяц запуска\n💳 Подключены Payme, Click и международный Stripe.",
        metrics_en="🛍 450+ orders in the first launch month\n💳 Integrated Payme, Click and Stripe.",
        metrics_uz="🛍 Birinchi oyda 450+ buyurtma\n💳 Payme, Click va Stripe to'lov tizimlari ulangan.",
        demo_url="https://github.com/Farrux-Developer"
    ),
    PortfolioCase(
        id="case_logistics_corp",
        category="corp",
        service_key="corp",
        title_ru="TransGlobal — Международная Логистика",
        title_en="TransGlobal — International Logistics",
        title_uz="TransGlobal — Xalqaro Logistika",
        stack="Django, Vue 3, TailwindCSS, REST API, CRM Webhook",
        desc_ru="Многостраничный корпоративный портал для логистической компании с трекингом грузов и калькулятором фрахта.",
        desc_en="Multi-page corporate portal for a logistics provider with live cargo tracking and freight calculator.",
        desc_uz="Yuklarni kuzatish va fraxt kalkulyatori bilan xalqaro logistika portali.",
        metrics_ru="💼 Рост B2B заявок на 65%\n🔗 Полная интеграция с CRM (Bitrix24) и Telegram-уведомлениями для диспетчеров.",
        metrics_en="💼 65% increase in B2B qualified leads\n🔗 Complete CRM (Bitrix24) and dispatcher Telegram notification integration.",
        metrics_uz="💼 B2B buyurtmalarning 65% o'sishi\n🔗 CRM va Telegram bildirishnomalar bilan to'liq integratsiya.",
        demo_url="https://github.com/Farrux-Developer"
    ),
    PortfolioCase(
        id="case_crypto_ui",
        category="frontend",
        service_key="frontend",
        title_ru="Crypto & DeFi Dashboard (Pixel-Perfect)",
        title_en="Crypto & DeFi Dashboard (Pixel-Perfect)",
        title_uz="Kripto & DeFi Boshqaruv Paneli",
        stack="HTML5 / SCSS / TailwindCSS / Webpack, Chart.js",
        desc_ru="Адаптивная вёрстка сложного дашборда аналитики с темной/светлой темой и анимациями данных.",
        desc_en="Responsive coding of an intricate crypto dashboard with dark/light themes and 60 FPS charts.",
        desc_uz="To'q/och rangli mavzular va 60 FPS grafiklar bilan murakkab tahliliy panel vyorstkasi.",
        metrics_ru="🎯 100% совпадение с макетом Figma (Pixel-Perfect)\n📱 Корректная работа на экранах от 320px до 4K UltraHD.",
        metrics_en="🎯 100% Figma layout match (Pixel-Perfect)\n📱 Flawless responsive layout from 320px to 4K UltraHD.",
        metrics_uz="🎯 Figma dizayniga 100% moslik (Pixel-Perfect)\n📱 320px dan 4K gacha to'liq moslashuvchanlik.",
        demo_url="https://github.com/Farrux-Developer"
    ),
]


# --- DEPOSIT TIERS ---
DEPOSIT_TIERS = {
    "30": {"percent": 0.30, "label_ru": "30% (Бронь очереди)", "label_en": "30% (Slot Reservation)", "label_uz": "30% (Navbatni band qilish)"},
    "50": {"percent": 0.50, "label_ru": "50% (Стандартный аванс)", "label_en": "50% (Standard Deposit)", "label_uz": "50% (Standart depozit)"},
    "100": {"percent": 1.00, "label_ru": "100% (Полная оплата)", "label_en": "100% (Full Payment)", "label_uz": "100% (To'liq to'lov)"},
}
