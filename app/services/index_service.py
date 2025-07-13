import json
from datetime import date, timedelta

import pandas as pd
import redis

from app.redis_cache import cache_get, cache_set
from app.redis_cache import r
from app.utils.db import get_connection

#r = redis.Redis(host="localhost", port=6379, db=0)


def construct_index(target_date: date):
    conn = get_connection()

    # Get top 100 by market cap
    query = f"""
    SELECT symbol, market_cap
    FROM daily_prices
    WHERE date = '{target_date}'
    ORDER BY market_cap DESC
    LIMIT 100;
    """
    top_100 = conn.execute(query).fetchdf()
    if top_100.empty:
        return {"error": f"No data available for {target_date}"}

    top_100["weight"] = 1.0 / 100

    conn.execute("DELETE FROM index_compositions WHERE date = ?", [target_date])
    for _, row in top_100.iterrows():
        conn.execute(
            "INSERT INTO index_compositions (date, symbol, weight) VALUES (?, ?, ?)",
            (target_date, row["symbol"], row["weight"])
        )

    # Today's and previous day's close prices
    prev_date = target_date - timedelta(days=1)
    today_prices = conn.execute(
        f"""SELECT symbol, close_price FROM daily_prices
            WHERE date = '{target_date}' AND symbol IN ({','.join(['?'] * len(top_100))})
        """, list(top_100["symbol"])
    ).fetchdf()

    prev_prices = conn.execute(
        f"""SELECT symbol, close_price FROM daily_prices
            WHERE date = '{prev_date}' AND symbol IN ({','.join(['?'] * len(top_100))})
        """, list(top_100["symbol"])
    ).fetchdf()

    merged = pd.merge(today_prices, prev_prices, on="symbol", suffixes=("_today", "_prev"))
    if merged.empty:
        return {"error": f"No return data available for {target_date}"}

    merged["return"] = merged["close_price_today"] / merged["close_price_prev"] - 1
    daily_return = merged["return"].mean()

    prev_cum_row = conn.execute(
        "SELECT cumulative_return FROM index_performance WHERE date = ?", [prev_date]
    ).fetchone()
    prev_cum = prev_cum_row[0] if prev_cum_row else 0

    cum_return = (1 + prev_cum) * (1 + daily_return) - 1

    # Save performance
    conn.execute(
        "INSERT OR REPLACE INTO index_performance VALUES (?, ?, ?)",
        (target_date, daily_return, cum_return)
    )

    # Save index value starting from 100
    prev_val_row = conn.execute(
        "SELECT index_value FROM index_values WHERE date = ?", [prev_date]
    ).fetchone()
    prev_index_value = prev_val_row[0] if prev_val_row else 100
    index_value = prev_index_value * (1 + daily_return)

    conn.execute("DELETE FROM index_values WHERE date = ?", [target_date])
    conn.execute("INSERT INTO index_values VALUES (?, ?)", [target_date, index_value])
    conn.close()
    '''
    # Cache
    r.set(f"performance:{target_date}", json.dumps({
        "date": str(target_date),
        "daily_return": daily_return,
        "cumulative_return": cum_return
    }), ex=86400)

    r.set(f"composition:{target_date}",
          top_100[["symbol", "weight"]].to_json(orient="records"), ex=86400)
    '''

    return {
        "date": str(target_date),
        "index_value": round(index_value, 2),
        "daily_return": round(daily_return, 6),
        "cumulative_return": round(cum_return, 6),
        "constituents": top_100.to_dict(orient="records")
    }


def build_equal_weight_index(start_date: date, end_date: date = None):
    end_date = end_date or start_date
    dates = pd.date_range(start=start_date, end=end_date).date

    summary = []
    for d in dates:
        result = construct_index(d)
        if "error" not in result:
            summary.append({
                "date": d,
                "index_value": result["index_value"],
                "daily_return": result["daily_return"],
                "cumulative_return": result["cumulative_return"]
            })

    return {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "days_processed": len(summary),
        "results": summary
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
    #cache_key = f"composition:{target_date}"
    #cached = cache_get(cache_key)
    #if cached:
        #return cached
    conn = get_connection()
    df = conn.execute("""
        SELECT * FROM index_compositions
        WHERE date = ?
        ORDER BY symbol
    """, [target_date]).fetchdf()
    result = df.to_dict(orient="records")
    #cache_set(cache_key, result)
    conn.close()
    return result


def get_composition_changes(start: date, end: date):
    #cache_key = f"composition_changes:{start}:{end}"
    #cached = cache_get(cache_key)
    #if cached:
        #return cached
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
    #cache_set(cache_key, changes)
    return changes


def get_index_performance(start_date, end_date):
    query_dates = f"""
    SELECT date
    FROM index_performance
    WHERE date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY date
    """
    conn = get_connection()
    dates = conn.execute(query_dates).fetchdf()["date"]
    results = []

    for d in dates:
        #cache_key = f"performance:{d}"
        #cached = cache_get(cache_key)
        #if cached:
            #results.append(cached)
        row = conn.execute(
            f"""
            SELECT date, daily_return, cumulative_return
            FROM index_performance
            WHERE date = '{d}'
            """
        ).fetchdf()
        if not row.empty:
            data = row.iloc[0].to_dict()
           # cache_set(cache_key, data)
            results.append(data)

    conn.close()
    return results
