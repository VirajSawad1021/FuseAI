import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from app.validator import validate_sql
from app.database import execute_query

load_dotenv()

# ── Lazy OpenAI client ─────────────────────────────────────────────────────────
# Instantiated on first use so a missing API key crashes the *request*, not the
# entire server startup.
_openai_client = None

def _get_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Add it to your .env file or environment."
            )
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client

SCHEMA_CONTEXT = """
Table: productlines (productLine, textDescription, htmlDescription, image)
Table: products (productCode, productName, productLine, productScale, productVendor, productDescription, quantityInStock, buyPrice, MSRP)
Table: offices (officeCode, city, phone, addressLine1, addressLine2, state, country, postalCode, territory)
Table: employees (employeeNumber, lastName, firstName, extension, email, officeCode, reportsTo, jobTitle)
Table: customers (customerNumber, customerName, contactLastName, contactFirstName, phone, addressLine1, addressLine2, city, state, postalCode, country, salesRepEmployeeNumber, creditLimit)
Table: orders (orderNumber, orderDate, requiredDate, shippedDate, status, comments, customerNumber)
Table: orderdetails (orderNumber, productCode, quantityOrdered, priceEach, orderLineNumber)
Table: payments (customerNumber, checkNumber, paymentDate, amount)
"""

def decompose_question(question: str):
    prompt = f"""
    You are an expert SQL Assistant. Analyze the following natural language question and break it down into structured components based on the database schema.
    
    Database Schema:
    {SCHEMA_CONTEXT}
    
    Question: "{question}"
    
    Return ONLY a raw JSON object with these exact keys:
    - "Intent": string
    - "Tables": list of strings
    - "Columns": list of strings
    - "Filters": string
    - "Joins": string
    """
    
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    try:
        content = response.choices[0].message.content.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError, AttributeError) as e:
        print(f"[sql_generator] Failed to parse decomposition response: {e}")
        return {
            "Intent": "Unknown", "Tables": [], "Columns": [], "Filters": "None", "Joins": "None"
        }

def generate_sql(decomposition: dict):
    prompt = f"""
    Generate a PostgreSQL SELECT query based on this decomposition and schema.
    
    Schema:
    {SCHEMA_CONTEXT}
    
    Decomposition:
    {json.dumps(decomposition, indent=2)}
    
    Return ONLY the raw SQL query text, no markdown blocks or explanation.
    """
    
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    sql = response.choices[0].message.content.replace('```sql', '').replace('```', '').strip()
    return sql

def self_correct_sql(question: str, bad_sql: str, error_msg: str):
    prompt = f"""
    You wrote a PostgreSQL query that failed.
    Question: {question}
    Bad SQL: {bad_sql}
    Error: {error_msg}
    
    Schema: {SCHEMA_CONTEXT}
    
    Fix the SQL. Return ONLY the raw valid SQL query without markdown blocks.
    """
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content.replace('```sql', '').replace('```', '').strip()

def summarize_results(question: str, sql: str, results: list):
    prompt = f"""
    The user asked: "{question}"
    The SQL query executed was: {sql}
    The database returned: {results[:5]} ... (truncated if long)
    
    Provide a direct, natural language answer summarizing these results. Make it concise and helpful. 
    """
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()
