from datetime import date, timedelta

from fastapi import APIRouter, Query

from app.services.index_service import (
    construct_index,
    get_index_range,
    get_composition,
    get_composition_changes,
)
from app.utils.excel_export import export_index_excel

router = APIRouter()


@router.post("/build-index")
def build_index(date: date = Query(...)):
    return construct_index(date)


@router.post("/build-index-range")
def build_index_range(start: date, end: date):
    result = []
    current = start
    while current <= end:
        result.append(construct_index(current))
        current += timedelta(days=1)
    return result


@router.get("/index")
def get_index(date: date = Query(...)):
    return construct_index(date)


@router.get("/index-performance")
def index_range(start: date, end: date):
    return get_index_range(start, end)


@router.get("/index-composition")
def index_composition(date: date):
    return get_composition(date)


@router.get("/composition-changes")
def composition_changes(start: date, end: date):
    return get_composition_changes(start, end)


@router.get("/export/index")
def export(date: date):
    return export_index_excel(date)
