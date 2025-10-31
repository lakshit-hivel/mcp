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
    

mcp.run()