from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class OrderDetailRead(ORMModel):
    order_number: int
    product_code: str
    quantity_ordered: int
    price_each: Decimal
    order_line_number: int


class OrderRead(ORMModel):
    order_number: int
    order_date: date
    required_date: date
    shipped_date: date | None = None
    status: str
    comments: str | None = None
    customer_number: int


class PaymentRead(ORMModel):
    customer_number: int
    check_number: str
    payment_date: date
    amount: Decimal


class CustomerSummary(ORMModel):
    customer_number: int
    customer_name: str
    contact_last_name: str
    contact_first_name: str
    phone: str
    city: str
    country: str
    credit_limit: Decimal | None = None


class CustomerOut(CustomerSummary):
    address_line_1: str
    address_line_2: str | None = None
    state: str | None = None
    postal_code: str | None = None
    sales_rep_employee_number: int | None = None
    orders: list[OrderRead] = Field(default_factory=list)
    payments: list[PaymentRead] = Field(default_factory=list)


class CustomerCreate(BaseModel):
    customer_number: int | None = None
    customer_name: str
    contact_last_name: str
    contact_first_name: str
    phone: str
    address_line_1: str
    address_line_2: str | None = None
    city: str
    state: str | None = None
    postal_code: str | None = None
    country: str
    sales_rep_employee_number: int | None = None
    credit_limit: Decimal | None = None


class CustomerUpdate(BaseModel):
    customer_name: str | None = None
    contact_last_name: str | None = None
    contact_first_name: str | None = None
    phone: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    sales_rep_employee_number: int | None = None
    credit_limit: Decimal | None = None
