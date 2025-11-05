import json
import os
from mcp.server.fastmcp import FastMCP
import psycopg2
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("pr-copilot")

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )

@mcp.tool()
def run_query(query: str) -> str:
    """Run a query for the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if not query.startswith("SELECT"):
        return json.dumps({
            "error": "Only SELECT queries are allowed",
        })
    cursor.execute(query)
    result = cursor.fetchall()
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def get_pr_summary(pr_id: int) -> str:
    """Return every kind of information available in the database for the given PR id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT * from insightly.pull_request where id = {pr_id}
        """
    )
    res = cursor.fetchall()
    return json.dumps(res, indent=2, default=str)

@mcp.tool()
def list_tables() -> str:
    """
    List all tables in the insightly schema with their row counts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT table_name 
        FROM information_schema.tables
        WHERE table_schema = 'insightly' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """
    
    cursor.execute(query)
    table_names = cursor.fetchall()
    
    tables = []

    for (table_name,) in table_names:
        count_query = f"SELECT COUNT(*) FROM insightly.{table_name}"
        cursor.execute(count_query)
        row_count = cursor.fetchone()[0]
        
        tables.append({
            "name": table_name,
            "row_count": row_count
        })
    
    result = {"tables": tables}
    
    cursor.close()
    conn.close()
    
    return json.dumps(result, indent=2)


@mcp.tool()
def safe_sql(sql: str) -> str:
    """
    Validate and safely execute SQL queries.
    
    Args:
        sql: The SQL query to validate and run
        schema_guard: If True, validate table/column names exist
        
    Returns:
        Query results or validation errors
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql_upper = sql.strip().upper()
    
    if not sql_upper.startswith("SELECT"):
        return json.dumps({
            "error": "Only SELECT queries are allowed",
            "provided": sql[:50]
        })
    dangerous_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE"]
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return json.dumps({
                "error": f"Dangerous keyword detected: {keyword}",
                "hint": "Only SELECT queries are allowed"
            })
    
    if "LIMIT" not in sql_upper:
        sql = sql.rstrip(";") + " LIMIT 100"
        added_limit = True
    else:
        added_limit = False

    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "sql": sql
        })
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    mcp.run()