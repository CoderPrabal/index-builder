import duckdb

DB_PATH = "data/market_data.duckdb"

def test_insert():
    try:
        conn = duckdb.connect(DB_PATH)
        # ✅ Fetch the inserted row
        result = conn.execute("SELECT * FROM daily_prices WHERE symbol = 'AAPL''").fetchdf()
        print("✅ Insert successful. Result:")
        print(result)

        conn.close()

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    test_insert()
