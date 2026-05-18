from flask import (
    render_template,
    request
)

from services.search import global_search

import sqlite3

DB_PATH = "data/inventory.db"

def register_home_routes(app):

    @app.route("/")
    def home():

        # Search
        search = request.args.get(
            "search",
            ""
        ).strip()

        results = {
            "employees": [],
            "assets": []
        }

        if search:
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