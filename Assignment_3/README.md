# FuseAI — Week 3 Assignment: Agentic Text-to-SQL System

A FastAPI-powered AI agent that converts natural language questions into SQL queries, executes them against a PostgreSQL database, and returns human-readable answers.

---

## 🧠 What It Does

1. **Understands** a natural language question (e.g. *"How many customers are from the USA?"*)
2. **Decomposes** it into structured components (intent, tables, filters, joins)
3. **Generates** a safe PostgreSQL `SELECT` query via GPT-4o-mini
4. **Validates** the query (blocks `DROP`, `DELETE`, `UPDATE`, `INSERT`)
5. **Executes** it against the ClassicModels PostgreSQL database
6. **Self-corrects** and retries up to 3 times on failure
7. **Summarizes** the result in plain English

---

## 🗂️ Project Structure

```
Assignment_3/
├── app/
│   ├── main.py          # FastAPI app + /agent/sql endpoint
│   ├── sql_generator.py # LLM decomposition, SQL generation, self-correction
│   ├── database.py      # Sync (psycopg2) + Async (SQLAlchemy) DB setup
│   ├── validator.py     # SQL safety validator
│   ├── models.py        # SQLAlchemy ORM models
│   ├── schemas.py       # Pydantic v2 request/response schemas
│   ├── crud.py          # Async CRUD operations
│   ├── router.py        # API router registration
│   ├── routers/
│   │   ├── customers.py # CRUD endpoints for customers
│   │   └── counts.py    # Row count endpoints for all tables
│   ├── config.py        # Settings via dataclass + lru_cache
│   └── logger.py        # Dual file + stdout logging
├── requirements.txt
├── seed.sql             # ClassicModels database seed
└── .env.example         # Environment variable template
```

---

## ⚙️ Setup

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 16 running (via Docker recommended)
- An OpenAI API key

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=assignment_db
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/assignment_db
OPENAI_API_KEY=sk-...
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🚀 API Endpoints

### `POST /agent/sql` — Main Agent Endpoint

```bash
curl -X POST http://localhost:8000/agent/sql \
  -H "Content-Type: application/json" \
  -d '{"question": "How many customers are from the USA?"}'
```

**Response:**
```json
{
  "sql": "SELECT COUNT(*) FROM customers WHERE country = 'USA'",
  "result": [{"count": 36}],
  "summary": "There are 36 customers from the USA.",
  "status": "success",
  "retries": 0,
  "execution_time_ms": 1842.3
}
```

### Other Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/customers` | List customers (paginated) |
| `GET` | `/customers/{id}` | Get customer by ID |
| `GET` | `/customers/{id}/orders` | Get customer orders |
| `GET` | `/customers/{id}/payments` | Get customer payments |
| `POST` | `/customers` | Create customer |
| `PUT` | `/customers/{id}` | Update customer |
| `DELETE` | `/customers/{id}` | Delete customer |
| `GET` | `/customers/count` | Count of customers |
| `GET` | `/overall_counts` | Row counts for all 8 tables |

Interactive docs: **http://localhost:8000/docs**

---

## 🗄️ Database

Uses the **ClassicModels** sample database (8 tables: customers, orders, orderdetails, products, productlines, employees, offices, payments).

Seed the database with `seed.sql` or use the Docker setup from `assignment-2/`.

---

## 🔒 Safety

- Only `SELECT` and `WITH` queries are allowed
- `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE` are blocked
- Max 3 retry attempts on query failure
