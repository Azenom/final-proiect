import sqlite3

DB_PATH = "data/inventory.db"


def assign_asset(asset_id, employee_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        # check availability
        cursor.execute("SELECT status FROM assets WHERE id = ?", (asset_id,))
        asset = cursor.fetchone()
        if not asset or asset[0] != "Available":
            raise Exception("Asset not available")

        # insert assignment
        cursor.execute("""
            INSERT INTO assignments (asset_id, employee_id, assigned_date, status)
            VALUES (?, ?, DATE('now'), 'Active')
        """, (asset_id, employee_id))

        # update asset
        cursor.execute("""
            UPDATE assets SET status = 'Assigned'
            WHERE id = ?
        """, (asset_id,))

        conn.commit()

    except Exception as e:
        print("❌ Error:", e)

    finally:
        conn.close()


def return_asset(assignment_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        # Get asset_id
        cursor.execute("SELECT asset_id FROM assignments WHERE id = ?", (assignment_id,))
        row = cursor.fetchone()

        if not row:
            raise Exception("Assignment not found")

        asset_id = row[0]

        # Update assignment
        cursor.execute("""
            UPDATE assignments
            SET returned_date = DATE('now'), status = 'Returned'
            WHERE id = ?
        """, (assignment_id,))

        # Update asset
        cursor.execute("""
            UPDATE assets SET status = 'Available'
            WHERE id = ?
        """, (asset_id,))

        conn.commit()
        print("✅ Asset returned!")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        conn.close()


def get_all_employees():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, first_name, last_name
        FROM employees
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def get_available_assets():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, category, brand, serial_number
        FROM assets
        WHERE status = 'Available'
    """)

    data = cursor.fetchall()
    conn.close()
    return data

def get_assignments():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            assignments.id AS assignment_id,
            assets.category,
            assets.brand,
            assets.serial_number,
            employees.first_name,
            employees.last_name,
            assignments.assigned_date,
            assignments.status
        FROM assignments
        JOIN assets ON assignments.asset_id = assets.id
        JOIN employees ON assignments.employee_id = employees.id
    """)

    data = cursor.fetchall()
    conn.close()
    return data