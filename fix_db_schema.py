import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "startup_validator.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def add_column(table, column, datatype):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {datatype}")
        print(f"Added {column} to {table}")
    except sqlite3.OperationalError as e:
        print(f"Column {column} probably already exists in {table}: {e}")

add_column("startups", "category", "TEXT")
add_column("analyses", "startup_name", "TEXT")
add_column("analyses", "industry", "TEXT")
add_column("analyses", "validation_experiment", "TEXT")

conn.commit()
conn.close()
print("Database schema migration complete.")
