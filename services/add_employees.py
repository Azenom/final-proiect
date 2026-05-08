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
        required_columns = ["first_name","last_name","department"]

        if not reader.fieldnames:
            conn.close()
            raise Exception("❌ CSV file is empty")

        missing = [col for col in required_columns if col not in reader.fieldnames]
        if missing:
            conn.close()
            raise Exception(f"❌ Missing columns: {', '.join(missing)}")

        for row in reader:
            if (not row["first_name"].strip() or not row["last_name"].strip()):
                print("❌ Skipped invalid employee row")
                continue

            cursor.execute("""
                INSERT INTO employees (
                    first_name,
                    last_name,
                    department
                )
                VALUES (?, ?, ?)
            """, (row["first_name"],row["last_name"],row["department"]))

    conn.commit()
    conn.close()

def get_all_employees_list(sort_by="name"):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    allowed_sort = {
        "name": "first_name",
        "department": "department"
    }

    sort_column = allowed_sort.get(sort_by, "first_name")

    query = f"""
        SELECT *
        FROM employees
        ORDER BY {sort_column}
    """

    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

def employee_has_active_assignment(employee_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM assignments
        WHERE employee_id = ?
        AND status = 'Active'
    """, (employee_id,))

    active = cursor.fetchone() is not None
    conn.close()
    return active

def delete_employee(employee_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # remove assignments first
    cursor.execute("""
        DELETE FROM assignments
        WHERE employee_id = ?
    """, (employee_id,))

    # remove employee
    cursor.execute("""
        DELETE FROM employees
        WHERE id = ?
    """, (employee_id,))

    conn.commit()
    conn.close()

def get_employee_by_id(employee_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM employees
        WHERE id = ?
    """, (employee_id,))

    employee = cursor.fetchone()
    conn.close()
    return employee

def update_employee(employee_id, first_name, last_name, department):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE employees
        SET first_name = ?, last_name = ?, department = ?
        WHERE id = ?
    """, (
        first_name,
        last_name,
        department,
        employee_id
    ))
    
    conn.commit()
    conn.close()