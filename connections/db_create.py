import sqlite3

DB_PATH = "data/inventory.db"

def create_tables():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Employees table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            department TEXT
        );
        """)

        # Assets table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            brand TEXT,
            serial_number TEXT UNIQUE,
            status TEXT NOT NULL DEFAULT 'Available',
            purchase_date TEXT
        );
        """)

        # Assignments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            assigned_date TEXT NOT NULL,
            returned_date TEXT,
            status TEXT NOT NULL DEFAULT 'Active',

            FOREIGN KEY (asset_id) REFERENCES assets(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );
        """)