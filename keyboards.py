"""Inline and Reply keyboards generator.

Builds responsive, multilingual markup for all user interactions, quiz steps,
portfolio showcases, deposit selections, and admin management controls.
"""

from __future__ import annotations

from telebot import types

import config
import database
from texts import t


def get_main_menu(lang: str = "ru", is_admin_user: bool = False) -> types.InlineKeyboardMarkup:
    """Generate main navigation menu."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(t("btn_menu_order", lang), callback_data="menu:order"),
        types.InlineKeyboardButton(t("btn_menu_pricing", lang), callback_data="menu:pricing"),
        types.InlineKeyboardButton(t("btn_menu_portfolio", lang), callback_data="menu:portfolio"),
        types.InlineKeyboardButton(t("btn_menu_faq", lang), callback_data="menu:faq"),
        types.InlineKeyboardButton(t("btn_menu_contact", lang), callback_data="menu:contact"),
        types.InlineKeyboardButton(t("btn_menu_lang", lang), callback_data="menu:lang"),
    )
    if is_admin_user:
        markup.add(
            types.InlineKeyboardButton(t("btn_menu_admin", lang), callback_data="admin:menu")
        )
    return markup


def get_language_keyboard() -> types.InlineKeyboardMarkup:
    """Generate language selection keyboard."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:set:ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang:set:en"),
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang:set:uz"),
        types.InlineKeyboardButton("◀️ В меню / Back", callback_data="menu:main"),
    )
    return markup


def get_pricing_keyboard(lang: str = "ru") -> types.InlineKeyboardMarkup:
    """Keyboard for pricing list view."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(t("btn_menu_order", lang), callback_data="menu:order"),
        types.InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main"),
    )
    return markup


def get_faq_keyboard(lang: str = "ru") -> types.InlineKeyboardMarkup:
    """Keyboard for FAQ / Workflow section."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(t("btn_menu_order", lang), callback_data="menu:order"),
        types.InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main"),
    )
    return markup


def get_contact_keyboard(lang: str = "ru") -> types.InlineKeyboardMarkup:
    """Keyboard for developer contacts view."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(t("contact_btn_write", lang), url=config.DEVELOPER_TG),
        types.InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main"),
    )
    return markup


# --- PORTFOLIO SHOWCASE KEYBOARDS ---

def get_portfolio_categories_keyboard(lang: str = "ru") -> types.InlineKeyboardMarkup:
    """Keyboard displaying portfolio categories."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    for cat_key, cat_names in config.PORTFOLIO_CATEGORIES.items():
        name = cat_names.get(lang) or cat_names.get("ru", cat_key)
        markup.add(types.InlineKeyboardButton(name, callback_data=f"portfolio:cat:{cat_key}"))
    markup.add(
        types.InlineKeyboardButton(t("portfolio_btn_gh", lang), url=config.GITHUB_URL)
    )
    markup.add(
        types.InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu:main")
    )
    return markup


def get_portfolio_cases_keyboard(category: str, lang: str = "ru") -> types.InlineKeyboardMarkup:
    """Keyboard listing projects in a chosen category."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    cases = [c for c in config.PORTFOLIO_CASES if c.category == category]
    for case in cases:
        markup.add(types.InlineKeyboardButton(f"📌 {case.get_title(lang)}", callback_data=f"portfolio:case:{case.id}"))
    markup.add(types.InlineKeyboardButton(t("btn_back", lang), callback_data="menu:portfolio"))
    return markup


def get_case_detail_keyboard(case: config.PortfolioCase, lang: str = "ru") -> types.InlineKeyboardMarkup:
    """Keyboard for single case study card."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(t("portfolio_btn_want_similar", lang), callback_data=f"quiz:start_with_service:{case.service_key}"),
        types.InlineKeyboardButton("🌐 Посмотреть демо / код", url=case.demo_url),
        types.InlineKeyboardButton(t("btn_back", lang), callback_data=f"portfolio:cat:{case.category}"),
    )
    return markup


# --- QUIZ KEYBOARDS ---

def get_services_keyboard(lang: str = "ru") -> types.InlineKeyboardMarkup:
    """Step 1: Website type selection keyboard."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    for key, s in config.SERVICES.items():
        button_text = f"{s.get_name(lang)} (от ${int(s.price)})"
        markup.add(types.InlineKeyboardButton(button_text, callback_data=f"quiz:service:{key}"))
    markup.add(types.InlineKeyboardButton(t("btn_back_main", lang), callback_data="quiz:cancel"))
    return markup


def get_description_step_keyboard(lang: str = "ru") -> types.InlineKeyboardMarkup:
    """Step 1 cont.: Description / Reference skip & back buttons."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(t("btn_skip", lang), callback_data="quiz:skip_desc"),
        types.InlineKeyboardButton(t("btn_back", lang), callback_data="quiz:back:service"),
    )
    markup.add(
        types.InlineKeyboardButton(t("btn_cancel", lang), callback_data="quiz:cancel")
    )
    return markup


