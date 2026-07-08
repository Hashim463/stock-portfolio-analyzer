"""
Database layer for the Portfolio Analyzer.
Uses SQLite (zero-setup) but the schema/queries are standard SQL,
so this ports directly to MySQL/PostgreSQL if you want to swap it in.
"""

import sqlite3
from contextlib import contextmanager

DB_PATH = "portfolio.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    quantity REAL NOT NULL,
    buy_price REAL NOT NULL,
    buy_date TEXT NOT NULL,
    UNIQUE(symbol, buy_date)
);

CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    close_price REAL NOT NULL,
    UNIQUE(symbol, date)
);
"""


@contextmanager
def get_conn(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str = DB_PATH):
    with get_conn(db_path) as conn:
        conn.executescript(SCHEMA)


def add_holding(symbol, company_name, sector, quantity, buy_price, buy_date, db_path: str = DB_PATH):
    with get_conn(db_path) as conn:
        conn.execute(
            """INSERT OR REPLACE INTO holdings
               (symbol, company_name, sector, quantity, buy_price, buy_date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (symbol, company_name, sector, quantity, buy_price, buy_date),
        )


def get_holdings(db_path: str = DB_PATH):
    with get_conn(db_path) as conn:
        rows = conn.execute("SELECT * FROM holdings ORDER BY symbol").fetchall()
        return [dict(r) for r in rows]


def save_price_history(symbol, price_series, db_path: str = DB_PATH):
    """price_series: list of (date_str, close_price) tuples."""
    with get_conn(db_path) as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO price_history (symbol, date, close_price) VALUES (?, ?, ?)",
            [(symbol, d, p) for d, p in price_series],
        )


def get_price_history(symbol, db_path: str = DB_PATH):
    with get_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT date, close_price FROM price_history WHERE symbol = ? ORDER BY date", (symbol,)
        ).fetchall()
        return [(r["date"], r["close_price"]) for r in rows]


def get_latest_price(symbol, db_path: str = DB_PATH):
    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT close_price FROM price_history WHERE symbol = ? ORDER BY date DESC LIMIT 1", (symbol,)
        ).fetchone()
        return row["close_price"] if row else None
