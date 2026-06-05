import psycopg2
import os
from langchain.tools import tool

@tool
def execute_postgres_query(query: str) -> str:
    """Useful to execute read-only queries against the SmartHouse PostgreSQL database to calculate metrics or find history. Returns the raw result rows. Database: smarthouse, Host: smarthouse-db, Port: 5432."""
    try:
        conn = psycopg2.connect(
            host="smarthouse-db",
            port=5432,
            database="smarthouse",
            user="smarthouse",
            password=os.environ.get("POSTGRES_PASSWORD", "smarthouse")
        )
        cur = conn.cursor()
        cur.execute("SET search_path TO main, public;")
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
