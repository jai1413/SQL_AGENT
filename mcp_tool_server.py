from mcp.server.fastmcp import FastMCP
import sqlite3
import os

mcp = FastMCP("My_MCP_Server")

# ✅ Absolute path fix
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'example.db')
print(f"Connecting to DB: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

PROTECTED_TABLES = {"sqlite_sequence", "sqlite_master", "sqlite_stat1"}

@mcp.tool("execute_sql_query")
def execute_query(user_input: str):
    print(f"\n🔍 SQL Executing: {user_input}\n") 
    try:
        query = user_input.strip()

        # Block system tables
        for protected in PROTECTED_TABLES:
            if protected in query.lower():
                return f"'{protected}' is a system table and cannot be touched."

        cursor.execute(query)

        if query.lower().startswith("select") or query.lower().startswith("pragma"):
            rows = cursor.fetchall()
            if not rows:
                return "No records found."

            # ✅ Return column headers + rows
            col_names = [desc[0] for desc in cursor.description]
            result = " | ".join(col_names) + "\n"
            result += "-" * 40 + "\n"
            for row in rows:
                result += " | ".join(str(v) for v in row) + "\n"
            return result          # ✅ return, not print

        else:
            conn.commit()
            return "Query executed successfully."  # ✅ return, not nothing

    except Exception as e:
        return f"Error: {str(e)}"  # ✅ never crash

@mcp.tool("get_database_schema")
def get_database_schema():
    """Returns all user-created table names and their column definitions"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)
    tables = cursor.fetchall()

    schema = {}
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = [
            {"col": col[1], "type": col[2]} for col in columns
        ]
    return schema

if __name__ == "__main__":
    mcp.run(transport='sse')