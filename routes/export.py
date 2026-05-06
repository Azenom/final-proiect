from flask import send_file
from openpyxl import Workbook
import sqlite3

DB_PATH = "data/inventory.db"

def register_export_routes(app):

    @app.route("/export")
    def export_excel():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        workbook = Workbook()

        # Employees sheet
        employees_sheet = workbook.active
        employees_sheet.title = "Employees"
        employees_sheet.append([
            "ID",
            "First Name",
            "Last Name",
            "Department"
        ])

        cursor.execute("""
            SELECT id, first_name, last_name, department
            FROM employees
        """)

        for row in cursor.fetchall():
            employees_sheet.append(row)

        # Assets sheet
        assets_sheet = workbook.create_sheet(title="Assets")
        assets_sheet.append([
            "ID",
            "Category",
            "Brand",
            "Serial Number",
            "Status",
            "Purchase Date"
        ])

        cursor.execute("""
            SELECT id, category, brand,
                   serial_number, status,
                   purchase_date
            FROM assets
        """)

        for row in cursor.fetchall():
            assets_sheet.append(row)

        # Assignments sheet
        assignments_sheet = workbook.create_sheet(title="Assignments")
        assignments_sheet.append([
            "ID",
            "Employee",
            "Asset",
            "Assigned Date",
            "Returned Date",
            "Status"
        ])

        cursor.execute("""
            SELECT
                assignments.id,
                employees.first_name || ' ' ||
                employees.last_name,
                assets.category || ' - ' ||
                assets.brand,
                assignments.assigned_date,
                assignments.returned_date,
                assignments.status
            FROM assignments
            JOIN employees
                ON assignments.employee_id = employees.id
            JOIN assets
                ON assignments.asset_id = assets.id
        """)

        for row in cursor.fetchall():
            assignments_sheet.append(row)

        conn.close()
        file_name = "inventory_export.xlsx"
        workbook.save(file_name)
        return send_file(file_name,as_attachment=True)