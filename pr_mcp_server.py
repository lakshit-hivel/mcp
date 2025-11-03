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
    
    if(query.startswith("SELECT")):
        cursor.execute(query)
        res = cursor.fetchall()
        return json.dumps(res, indent=2, default=str)
    else:
        return "Mission aborted. Please use a SELECT query."


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
    
    Returns:
        JSON with list of tables and their row counts
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
def get_current_database() -> str:
    """Get the current database and schema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT current_database(), current_schema();")
    res = cursor.fetchone()
    return json.dumps(res, indent=2, default=str)

mcp.run()