def get_options_keyboard(
    selected_options: list[str] | set[str],
    lang: str = "ru"
) -> types.InlineKeyboardMarkup:
    """Step 2: Interactive multi-toggle options keyboard with ✅ / ⬜."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    selected_set = set(selected_options)

    for key, opt in config.OPTIONS.items():
        checkbox = "✅" if key in selected_set else "⬜"
        price_tag = f"+${int(opt.price)}"
        button_text = f"{checkbox} {opt.get_name(lang)} ({price_tag})"
        markup.add(types.InlineKeyboardButton(button_text, callback_data=f"quiz:opt:{key}"))

    # Navigation buttons
    markup.add(
        types.InlineKeyboardButton(f"{t('btn_next', lang)} ➡️", callback_data="quiz:options_done")
    )
    markup.row(
        types.InlineKeyboardButton(t("btn_back", lang), callback_data="quiz:back:desc"),
        types.InlineKeyboardButton(t("btn_cancel", lang), callback_data="quiz:cancel"),
    )
    return markup


def get_budget_keyboard(calc_price: float, lang: str = "ru") -> types.InlineKeyboardMarkup:
    """Step 3: Budget tier selection keyboard."""
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Primary calculated option
    markup.add(
        types.InlineKeyboardButton(
            t("quiz_btn_calc_price", lang, total_price=int(calc_price)),
            callback_data="quiz:budget:calc"
        )
    )

    # Preset tiers
    markup.add(
        types.InlineKeyboardButton("< $100", callback_data="quiz:budget:tier_under_100"),
        types.InlineKeyboardButton("$100 – $300", callback_data="quiz:budget:tier_100_300"),
    )
    markup.add(
        types.InlineKeyboardButton("$300 – $600", callback_data="quiz:budget:tier_300_600"),
        types.InlineKeyboardButton("$600+", callback_data="quiz:budget:tier_600_plus"),
    )

    # Custom text entry
    markup.add(
        types.InlineKeyboardButton(t("quiz_btn_custom_budget", lang), callback_data="quiz:budget:custom")
    )

    # Navigation
    markup.row(
        types.InlineKeyboardButton(t("btn_back", lang), callback_data="quiz:back:options"),
        types.InlineKeyboardButton(t("btn_cancel", lang), callback_data="quiz:cancel"),
    )
    return markup


def get_contact_step_keyboard(
    has_tg_username: bool = False,
    username: str | None = None,
    lang: str = "ru"
) -> types.InlineKeyboardMarkup:
    """Step 4: Contact details entry keyboard."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    if has_tg_username and username:
        markup.add(
            types.InlineKeyboardButton(
                t("quiz_btn_use_tg", lang, username=f"@{username}"),
                callback_data="quiz:contact:use_tg"
            )
        )
    markup.row(
        types.InlineKeyboardButton(t("btn_back", lang), callback_data="quiz:back:budget"),
        types.InlineKeyboardButton(t("btn_cancel", lang), callback_data="quiz:cancel"),
    )
    return markup


def get_confirmation_keyboard(
    can_pay_deposit: bool = False,
    lang: str = "ru"
) -> types.InlineKeyboardMarkup:
    """Step 5: Final review and order confirmation keyboard."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(t("quiz_btn_confirm", lang), callback_data="quiz:confirm")
    )
    if can_pay_deposit:
        markup.add(
            types.InlineKeyboardButton(t("quiz_btn_deposit_menu", lang), callback_data="quiz:deposit_tiers")
        )
    markup.row(
        types.InlineKeyboardButton(t("btn_back", lang), callback_data="quiz:back:contact"),
        types.InlineKeyboardButton(t("btn_cancel", lang), callback_data="quiz:cancel"),
    )
    return markup


def get_deposit_tiers_keyboard(base_price: float, lang: str = "ru") -> types.InlineKeyboardMarkup:
    """Deposit percentage selection keyboard (30%, 50%, 100%)."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    for code, tier in config.DEPOSIT_TIERS.items():
        amount = int(base_price * tier["percent"])
        lbl = tier.get(f"label_{lang}", tier["label_ru"])
        markup.add(
            types.InlineKeyboardButton(f"{lbl} — ${amount}", callback_data=f"pay:deposit:{code}")
        )
    markup.add(types.InlineKeyboardButton(t("btn_back", lang), callback_data="quiz:back:confirm"))
    return markup


