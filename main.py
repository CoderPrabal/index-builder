from fastapi import FastAPI
from app.api.index import router as index_router

app = FastAPI()
app.include_router(index_router)