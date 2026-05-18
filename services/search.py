import sqlite3

from services.logger import logger


DB_PATH: str = "data/inventory.db"


def global_search(
    search: str
) -> dict[str, list[sqlite3.Row]]:
    """
    Perform a global search across employees and assets.

    Returns:
        Dictionary containing employee and asset results.
    """

    search_term = f"%{search.strip().lower()}%"

    logger.info(
        f"Global search executed: {search}"
    )

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

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

    logger.info(
        f"Search completed | "
        f"Employees: {len(employee_results)} | "
        f"Assets: {len(asset_results)}"
    )

    return {
        "employees": employee_results,
        "assets": asset_results
    }