import sqlite3
import csv
from models.employee import Employee

DB_PATH = "data/inventory.db"


def add_employee(first_name, last_name, department):

    if employee_exists(first_name, last_name):
        return "❌ Employee already exists"

    try:
        with sqlite3.connect(DB_PATH) as conn:

            conn.execute("PRAGMA foreign_keys = ON")

            conn.execute("""
                INSERT INTO employees (
                    first_name,
                    last_name,
                    department
                )
                VALUES (?, ?, ?)
            """, (
                first_name,
                last_name,
                department
            ))

        return None

    except sqlite3.Error as e:
        return f"❌ Database error: {e}"


def import_employees_from_csv(file_path):

    imported = 0
    duplicates = 0
    invalid = 0

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        cursor = conn.cursor()

        with open(file_path, newline='', encoding='utf-8') as csvfile:

            reader = csv.DictReader(csvfile)

            required_columns = [
                "first_name",
                "last_name",
                "department"
            ]

            if not reader.fieldnames:
                return "❌ CSV file is empty"

            reader.fieldnames = [
                field.strip().lower()
                for field in reader.fieldnames
            ]

            missing = [
                col
                for col in required_columns
                if col not in reader.fieldnames
            ]

            if missing:
                return (
                    "❌ Invalid CSV header. "
                    "Required columns: "
                    "first_name, last_name, department"
                )

            for row in reader:

                row = {
                    k.strip().lower(): v
                    for k, v in row.items()
                }

                if (
                    not row["first_name"].strip()
                    or not row["last_name"].strip()
                ):
                    invalid += 1
                    continue

                try:

                    employee = Employee(
                        None,
                        row["first_name"],
                        row["last_name"],
                        row["department"]
                    )

                    employee.normalize()

                    error = employee.validate()

                    if error:
                        invalid += 1
                        continue

                    cursor.execute("""
                        INSERT INTO employees (
                            first_name,
                            last_name,
                            department
                        )
                        VALUES (?, ?, ?)
                    """, (
                        employee.first_name,
                        employee.last_name,
                        employee.department
                    ))

                    imported += 1

                except sqlite3.IntegrityError:
                    duplicates += 1

    return {
        "imported": imported,
        "duplicates": duplicates,
        "invalid": invalid
    }


def get_all_employees_list(sort_by="name"):

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

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(query)

        return cursor.fetchall()


def employee_has_active_assignment(employee_id):

    with sqlite3.connect(DB_PATH) as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM assignments
            WHERE employee_id = ?
            AND status = 'Active'
        """, (employee_id,))

        return cursor.fetchone() is not None


def delete_employee(employee_id):

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM assignments
            WHERE employee_id = ?
        """, (employee_id,))

        cursor.execute("""
            DELETE FROM employees
            WHERE id = ?
        """, (employee_id,))


def get_employee_by_id(employee_id):

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM employees
            WHERE id = ?
        """, (employee_id,))

        return cursor.fetchone()


def update_employee(employee_id, first_name, last_name, department):

    if employee_exists(first_name, last_name, employee_id):
        return "❌ Employee already exists"

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE employees
            SET first_name = ?,
                last_name = ?,
                department = ?
            WHERE id = ?
        """, (
            first_name,
            last_name,
            department,
            employee_id
        ))

    return None


def employee_exists(first_name, last_name, exclude_id=None):

    first_name = first_name.strip().lower()
    last_name = last_name.strip().lower()

    with sqlite3.connect(DB_PATH) as conn:

        cursor = conn.cursor()

        if exclude_id is not None:

            cursor.execute("""
                SELECT id
                FROM employees
                WHERE
                (
                    (
                        LOWER(first_name) = ?
                        AND LOWER(last_name) = ?
                    )
                    OR
                    (
                        LOWER(first_name) = ?
                        AND LOWER(last_name) = ?
                    )
                )
                AND id != ?
            """, (
                first_name,
                last_name,
                last_name,
                first_name,
                exclude_id
            ))

        else:

            cursor.execute("""
                SELECT id
                FROM employees
                WHERE
                (
                    LOWER(first_name) = ?
                    AND LOWER(last_name) = ?
                )
                OR
                (
                    LOWER(first_name) = ?
                    AND LOWER(last_name) = ?
                )
            """, (
                first_name,
                last_name,
                last_name,
                first_name
            ))

        return cursor.fetchone() is not None