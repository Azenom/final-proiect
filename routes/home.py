from flask import (
    render_template,
    request,
    Flask
)

from services.search import global_search
from services.logger import logger

import sqlite3


DB_PATH: str = "data/inventory.db"


def register_home_routes(app: Flask) -> None:
    """
    Register home and dashboard routes.
    """

    @app.route("/")
    def home() -> str:
        """
        Display the application dashboard and search results.
        """

        # Search
        search = request.args.get(
            "search",
            ""
        ).strip()

        results: dict[str, list] = {
            "employees": [],
            "assets": []
        }

        if search:

            logger.info(
                f"Global search performed: {search}"
            )

            results = global_search(search)

        with sqlite3.connect(DB_PATH) as conn:

            cursor = conn.cursor()

            # Dashboard stats
            cursor.execute("""
                SELECT COUNT(*)
                FROM employees
            """)

            employees = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM assets
            """)

            assets = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM assets
                WHERE status = 'Available'
            """)

            available = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM assignments
                WHERE status = 'Active'
            """)

            assigned = cursor.fetchone()[0]

        return render_template(
            "home.html",
            employees=employees,
            assets=assets,
            available=available,
            assigned=assigned,
            search=search,
            employee_results=results["employees"],
            asset_results=results["assets"]
        )