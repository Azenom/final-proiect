import sqlite3
import csv

DB_PATH = "data/inventory.db"

def add_employee(first_name, last_name, department):
    if employee_exists(first_name, last_name):
        return "❌ Employee already exists"
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
        return None
    except sqlite3.Error as e:
        return f"❌ Database error: {e}"
    finally:
        conn.close()

def import_employees_from_csv(file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    imported = 0
    duplicates = 0
    invalid = 0

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        required_columns = ["first_name","last_name","department"]
        
        if not reader.fieldnames:
            conn.close()
            return "❌ CSV file is empty"
        reader.fieldnames = [field.strip().lower()for field in reader.fieldnames]

        missing = [col for col in required_columns if col not in reader.fieldnames]
        if missing:
            conn.close()
            return (
                "❌ Invalid CSV header. "
                "Required columns: "
                "first_name, last_name, department")

        for row in reader:
            row = {k.strip().lower(): v for k, v in row.items()}
            if (not row["first_name"].strip() or not row["last_name"].strip()):
                invalid += 1
                continue
            try:
                cursor.execute("""
                    INSERT INTO employees (
                        first_name,
                        last_name,
                        department
                    )
                    VALUES (?, ?, ?)
                """, (row["first_name"],row["last_name"],row["department"]))
                imported += 1
            except sqlite3.IntegrityError:
                duplicates += 1
    conn.commit()
    conn.close()

    return {
        "imported": imported,
        "duplicates": duplicates,
        "invalid": invalid}

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
    if employee_exists(first_name, last_name, employee_id):
        return "❌ Employee already exists"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE employees
        SET first_name = ?, last_name = ?, department = ?
        WHERE id = ?
    """, (first_name,last_name,department,employee_id))
    
    conn.commit()
    conn.close()

def employee_exists(first_name, last_name, exclude_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if exclude_id is not None:
        cursor.execute("""
            SELECT id
            FROM employees
            WHERE
            (
                (
                    LOWER(first_name) = LOWER(?)
                    AND LOWER(last_name) = LOWER(?)
                )
                OR
                (
                    LOWER(first_name) = LOWER(?)
                    AND LOWER(last_name) = LOWER(?)
                )
            )
            AND id != ?
        """, (first_name,last_name,last_name,first_name,exclude_id))
    else:
        cursor.execute("""
            SELECT id
            FROM employees
            WHERE
            (
                LOWER(first_name) = LOWER(?)
                AND LOWER(last_name) = LOWER(?)
            )
            OR
            (
                LOWER(first_name) = LOWER(?)
                AND LOWER(last_name) = LOWER(?)
            )
        """, (first_name,last_name,last_name,first_name))

    exists = cursor.fetchone() is not None
    conn.close()
    return exists