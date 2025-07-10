from pydantic import BaseModel
from datetime import date
from typing import List


class StockBase(BaseModel):
    symbol: str
    name: str
    sector: str


class DailyPrice(BaseModel):
    symbol: str
    date: date
    close_price: float
    market_cap: float


class IndexEntry(BaseModel):
    date: date
    symbol: str
    weight: float


class IndexValue(BaseModel):
    date: date
    index_value: float


class IndexResponse(BaseModel):
    date: date
    index_value: float
    constituents: List[IndexEntry]
