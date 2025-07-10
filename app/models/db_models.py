import os
import duckdb

DB_PATH = "data/market_data.duckdb"


def create_tables():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = duckdb.connect(DB_PATH)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        symbol TEXT PRIMARY KEY,
        name TEXT,
        sector TEXT
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS daily_prices (
        symbol TEXT,
        date DATE,
        close_price DOUBLE,
        market_cap DOUBLE,
        PRIMARY KEY (symbol, date)
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS index_compositions (
        date DATE,
        symbol TEXT,
        weight DOUBLE,
        PRIMARY KEY (date, symbol)
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS index_values (
        date DATE PRIMARY KEY,
        index_value DOUBLE
    );
    """)

    conn.close()
