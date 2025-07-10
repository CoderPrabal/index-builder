from app.utils.db import init_db
from app.services.index_service import construct_index
from datetime import date

if __name__ == "__main__":
    # Ensure DB tables exist
    init_db()

    # Pick any date for which you have data
    target_date = date(2025, 7, 1)

    # Call the index construction logic
    success = construct_index(target_date)

    if success:
        print(f"✅ Index successfully constructed for {target_date}")
    else:
        print(f"❌ Failed to construct index for {target_date} (no data?)")
