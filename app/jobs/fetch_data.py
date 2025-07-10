import yfinance as yf
import pandas as pd
from app.utils.db import get_connection, init_db
from datetime import datetime

TOP_STOCKS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "BRK-B", "UNH", "JNJ",
    "V", "XOM", "PG", "JPM", "LLY", "MA", "HD", "CVX", "ABBV", "AVGO",  # 20 of top 100
    # Add more if needed
]

def fetch_market_data(symbols, period="35d"):
    all_data = []

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            info = ticker.info
            market_cap = info.get("marketCap", 0)

            for date, row in hist.iterrows():
                all_data.append({
                    "symbol": symbol,
                    "date": date.date(),
                    "close_price": row["Close"],
                    "market_cap": market_cap
                })
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    return pd.DataFrame(all_data)

def load_into_duckdb(df):
    conn = get_connection()

    if df.empty:
        print("⚠️ No data to insert.")
        return

    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df[["symbol", "date", "close_price", "market_cap"]]
    df = df.drop_duplicates(subset=["symbol", "date"])  # ✅ Prevent same-day duplicates

    conn.register("temp_df", df)

    conn.execute("""
        INSERT OR REPLACE INTO daily_prices
        SELECT symbol, date, close_price, market_cap FROM temp_df
    """)

    conn.unregister("temp_df")
    conn.close()
    print(f"✅ Inserted {len(df)} rows into daily_prices.")


if __name__ == "__main__":
    init_db()
    df = fetch_market_data(TOP_STOCKS, period="35d")
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.drop_duplicates(subset=["symbol", "date"])
    print(df.head())  # Check content
    print(df.dtypes)
    load_into_duckdb(df)
    print("✅ Data saved to DuckDB.")
