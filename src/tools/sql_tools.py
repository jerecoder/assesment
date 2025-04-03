import sqlite3
from langchain_core.tools import tool

@tool
def execute_sql(query: str) -> str:
    """Ejecuta query y guarda en string"""
    try:
        with sqlite3.connect("stops.db") as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            if not rows:
                return "No results found"
            
            columns = [desc[0] for desc in cursor.description]
            result = "Columns: " + ", ".join(columns) + "\n"
            result += "\nRows:\n"
            for row in rows:
                result += str(row) + "\n"
            return result
    except Exception as e:
        return f"Error executing query: {str(e)}" 