# --- ADMIN CONTROLS KEYBOARDS ---

def get_admin_dashboard_keyboard() -> types.InlineKeyboardMarkup:
    """Admin root menu."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📋 Все заявки", callback_data="admin:orders:all:0"),
        types.InlineKeyboardButton("🆕 Новые", callback_data="admin:orders:new:0"),
    )
    markup.add(
        types.InlineKeyboardButton("⚙️ В работе", callback_data="admin:orders:in_progress:0"),
        types.InlineKeyboardButton("🔍 На согласовании", callback_data="admin:orders:review:0"),
    )
    markup.add(
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin:stats"),
        types.InlineKeyboardButton("◀️ В главное меню", callback_data="menu:main"),
    )
    return markup


def get_admin_orders_list_keyboard(
    orders: list[dict],
    status_filter: str,
    offset: int,
    total_count: int,
    limit: int = 5
) -> types.InlineKeyboardMarkup:
    """Paginated list of orders with filter tabs."""
    markup = types.InlineKeyboardMarkup(row_width=1)

    for o in orders:
        status_name = database.ORDER_STATUSES.get(o["status"], o["status"])
        service = config.SERVICES.get(o["service_type"])
        srv_name = service.get_name("ru") if service else o["service_type"]
        price = int(o.get("estimated_price") or 0)
        btn_text = f"#{o['id']} | {srv_name} | ${price} | {status_name}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"admin:view_order:{o['id']}"))

    # Pagination row
    nav_row = []
    if offset > 0:
        prev_offset = max(0, offset - limit)
        nav_row.append(types.InlineKeyboardButton("◀️ Назад", callback_data=f"admin:orders:{status_filter}:{prev_offset}"))
    if offset + limit < total_count:
        next_offset = offset + limit
        nav_row.append(types.InlineKeyboardButton("Вперёд ▶️", callback_data=f"admin:orders:{status_filter}:{next_offset}"))
    if nav_row:
        markup.row(*nav_row)

    # Filter selector row
    markup.row(
        types.InlineKeyboardButton("Все", callback_data="admin:orders:all:0"),
        types.InlineKeyboardButton("Новые", callback_data="admin:orders:new:0"),
        types.InlineKeyboardButton("В работе", callback_data="admin:orders:in_progress:0"),
    )
    markup.add(types.InlineKeyboardButton("◀️ В админ-панель", callback_data="admin:menu"))
    return markup


def get_admin_order_card_keyboard(
    order_id: int,
    user_id: int,
    username: str | None = None
) -> types.InlineKeyboardMarkup:
    """Single order view actions for admin."""
    markup = types.InlineKeyboardMarkup(row_width=2)

    # 1. Direct message button
    if username:
        markup.add(types.InlineKeyboardButton("💬 Профиль в Telegram", url=f"https://t.me/{username}"))
    else:
        markup.add(types.InlineKeyboardButton("💬 Профиль в Telegram", url=f"tg://user?id={user_id}"))

    # 2. Bot messaging & status
    markup.add(
        types.InlineKeyboardButton("✍️ Ответить через бота", callback_data=f"admin:reply:{order_id}"),
        types.InlineKeyboardButton("🔄 Сменить статус", callback_data=f"admin:status_menu:{order_id}"),
    )
    markup.add(
        types.InlineKeyboardButton("💳 Статус оплаты", callback_data=f"admin:pay_menu:{order_id}"),
        types.InlineKeyboardButton("◀️ К списку заявок", callback_data="admin:orders:all:0"),
    )
    return markup


def get_admin_status_choice_keyboard(order_id: int) -> types.InlineKeyboardMarkup:
    """Admin status selection submenu."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    for code, label in database.ORDER_STATUSES.items():
        markup.add(types.InlineKeyboardButton(label, callback_data=f"admin:set_status:{order_id}:{code}"))
    markup.add(types.InlineKeyboardButton("◀️ Назад к карточке", callback_data=f"admin:view_order:{order_id}"))
    return markup


def get_admin_payment_status_keyboard(order_id: int) -> types.InlineKeyboardMarkup:
    """Admin payment status selector submenu."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    for code, label in database.PAYMENT_STATUSES.items():
        markup.add(types.InlineKeyboardButton(label, callback_data=f"admin:set_pay_status:{order_id}:{code}"))
    markup.add(types.InlineKeyboardButton("◀️ Назад к карточке", callback_data=f"admin:view_order:{order_id}"))
    return markup
