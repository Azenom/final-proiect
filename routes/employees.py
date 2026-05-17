from flask import render_template, request, redirect, url_for, flash
from services.add_employees import add_employee,import_employees_from_csv,get_all_employees_list,delete_employee
from services.add_employees import get_employee_by_id,update_employee,employee_has_active_assignment
from models.employee import Employee
import os

def register_employee_routes(app):

    @app.route("/employees/add", methods=["GET", "POST"])
    def add_employee_route():

        # Manual add
        if request.method == "POST" and "add_employee" in request.form:
            first_name = request.form["first_name"].strip()
            last_name = request.form["last_name"].strip()
            department = request.form["department"].strip()

            employee = Employee(None,first_name,last_name,department)
            employee.normalize()

            error = employee.validate()
            if error:
                flash(error)
                return redirect(url_for("add_employee_route"))

            db_error = add_employee(employee.first_name,employee.last_name,employee.department)
            if db_error:
                flash(db_error)
                return redirect(url_for("add_employee_route"))

            flash("✅ Employee added successfully")
            return redirect(url_for("add_employee_route"))

        # CSV import
        if request.method == "POST" and "import_csv" in request.form:
            file = request.files["csv_file"]
            if file:
                upload_path = "temp_employees.csv"
                file.save(upload_path)

                result = import_employees_from_csv(upload_path)
                if isinstance(result, str):
                    os.remove(upload_path)
                    flash(result, "error")
                    return redirect(url_for("add_employee_route"))
                
                flash(
                    f"✅ Imported {result['imported']} employees | "
                    f"⚠️ Duplicates: {result['duplicates']} | "
                    f"❌ Invalid rows: {result['invalid']}")
                os.remove(upload_path)
            return redirect(url_for("add_employee_route"))

        sort_by = request.args.get("sort", "name")
        employees = get_all_employees_list(sort_by)
        return render_template("employees/add.html",employees=employees)

    @app.route("/employees/delete/<int:employee_id>")
    def delete_employee_route(employee_id):
        if employee_has_active_assignment(employee_id):
            flash(
                "❌ Cannot delete employee "
                "with active assignments")
            return redirect(url_for("add_employee_route"))
        
        delete_employee(employee_id)
        flash("✅ Employee deleted")
        return redirect(url_for("add_employee_route"))

    @app.route("/employees/edit/<int:employee_id>",methods=["GET", "POST"])
    def edit_employee(employee_id):
        if request.method == "POST":
            first_name = request.form["first_name"].strip()
            last_name = request.form["last_name"].strip()
            department = request.form["department"].strip()

            employee = Employee(employee_id,first_name,last_name,department)
            employee.normalize()

            error = employee.validate()
            if error:
                flash(error)
                return redirect(url_for("edit_employee",employee_id=employee_id))

            db_error = update_employee(employee_id,employee.first_name,employee.last_name,employee.department)
            if db_error:
                flash(db_error)
                return redirect(url_for("edit_employee", employee_id=employee_id))

            flash("✅ Employee updated successfully")   
            return redirect(url_for("add_employee_route"))

        employee = get_employee_by_id(employee_id)
        return render_template("employees/edit.html",employee=employee)