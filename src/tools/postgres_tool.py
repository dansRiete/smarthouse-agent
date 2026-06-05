import psycopg2
import os
from langchain.tools import tool

@tool
def execute_postgres_query(query: str) -> str:
    """Useful to execute read-only queries against the SmartHouse PostgreSQL database to calculate metrics or find history. Returns the raw result rows. Database: smarthouse, Host: 192.168.0.201, Port: 24870."""
    try:
        conn = psycopg2.connect(
            host="192.168.0.201",
            port=24870,
            database="smarthouse",
            user="smarthouse",
            password=os.environ.get("POSTGRES_PASSWORD", "smarthouse")
        )
        cur = conn.cursor()
        cur.execute(query)
        if cur.description:
            rows = cur.fetchall()
            conn.close()
            return str(rows)
        else:
            conn.commit()
            conn.close()
            return "Query executed successfully, no rows returned."
    except Exception as e:
        return f"Error executing query: {str(e)}"
