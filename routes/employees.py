from flask import render_template, request, redirect, url_for, flash
from services.add_employees import (
    add_employee, 
    import_employees_from_csv,
    get_all_employees_list,
    delete_employee,
    get_employee_by_id,
    update_employee
)
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
            flash("✅ Employee added successfully")
            return redirect(url_for("add_employee_route"))

        # CSV import
        if request.method == "POST" and "import_csv" in request.form:
            file = request.files["csv_file"]
            if file:
                upload_path = "temp_employees.csv"
                file.save(upload_path)
                import_employees_from_csv(upload_path)
                flash("✅ Employees imported successfully")
                os.remove(upload_path)
            return redirect(url_for("add_employee_route"))
        
        sort_by = request.args.get("sort", "name")
        employees = get_all_employees_list(sort_by)
        return render_template ("employees/add.html", employees = employees)

    @app.route("/employees/delete/<int:employee_id>")
    def delete_employee_route(employee_id):
        delete_employee(employee_id)
        flash("✅ Employee deleted")
        return redirect(url_for("add_employee_route"))
    
    @app.route("/employees/edit/<int:employee_id>", methods=["GET", "POST"])
    def edit_employee(employee_id):
        if request.method == "POST":
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            department = request.form["department"]
            update_employee(employee_id,first_name,last_name,department)
            flash("✅ Employee updated successfully")
            return redirect(url_for("add_employee_route"))
        
        employee = get_employee_by_id(employee_id)
        return render_template("employees/edit.html",employee=employee)
    
    