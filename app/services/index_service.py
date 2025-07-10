import pandas as pd
from datetime import date
from app.utils.db import get_connection

def construct_index(target_date: date):
    conn = get_connection()

    # Get top 100 stocks by market cap for the given date
    query = f"""
    SELECT symbol, market_cap
    FROM daily_prices
    WHERE date = '{target_date}'
    ORDER BY market_cap DESC
    LIMIT 100;
    """
    top_100 = conn.execute(query).fetchdf()

    if top_100.empty:
        return {"error": f"No data found for {target_date}"}

    top_100["weight"] = 1.0 / len(top_100)

    # Insert into index_compositions
    conn.execute("DELETE FROM index_compositions WHERE date = ?", [target_date])
    conn.execute("INSERT INTO index_compositions SELECT ?, symbol, weight FROM top_100", [target_date])

    # Compute index value as average close price
    close_prices = conn.execute(f"""
        SELECT symbol, close_price FROM daily_prices
        WHERE date = '{target_date}' AND symbol IN ({','.join(['?']*len(top_100))})
    """, list(top_100["symbol"])).fetchdf()

    index_value = close_prices["close_price"].mean()

    # Store index value
    conn.execute("DELETE FROM index_values WHERE date = ?", [target_date])
    conn.execute("INSERT INTO index_values VALUES (?, ?)", [target_date, index_value])

    conn.close()

    return {
        "date": target_date,
        "index_value": round(index_value, 2),
        "constituents": top_100.to_dict(orient="records")
    }


def get_index_range(start: date, end: date):
    conn = get_connection()
    result = conn.execute("""
        SELECT * FROM index_values
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """, [start, end]).fetchdf()
    conn.close()

    return result.to_dict(orient="records")


def get_composition(target_date: date):
    conn = get_connection()
    df = conn.execute("""
        SELECT * FROM index_compositions
        WHERE date = ?
        ORDER BY symbol
    """, [target_date]).fetchdf()
    conn.close()
    return df.to_dict(orient="records")


def get_composition_changes(start: date, end: date):
    conn = get_connection()

    df = conn.execute("""
        SELECT date, symbol
        FROM index_compositions
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """, [start, end]).fetchdf()

    changes = []
    prev = set()

    for day in sorted(df["date"].unique()):
        current = set(df[df["date"] == day]["symbol"])
        added = list(current - prev)
        removed = list(prev - current)
        if added or removed:
            changes.append({
                "date": day,
                "added": added,
                "removed": removed
            })
        prev = current

    conn.close()
    return changes