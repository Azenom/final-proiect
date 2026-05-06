from flask import render_template, request, redirect, url_for
from services.add_employees import add_employee, import_employees_from_csv
import os

def register_employee_routes(app):

    @app.route("/employees/add", methods=["GET", "POST"])
    def add_employee_route():

        # Manual add
        if request.method == "POST" and "add_employee" in request.form:
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            department = request.form["department"]
            add_employee(first_name, last_name, department)
            return redirect(url_for("add_employee_route"))

        # CSV import
        if request.method == "POST" and "import_csv" in request.form:
            file = request.files["csv_file"]
            if file:
                upload_path = "temp_employees.csv"
                file.save(upload_path)
                import_employees_from_csv(upload_path)
                os.remove(upload_path)
            return redirect(url_for("add_employee_route"))

        return render_template("employees/add.html")
    