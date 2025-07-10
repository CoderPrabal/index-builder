import os

import duckdb

from app.models.db_models import create_tables

DB_PATH = os.getenv("DB_PATH", "data/market_data.duckdb")


def get_connection():
    return duckdb.connect(DB_PATH)


def init_db():
    create_tables()
