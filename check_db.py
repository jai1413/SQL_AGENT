# check_db.py
import sqlite3
import os

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

print(f"DB Path: {os.path.abspath('example.db')}\n")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = cursor.fetchall()

for (table,) in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count} rows")

print("\n--- Sample from customers ---")
cursor.execute("SELECT * FROM customers LIMIT 3")
print(cursor.fetchall())

print("\n--- Sample from orders ---")
cursor.execute("SELECT * FROM orders LIMIT 3")
print(cursor.fetchall())

conn.close()# check_db.py
import sqlite3
import os

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

print(f"DB Path: {os.path.abspath('example.db')}\n")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = cursor.fetchall()

for (table,) in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count} rows")

print("\n--- Sample from customers ---")
cursor.execute("SELECT * FROM customers LIMIT 3")
print(cursor.fetchall())

print("\n--- Sample from orders ---")
cursor.execute("SELECT * FROM orders LIMIT 3")
print(cursor.fetchall())

conn.close()