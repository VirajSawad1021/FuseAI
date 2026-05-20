from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud
from ..database import get_db
from ..logger import get_logger
from ..schemas import CustomerCreate, CustomerOut, CustomerSummary, CustomerUpdate, OrderRead, PaymentRead

router = APIRouter(prefix="/customers", tags=["customers"])
logger = get_logger(__name__)


@router.get("", response_model=list[CustomerSummary])
async def list_customers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> list[CustomerSummary]:
    logger.info("Incoming request GET /customers skip=%s limit=%s", skip, limit)
    customers = await crud.get_customers(session, skip=skip, limit=limit)
    logger.info("Completed GET /customers with %s records", len(customers))
    return customers


@router.get("/{customer_number}", response_model=CustomerOut)
async def get_customer(customer_number: int, session: AsyncSession = Depends(get_db)) -> CustomerOut:
    logger.info("Incoming request GET /customers/%s", customer_number)
    customer = await crud.get_customer(session, customer_number)
    if customer is None:
        logger.warning("GET /customers/%s returned 404", customer_number)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    logger.info("Completed GET /customers/%s successfully", customer_number)
    return customer


@router.get("/{customer_number}/orders", response_model=list[OrderRead])
async def get_customer_orders(
    customer_number: int, session: AsyncSession = Depends(get_db)
) -> list[OrderRead]:
    logger.info("Incoming request GET /customers/%s/orders", customer_number)
    orders = await crud.get_customer_orders(session, customer_number)
    logger.info("Completed GET /customers/%s/orders with %s records", customer_number, len(orders))
    return orders


@router.get("/{customer_number}/payments", response_model=list[PaymentRead])
async def get_customer_payments(
    customer_number: int, session: AsyncSession = Depends(get_db)
) -> list[PaymentRead]:
    logger.info("Incoming request GET /customers/%s/payments", customer_number)
    payments = await crud.get_customer_payments(session, customer_number)
    logger.info("Completed GET /customers/%s/payments with %s records", customer_number, len(payments))
    return payments


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_in: CustomerCreate, session: AsyncSession = Depends(get_db)
) -> CustomerOut:
    logger.info("Incoming request POST /customers")
    customer = await crud.create_customer(session, customer_in)
    logger.info("Completed POST /customers successfully")
    return customer


@router.put("/{customer_number}", response_model=CustomerOut)
async def update_customer(
    customer_number: int,
    customer_in: CustomerUpdate,
    session: AsyncSession = Depends(get_db),
) -> CustomerOut:
    logger.info("Incoming request PUT /customers/%s", customer_number)
    customer = await crud.update_customer(session, customer_number, customer_in)
    if customer is None:
        logger.warning("PUT /customers/%s returned 404", customer_number)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    logger.info("Completed PUT /customers/%s successfully", customer_number)
    return customer


@router.delete("/{customer_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_number: int, session: AsyncSession = Depends(get_db)) -> None:
    logger.info("Incoming request DELETE /customers/%s", customer_number)
    deleted = await crud.delete_customer(session, customer_number)
    if not deleted:
        logger.warning("DELETE /customers/%s returned 404", customer_number)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    logger.info("Completed DELETE /customers/%s successfully", customer_number)
