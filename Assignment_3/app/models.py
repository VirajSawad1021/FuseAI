from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import LargeBinary, SmallInteger

from .database import Base


class ProductLine(Base):
    __tablename__ = "productlines"

    product_line: Mapped[str] = mapped_column("productLine", String(50), primary_key=True)
    text_description: Mapped[Optional[str]] = mapped_column(
        "textDescription", String(4000), nullable=True
    )
    html_description: Mapped[Optional[str]] = mapped_column("htmlDescription", Text, nullable=True)
    image: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)

    products: Mapped[list["Product"]] = relationship(back_populates="product_line_ref")


class Product(Base):
    __tablename__ = "products"

    product_code: Mapped[str] = mapped_column("productCode", String(15), primary_key=True)
    product_name: Mapped[str] = mapped_column("productName", String(70), nullable=False)
    product_line: Mapped[str] = mapped_column(
        "productLine", ForeignKey("productlines.productLine"), nullable=False
    )
    product_scale: Mapped[str] = mapped_column("productScale", String(10), nullable=False)
    product_vendor: Mapped[str] = mapped_column("productVendor", String(50), nullable=False)
    product_description: Mapped[str] = mapped_column("productDescription", Text, nullable=False)
    quantity_in_stock: Mapped[int] = mapped_column("quantityInStock", Integer, nullable=False)
    buy_price: Mapped[Decimal] = mapped_column("buyPrice", Numeric(10, 2), nullable=False)
    msrp: Mapped[Decimal] = mapped_column("MSRP", Numeric(10, 2), nullable=False)

    product_line_ref: Mapped["ProductLine"] = relationship(back_populates="products")
    order_details: Mapped[list["OrderDetail"]] = relationship(back_populates="product")


class Office(Base):
    __tablename__ = "offices"

    office_code: Mapped[str] = mapped_column("officeCode", String(10), primary_key=True)
    city: Mapped[str] = mapped_column("city", String(50), nullable=False)
    phone: Mapped[str] = mapped_column("phone", String(50), nullable=False)
    address_line_1: Mapped[str] = mapped_column("addressLine1", String(50), nullable=False)
    address_line_2: Mapped[Optional[str]] = mapped_column("addressLine2", String(50), nullable=True)
    state: Mapped[Optional[str]] = mapped_column("state", String(50), nullable=True)
    country: Mapped[str] = mapped_column("country", String(50), nullable=False)
    postal_code: Mapped[str] = mapped_column("postalCode", String(15), nullable=False)
    territory: Mapped[str] = mapped_column("territory", String(10), nullable=False)

    employees: Mapped[list["Employee"]] = relationship(back_populates="office")


class Employee(Base):
    __tablename__ = "employees"

    employee_number: Mapped[int] = mapped_column("employeeNumber", Integer, primary_key=True)
    last_name: Mapped[str] = mapped_column("lastName", String(50), nullable=False)
    first_name: Mapped[str] = mapped_column("firstName", String(50), nullable=False)
    extension: Mapped[str] = mapped_column("extension", String(10), nullable=False)
    email: Mapped[str] = mapped_column("email", String(100), nullable=False)
    office_code: Mapped[str] = mapped_column(
        "officeCode", ForeignKey("offices.officeCode"), nullable=False
    )
    reports_to: Mapped[Optional[int]] = mapped_column(
        "reportsTo", ForeignKey("employees.employeeNumber"), nullable=True
    )
    job_title: Mapped[str] = mapped_column("jobTitle", String(50), nullable=False)

    office: Mapped["Office"] = relationship(back_populates="employees")
    customers: Mapped[list["Customer"]] = relationship(back_populates="sales_rep")


class Customer(Base):
    __tablename__ = "customers"

    customer_number: Mapped[int] = mapped_column("customerNumber", Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column("customerName", String(50), nullable=False)
    contact_last_name: Mapped[str] = mapped_column("contactLastName", String(50), nullable=False)
    contact_first_name: Mapped[str] = mapped_column("contactFirstName", String(50), nullable=False)
    phone: Mapped[str] = mapped_column("phone", String(50), nullable=False)
    address_line_1: Mapped[str] = mapped_column("addressLine1", String(50), nullable=False)
    address_line_2: Mapped[Optional[str]] = mapped_column("addressLine2", String(50), nullable=True)
    city: Mapped[str] = mapped_column("city", String(50), nullable=False)
    state: Mapped[Optional[str]] = mapped_column("state", String(50), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column("postalCode", String(15), nullable=True)
    country: Mapped[str] = mapped_column("country", String(50), nullable=False)
    sales_rep_employee_number: Mapped[Optional[int]] = mapped_column(
        "salesRepEmployeeNumber", ForeignKey("employees.employeeNumber"), nullable=True
    )
    credit_limit: Mapped[Optional[Decimal]] = mapped_column("creditLimit", Numeric(10, 2), nullable=True)

    sales_rep: Mapped[Optional["Employee"]] = relationship(back_populates="customers")
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
    payments: Mapped[list["Payment"]] = relationship(back_populates="customer")


class Payment(Base):
    __tablename__ = "payments"

    customer_number: Mapped[int] = mapped_column(
        "customerNumber", ForeignKey("customers.customerNumber"), primary_key=True
    )
    check_number: Mapped[str] = mapped_column("checkNumber", String(50), primary_key=True)
    payment_date: Mapped[date] = mapped_column("paymentDate", Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column("amount", Numeric(10, 2), nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="payments")


class Order(Base):
    __tablename__ = "orders"

    order_number: Mapped[int] = mapped_column("orderNumber", Integer, primary_key=True)
    order_date: Mapped[date] = mapped_column("orderDate", Date, nullable=False)
    required_date: Mapped[date] = mapped_column("requiredDate", Date, nullable=False)
    shipped_date: Mapped[Optional[date]] = mapped_column("shippedDate", Date, nullable=True)
    status: Mapped[str] = mapped_column("status", String(15), nullable=False)
    comments: Mapped[Optional[str]] = mapped_column("comments", Text, nullable=True)
    customer_number: Mapped[int] = mapped_column(
        "customerNumber", ForeignKey("customers.customerNumber"), nullable=False
    )

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    details: Mapped[list["OrderDetail"]] = relationship(back_populates="order")


class OrderDetail(Base):
    __tablename__ = "orderdetails"

    order_number: Mapped[int] = mapped_column(
        "orderNumber", ForeignKey("orders.orderNumber"), primary_key=True
    )
    product_code: Mapped[str] = mapped_column(
        "productCode", ForeignKey("products.productCode"), primary_key=True
    )
    quantity_ordered: Mapped[int] = mapped_column("quantityOrdered", Integer, nullable=False)
    price_each: Mapped[Decimal] = mapped_column("priceEach", Numeric(10, 2), nullable=False)
    order_line_number: Mapped[int] = mapped_column("orderLineNumber", SmallInteger, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="details")
    product: Mapped["Product"] = relationship(back_populates="order_details")
