from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import time

from app.sql_generator import decompose_question, generate_sql, self_correct_sql, summarize_results
from app.database import execute_query
from app.validator import validate_sql
from app.router import api_router

app = FastAPI(title="Text-to-SQL Agent API")
app.include_router(api_router)  # registers /customers/* and /*/count routes

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql: str
    result: list | str
    summary: str
    status: str
    retries: int
    execution_time_ms: float

@app.post("/agent/sql", response_model=QueryResponse)
async def execute_sql_agent(request: QueryRequest):
    """Async agent: decompose → generate SQL → validate → execute → retry → summarize."""
    start_time = time.time()
    
    # Step 1: Decomposition (runs in threadpool to avoid blocking async event loop)
    decomposition = await asyncio.to_thread(decompose_question, request.question)

    # Step 2: Initial SQL Generation
    sql = await asyncio.to_thread(generate_sql, decomposition)

    retries = 0
    max_retries = 3
    final_result = []
    status = "success"

    while retries < max_retries:  # retries: 0, 1, 2  → max 3 total attempts
        # Validate Safety
        if not validate_sql(sql):
            return QueryResponse(
                sql=sql, result=[], summary="Dangerous query blocked.",
                status="failed", retries=retries, execution_time_ms=(time.time()-start_time)*1000
            )

        # Step 3: Execute (run sync psycopg2 call in a threadpool)
        success, results, error_msg = await asyncio.to_thread(execute_query, sql)

        if success:
            final_result = results
            break

        # Step 4: Error Handling & Retry (Task 4)
        retries += 1
        if retries < max_retries:
            print(f"Query Failed. Retry {retries}/{max_retries}. Error: {error_msg}")
            sql = await asyncio.to_thread(self_correct_sql, request.question, sql, error_msg)
        else:
            status = "failed"
            return QueryResponse(
                sql=sql, result=str(error_msg),
                summary="The agent repeatedly failed to generate a valid SQL query.",
                status=status, retries=retries, execution_time_ms=(time.time()-start_time)*1000
            )

    # Step 5: Final Output & Summary
    summary = await asyncio.to_thread(summarize_results, request.question, sql, final_result)

    return QueryResponse(
        sql=sql,
        result=final_result,
        summary=summary,
        status=status,
        retries=retries,
        execution_time_ms=round((time.time() - start_time) * 1000, 2)
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
