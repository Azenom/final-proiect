import sqlite3
from models.asset import Asset
from models.employee import Employee

DB_PATH = "data/inventory.db"


def assign_asset(asset_id, employee_id):

    try:
        with sqlite3.connect(DB_PATH) as conn:

            conn.execute("PRAGMA foreign_keys = ON")

            cursor = conn.cursor()

            # check availability
            cursor.execute("""
                SELECT status
                FROM assets
                WHERE id = ?
            """, (asset_id,))

            asset = cursor.fetchone()

            if not asset or asset[0] != "Available":
                return "❌ Asset not available"

            # insert assignment
            cursor.execute("""
                INSERT INTO assignments (
                    asset_id,
                    employee_id,
                    assigned_date,
                    status
                )
                VALUES (?, ?, DATE('now'), 'Active')
            """, (
                asset_id,
                employee_id
            ))

            # update asset status
            cursor.execute("""
                UPDATE assets
                SET status = 'Assigned'
                WHERE id = ?
            """, (asset_id,))

        return None

    except sqlite3.Error as e:
        return f"❌ Database error: {e}"


def return_asset(assignment_id):

    try:
        with sqlite3.connect(DB_PATH) as conn:

            conn.execute("PRAGMA foreign_keys = ON")

            cursor = conn.cursor()

            # get asset_id
            cursor.execute("""
                SELECT asset_id
                FROM assignments
                WHERE id = ?
            """, (assignment_id,))

            row = cursor.fetchone()

            if not row:
                return "❌ Assignment not found"

            asset_id = row[0]

            # update assignment
            cursor.execute("""
                UPDATE assignments
                SET returned_date = DATE('now'),
                    status = 'Returned'
                WHERE id = ?
            """, (assignment_id,))

            # update asset
            cursor.execute("""
                UPDATE assets
                SET status = 'Available'
                WHERE id = ?
            """, (asset_id,))

        return None

    except sqlite3.Error as e:
        return f"❌ Database error: {e}"


def get_all_employees():

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id,
                   first_name,
                   last_name
            FROM employees
        """)

        return cursor.fetchall()


def get_available_assets():

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id,
                   category,
                   brand,
                   serial_number
            FROM assets
            WHERE status = 'Available'
        """)

        return cursor.fetchall()


def get_active_assignments(sort_by="assigned_date"):

    allowed_sort = {
        "date": "assignments.assigned_date",
        "name": "employees.first_name",
        "category": "assets.category"
    }

    sort_column = allowed_sort.get(
        sort_by,
        "assignments.assigned_date"
    )

    query = f"""
        SELECT
            assignments.id AS assignment_id,
            assets.id AS asset_id,
            assets.category,
            assets.brand,
            assets.serial_number,
            employees.first_name,
            employees.last_name,
            assignments.assigned_date,
            assignments.status
        FROM assignments
        JOIN assets
            ON assignments.asset_id = assets.id
        JOIN employees
            ON assignments.employee_id = employees.id
        WHERE assignments.status = 'Active'
        ORDER BY {sort_column}
    """

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(query)

        return cursor.fetchall()


def get_asset_history(asset_id):

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                employees.id AS employee_id,
                employees.first_name,
                employees.last_name,
                employees.department,
                assignments.assigned_date,
                assignments.returned_date,
                assignments.status
            FROM assignments
            JOIN employees
                ON assignments.employee_id = employees.id
            WHERE assignments.asset_id = ?
            ORDER BY assignments.assigned_date DESC
        """, (asset_id,))

        rows = cursor.fetchall()

    history = []

    for row in rows:

        employee = Employee(
            row["employee_id"],
            row["first_name"],
            row["last_name"],
            row["department"]
        )

        history.append({
            "employee": employee,
            "assigned_date": row["assigned_date"],
            "returned_date": row["returned_date"],
            "status": row["status"]
        })

    return history


def get_asset_details(asset_id):

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM assets
            WHERE id = ?
        """, (asset_id,))

        row = cursor.fetchone()

    if row:

        return Asset(
            row["id"],
            row["category"],
            row["brand"],
            row["serial_number"],
            row["status"]
        )

    return None