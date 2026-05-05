import sqlite3

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