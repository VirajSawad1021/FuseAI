from __future__ import annotations

import time
from typing import Callable, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .logger import get_logger
from .models import Customer, Employee, Office, Order, OrderDetail, Payment, Product, ProductLine
from .schemas import CustomerCreate, CustomerUpdate

logger = get_logger(__name__)
T = TypeVar("T")


async def _count_rows(session: AsyncSession, model: type, label: str) -> int:
    start_time = time.perf_counter()
    logger.info("Starting count query for %s", label)
    try:
        result = await session.scalar(select(func.count()).select_from(model))
        count = int(result or 0)
        elapsed = time.perf_counter() - start_time
        logger.info("Completed count query for %s in %.4fs", label, elapsed)
        return count
    except Exception:
        logger.exception("Count query failed for %s", label)
        raise


async def get_customers_count(session: AsyncSession) -> int:
    return await _count_rows(session, Customer, "customers")


async def get_orders_count(session: AsyncSession) -> int:
    return await _count_rows(session, Order, "orders")


async def get_products_count(session: AsyncSession) -> int:
    return await _count_rows(session, Product, "products")


async def get_employees_count(session: AsyncSession) -> int:
    return await _count_rows(session, Employee, "employees")


async def get_offices_count(session: AsyncSession) -> int:
    return await _count_rows(session, Office, "offices")


async def get_payments_count(session: AsyncSession) -> int:
    return await _count_rows(session, Payment, "payments")


async def get_orderdetails_count(session: AsyncSession) -> int:
    return await _count_rows(session, OrderDetail, "orderdetails")


async def get_productlines_count(session: AsyncSession) -> int:
    return await _count_rows(session, ProductLine, "productlines")


async def get_customers(session: AsyncSession, skip: int = 0, limit: int = 10) -> list[Customer]:
    logger.info("Reading customers with skip=%s limit=%s", skip, limit)
    result = await session.scalars(
        select(Customer).order_by(Customer.customer_number).offset(skip).limit(limit)
    )
    customers = list(result.all())
    logger.info("Loaded %s customers", len(customers))
    return customers


async def get_customer(session: AsyncSession, customer_number: int) -> Customer | None:
    logger.info("Reading customer %s", customer_number)
    statement = (
        select(Customer)
        .options(selectinload(Customer.orders), selectinload(Customer.payments))
        .where(Customer.customer_number == customer_number)
    )
    result = await session.scalars(statement)
    customer = result.unique().one_or_none()
    if customer is None:
        logger.warning("Customer not found: %s", customer_number)
    return customer


async def get_customer_orders(session: AsyncSession, customer_number: int) -> list[Order]:
    logger.info("Reading orders for customer %s", customer_number)
    result = await session.scalars(
        select(Order).where(Order.customer_number == customer_number).order_by(Order.order_number)
    )
    orders = list(result.all())
    logger.info("Loaded %s orders for customer %s", len(orders), customer_number)
    return orders


async def get_customer_payments(session: AsyncSession, customer_number: int) -> list[Payment]:
    logger.info("Reading payments for customer %s", customer_number)
    result = await session.scalars(
        select(Payment)
        .where(Payment.customer_number == customer_number)
        .order_by(Payment.payment_date.desc())
    )
    payments = list(result.all())
    logger.info("Loaded %s payments for customer %s", len(payments), customer_number)
    return payments


async def create_customer(session: AsyncSession, customer_in: CustomerCreate) -> Customer:
    logger.info("Creating customer %s", customer_in.customer_name)
    data = customer_in.model_dump(exclude_unset=True)
    if data.get("customer_number") is None:
        next_number = await session.scalar(select(func.max(Customer.customer_number)))
        data["customer_number"] = int(next_number or 0) + 1

    customer = Customer(**data)
    session.add(customer)
    await session.flush()
    await session.refresh(customer)
    logger.info("Created customer %s", customer.customer_number)
    return (await get_customer(session, customer.customer_number)) or customer


async def update_customer(
    session: AsyncSession, customer_number: int, customer_in: CustomerUpdate
) -> Customer | None:
    logger.info("Updating customer %s", customer_number)
    customer = await get_customer(session, customer_number)
    if customer is None:
        return None

    update_data = customer_in.model_dump(exclude_unset=True)
    for field_name, value in update_data.items():
        if value is not None:
            setattr(customer, field_name, value)

    await session.flush()
    await session.refresh(customer)
    logger.info("Updated customer %s", customer_number)
    return (await get_customer(session, customer_number)) or customer


async def delete_customer(session: AsyncSession, customer_number: int) -> bool:
    logger.info("Deleting customer %s", customer_number)
    customer = await get_customer(session, customer_number)
    if customer is None:
        return False

    await session.delete(customer)
    await session.flush()
    logger.info("Deleted customer %s", customer_number)
    return True
