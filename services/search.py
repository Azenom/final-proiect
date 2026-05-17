import sqlite3

DB_PATH = "data/inventory.db"

def global_search(search):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    search_term = f"%{search.lower()}%"

    # Employees
    cursor.execute("""
        SELECT
            first_name,
            last_name,
            department
        FROM employees
        WHERE
            LOWER(first_name) LIKE ?
            OR LOWER(last_name) LIKE ?
            OR LOWER(department) LIKE ?
    """, (
        search_term,
        search_term,
        search_term
    ))

    employee_results = cursor.fetchall()

    # Assets
    cursor.execute("""
        SELECT
            category,
            brand,
            serial_number,
            status
        FROM assets
        WHERE
            LOWER(category) LIKE ?
            OR LOWER(brand) LIKE ?
            OR LOWER(serial_number) LIKE ?
            OR LOWER(status) LIKE ?
    """, (
        search_term,
        search_term,
        search_term,
        search_term
    ))

    asset_results = cursor.fetchall()

    conn.close()

    return {
        "employees": employee_results,
        "assets": asset_results
    }