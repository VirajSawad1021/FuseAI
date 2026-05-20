import asyncio
import time

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud
from ..database import AsyncSessionLocal
from ..logger import get_logger

router = APIRouter(tags=["counts"])
logger = get_logger(__name__)


async def _run_count(count_func) -> int:
    async with AsyncSessionLocal() as session:
        return await count_func(session)


@router.get("/customers/count")
async def customers_count() -> dict[str, int]:
    logger.info("Incoming request GET /customers/count")
    async with AsyncSessionLocal() as session:
        count = await crud.get_customers_count(session)
    logger.info("Completed GET /customers/count with status success")
    return {"count": count}


@router.get("/orders/count")
async def orders_count() -> dict[str, int]:
    logger.info("Incoming request GET /orders/count")
    async with AsyncSessionLocal() as session:
        count = await crud.get_orders_count(session)
    logger.info("Completed GET /orders/count with status success")
    return {"count": count}


@router.get("/products/count")
async def products_count() -> dict[str, int]:
    logger.info("Incoming request GET /products/count")
    async with AsyncSessionLocal() as session:
        count = await crud.get_products_count(session)
    logger.info("Completed GET /products/count with status success")
    return {"count": count}


@router.get("/employees/count")
async def employees_count() -> dict[str, int]:
    logger.info("Incoming request GET /employees/count")
    async with AsyncSessionLocal() as session:
        count = await crud.get_employees_count(session)
    logger.info("Completed GET /employees/count with status success")
    return {"count": count}


@router.get("/offices/count")
async def offices_count() -> dict[str, int]:
    logger.info("Incoming request GET /offices/count")
    async with AsyncSessionLocal() as session:
        count = await crud.get_offices_count(session)
    logger.info("Completed GET /offices/count with status success")
    return {"count": count}


@router.get("/payments/count")
async def payments_count() -> dict[str, int]:
    logger.info("Incoming request GET /payments/count")
    async with AsyncSessionLocal() as session:
        count = await crud.get_payments_count(session)
    logger.info("Completed GET /payments/count with status success")
    return {"count": count}


@router.get("/orderdetails/count")
async def orderdetails_count() -> dict[str, int]:
    logger.info("Incoming request GET /orderdetails/count")
    async with AsyncSessionLocal() as session:
        count = await crud.get_orderdetails_count(session)
    logger.info("Completed GET /orderdetails/count with status success")
    return {"count": count}


@router.get("/productlines/count")
async def productlines_count() -> dict[str, int]:
    logger.info("Incoming request GET /productlines/count")
    async with AsyncSessionLocal() as session:
        count = await crud.get_productlines_count(session)
    logger.info("Completed GET /productlines/count with status success")
    return {"count": count}


@router.get("/overall_counts")
async def overall_counts() -> dict[str, int]:
    logger.info("Incoming request GET /overall_counts")
    start_time = time.perf_counter()
    tasks = [
        _run_count(crud.get_customers_count),
        _run_count(crud.get_orders_count),
        _run_count(crud.get_products_count),
        _run_count(crud.get_employees_count),
        _run_count(crud.get_offices_count),
        _run_count(crud.get_payments_count),
        _run_count(crud.get_orderdetails_count),
        _run_count(crud.get_productlines_count),
    ]
    logger.info("Starting asyncio.gather for overall_counts")
    counts = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - start_time
    logger.info("asyncio.gather completed for overall_counts in %.4fs", elapsed)
    response = {
        "customers": counts[0],
        "orders": counts[1],
        "products": counts[2],
        "employees": counts[3],
        "offices": counts[4],
        "payments": counts[5],
        "orderdetails": counts[6],
        "productlines": counts[7],
    }
    logger.info("Completed GET /overall_counts with status success")
    return response
