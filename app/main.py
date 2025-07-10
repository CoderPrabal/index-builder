from fastapi import FastAPI

from app.api.routes import router
from app.utils.db import init_db

app = FastAPI(title="Custom Equal-Weighted Stock Index API")


# Initialize DB tables on startup
@app.on_event("startup")
def startup_event():
    init_db()


# Include API routes
app.include_router(router)
