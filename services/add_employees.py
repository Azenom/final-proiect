import sqlite3
import csv

DB_PATH = "data/inventory.db"

def add_employee(first_name, last_name, department):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO employees (
                first_name,
                last_name,
                department
            )
            VALUES (?, ?, ?)
        """, (first_name, last_name, department))

        conn.commit()

        employee_id = cursor.lastrowid
        print(f"✅ Employee added with ID: {employee_id}")

        return employee_id

    except sqlite3.Error as e:
        print("❌ Error:", e)

    finally:
        conn.close()

def import_employees_from_csv(file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            cursor.execute("""
                INSERT INTO employees (
                    first_name,
                    last_name,
                    department
                )
                VALUES (?, ?, ?)
            """, (
                row["first_name"],
                row["last_name"],
                row["department"]
            ))

    conn.commit()
    conn.close()
