# Assignment 2

## Task 1: Start PostgreSQL

```bash
docker compose up -d
```

The database container uses `seed.sql` automatically on first start.

## Verify the database

```bash
docker exec -it assignment-db /bin/bash
psql -U postgres -d assignment_db
\dt
SELECT COUNT(*) FROM customers;
```

## Task 2 and Task 3: Run the API

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
uvicorn app.main:app --reload
```

Open the docs:

```text
http://localhost:8000/docs
```

## Endpoints

- `GET /customers`
- `GET /customers/{customer_number}`
- `POST /customers`
- `PUT /customers/{customer_number}`
- `DELETE /customers/{customer_number}`
- `GET /customers/{customer_number}/orders`
- `GET /customers/{customer_number}/payments`
- `GET /customers/count`
- `GET /orders/count`
- `GET /products/count`
- `GET /employees/count`
- `GET /offices/count`
- `GET /payments/count`
- `GET /orderdetails/count`
- `GET /productlines/count`
- `GET /overall_counts`
