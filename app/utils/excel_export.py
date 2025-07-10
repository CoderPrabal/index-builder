from datetime import date

import pandas as pd
from fastapi.responses import FileResponse

from app.utils.db import get_connection


def export_index_excel(target_date: date):
    conn = get_connection()

    df_comp = conn.execute("""
        SELECT * FROM index_compositions
        WHERE date = ?
    """, [target_date]).fetchdf()

    df_val = conn.execute("""
        SELECT * FROM index_values
        WHERE date = ?
    """, [target_date]).fetchdf()

    conn.close()

    if df_comp.empty or df_val.empty:
        return {"error": f"No index data for {target_date}"}

    filename = f"index_{target_date}.xlsx"
    filepath = f"/tmp/{filename}"

    with pd.ExcelWriter(filepath) as writer:
        df_val.to_excel(writer, sheet_name="Index Value", index=False)
        df_comp.to_excel(writer, sheet_name="Composition", index=False)

    return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=filename)
