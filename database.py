"""Database management module using SQLite.

Implements persistent storage for users, orders, and payments with clean schema design,
indexing, connection pooling context manager, and migration-ready structures for PostgreSQL.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator

import config

logger = logging.getLogger(__name__)

# Canonical order statuses mapping internal code to display labels
ORDER_STATUSES = {
    "new": "Новая",
    "evaluating": "На оценке",
    "in_progress": "В работе",
    "review": "На согласовании",
    "completed": "Завершена",
    "cancelled": "Отменена",
}

PAYMENT_STATUSES = {
    "unpaid": "Не оплачено",
    "deposit_paid": "Депозит внесен",
    "fully_paid": "Оплачено полностью",
}


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite database connection.

    Yields:
        sqlite3.Connection: Database connection with row_factory set to sqlite3.Row.
    """
    conn = sqlite3.connect(config.DB_PATH, timeout=15.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction error: {e}", exc_info=True)
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database tables, columns, and indices."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Users table (id matches Telegram user_id)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                language TEXT DEFAULT 'ru'
            );
        """)

        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                service_type TEXT NOT NULL,
                details TEXT,
                options TEXT,
                budget TEXT,
                estimated_price REAL DEFAULT 0.0,
                estimated_days TEXT,
                contact_info TEXT,
                status TEXT DEFAULT 'new',
                payment_status TEXT DEFAULT 'unpaid',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)

        # Payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_id INTEGER,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                telegram_payment_charge_id TEXT,
                provider_payment_charge_id TEXT,
                payload TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (order_id) REFERENCES orders (id)
            );
        """)

        # Indices for optimal query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders (user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders (created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments (order_id);")

    logger.info("Database schema initialized and verified.")


def get_or_create_user(
    user_id: int,
    username: str | None = None,
    full_name: str | None = None,
    default_lang: str = "ru"
) -> dict[str, Any]:
    """Retrieve existing user or register a new user in database.

    Args:
        user_id: Telegram user ID.
        username: Telegram username.
        full_name: User display full name.
        default_lang: Language code for new users.

    Returns:
        dict[str, Any]: User record dictionary.
    """
    now = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE users
                SET username = ?, full_name = ?, last_seen = ?
                WHERE id = ?
            """, (username, full_name, now, user_id))
            return dict(row)

        cursor.execute("""
            INSERT INTO users (id, username, full_name, first_seen, last_seen, language)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, full_name, now, now, default_lang))

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        new_row = cursor.fetchone()
        return dict(new_row) if new_row else {}


def update_user_last_seen(user_id: int) -> None:
    """Update last active timestamp for user."""
    now = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_seen = ? WHERE id = ?", (now, user_id))


def get_user_language(user_id: int) -> str:
    """Get preferred language for user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row and row["language"]:
            return row["language"]
    return config.DEFAULT_LANGUAGE


def set_user_language(user_id: int, language: str) -> None:
    """Save preferred language for user."""
    now = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (id, first_seen, last_seen, language)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                language = excluded.language,
                last_seen = excluded.last_seen
        """, (user_id, now, now, language))


def create_order(
    user_id: int,
    service_type: str,
    details: str,
    options: list[str],
    budget: str,
    estimated_price: float,
    estimated_days: str,
    contact_info: str
) -> int:
    """Create a new order in SQLite.

    Returns:
        int: Unique order ID.
    """
    now = datetime.now().isoformat()
    options_json = json.dumps(options, ensure_ascii=False)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (
                user_id, service_type, details, options, budget,
                estimated_price, estimated_days, contact_info,
                status, payment_status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new', 'unpaid', ?, ?)
        """, (
            user_id, service_type, details, options_json, budget,
            estimated_price, estimated_days, contact_info, now, now
        ))
        return int(cursor.lastrowid)


def get_order(order_id: int) -> dict[str, Any] | None:
    """Fetch order by ID with decoded options.

    Returns:
        dict or None: Order record.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, u.username, u.full_name, u.language
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            WHERE o.id = ?
        """, (order_id,))
        row = cursor.fetchone()
        if not row:
            return None
        data = dict(row)
        try:
            data["options"] = json.loads(data["options"]) if data["options"] else []
        except Exception:
            data["options"] = []
        return data


def update_order_status(order_id: int, status: str) -> bool:
    """Update order status.

    Args:
        order_id: Order ID.
        status: Internal status code ('new', 'evaluating', 'in_progress', 'review', 'completed', 'cancelled').

    Returns:
        bool: True if updated.
    """
    now = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status, now, order_id))
        return cursor.rowcount > 0


def update_order_payment_status(order_id: int, payment_status: str) -> bool:
    """Update order payment status ('unpaid', 'deposit_paid', 'fully_paid')."""
    now = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders
            SET payment_status = ?, updated_at = ?
            WHERE id = ?
        """, (payment_status, now, order_id))
        return cursor.rowcount > 0


def get_orders(
    status_filter: str | None = None,
    limit: int = 5,
    offset: int = 0
) -> list[dict[str, Any]]:
    """Retrieve paginated orders, optionally filtered by status.

    Returns:
        list of order records.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if status_filter and status_filter != "all":
            cursor.execute("""
                SELECT o.*, u.username, u.full_name
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                WHERE o.status = ?
                ORDER BY o.id DESC
                LIMIT ? OFFSET ?
            """, (status_filter, limit, offset))
        else:
            cursor.execute("""
                SELECT o.*, u.username, u.full_name
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                ORDER BY o.id DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            try:
                d["options"] = json.loads(d["options"]) if d["options"] else []
            except Exception:
                d["options"] = []
            result.append(d)
        return result


def count_orders(status_filter: str | None = None) -> int:
    """Count total orders, optionally filtered by status."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if status_filter and status_filter != "all":
            cursor.execute("SELECT COUNT(*) FROM orders WHERE status = ?", (status_filter,))
        else:
            cursor.execute("SELECT COUNT(*) FROM orders")
        return int(cursor.fetchone()[0])


def add_payment(
    user_id: int,
    amount: float,
    currency: str,
    order_id: int | None = None,
    telegram_payment_charge_id: str | None = None,
    provider_payment_charge_id: str | None = None,
    payload: str | None = None
) -> int:
    """Record payment in database."""
    now = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO payments (
                user_id, order_id, amount, currency,
                telegram_payment_charge_id, provider_payment_charge_id, payload, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, order_id, amount, currency,
            telegram_payment_charge_id, provider_payment_charge_id, payload, now
        ))
        payment_id = cursor.lastrowid

        # Update order payment status if linked
        if order_id:
            cursor.execute("UPDATE orders SET payment_status = 'deposit_paid' WHERE id = ?", (order_id,))

        return int(payment_id)


def get_admin_stats() -> dict[str, Any]:
    """Retrieve full admin metrics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'new'")
        new_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'in_progress'")
        in_progress_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'completed'")
        completed_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM payments")
        total_revenue = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(estimated_price), 0) FROM orders")
        total_order_volume = cursor.fetchone()[0]

        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "new_orders": new_orders,
            "in_progress_orders": in_progress_orders,
            "completed_orders": completed_orders,
            "total_revenue": total_revenue,
            "total_order_volume": total_order_volume,
        }
