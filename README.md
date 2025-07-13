IndexBuilder is a backend service that dynamically builds and tracks a custom equal-weighted stock index consisting of the top 100 US stocks by daily market capitalization.

Built using FastAPI, DuckDB, Redis, and Docker, this project demonstrates:

Financial modeling of equal-weight indices

API-driven index construction

Historical tracking and composition change detection

Excel export support

🚀 Features
✅ Dynamic Index Construction
Build an equal-weighted index for any date or date range using market cap data.

📈 Daily & Cumulative Returns
Track performance over time with proper equal-weight logic.

📦 Composition Storage & Change Detection
See which stocks entered or exited the index over time.

⚡ Fast Redis Caching
Cached index compositions and returns for fast access.

📄 Excel Export Support
Export index data and composition changes as .xlsx.

🧱 Tech Stack
Layer	Tech
Language	Python 3.10+
Web Framework	FastAPI
Database	DuckDB / SQLite
Caching	Redis
Containerization	Docker
Excel Export	Pandas + openpyxl

🙋 Author
Built with 💻 by Prabal Kumar
