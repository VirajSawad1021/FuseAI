import re

def validate_sql(sql_query: str) -> bool:
    """Ensures that only SELECT queries are executed to prevent destructive operations."""
    sql_upper = sql_query.upper().strip()
    
    # Must start with SELECT or WITH
    if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
        return False
        
    # Block destructive commands
    dangerous_keywords = ['DROP ', 'DELETE ', 'UPDATE ', 'INSERT ', 'ALTER ', 'TRUNCATE ', 'GRANT ', 'REVOKE ']
    for keyword in dangerous_keywords:
        if re.search(r'\b' + keyword + r'\b', sql_upper):
            return False
            
    return True
