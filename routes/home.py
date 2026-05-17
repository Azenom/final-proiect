from flask import render_template
import sqlite3

DB_PATH = "data/inventory.db"

def register_home_routes(app):

    @app.route("/")
    def home():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Dashboard stats
        cursor.execute("SELECT COUNT(*) FROM employees")
        employees = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM assets")
        assets = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM assets WHERE status='Available'")
        available = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM assignments WHERE status='Active'")
        assigned = cursor.fetchone()[0]

        conn.close()
        return render_template("home.html",employees=employees,assets=assets,available=available,assigned=assigned)