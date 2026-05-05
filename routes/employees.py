from flask import render_template, request, redirect, url_for
from services.add_employees import add_employee

def register_employee_routes(app):

    @app.route("/employees/add", methods=["GET", "POST"])
    def add_employee_route():
        if request.method == "POST":
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            department = request.form["department"]

            add_employee(first_name, last_name, department)

            return redirect(url_for("add_employee_route"))

        return render_template("employees/add.html")