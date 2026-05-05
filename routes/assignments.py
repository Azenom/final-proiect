from flask import render_template, request, redirect, url_for
from services.assignments import (
    assign_asset,
    return_asset,
    get_all_employees,
    get_available_assets,
    get_assignments
)

def register_assignment_routes(app):

    @app.route("/assign", methods=["GET", "POST"])
    def assign_asset_route():
        if request.method == "POST":
            asset_id = request.form["asset_id"]
            employee_id = request.form["employee_id"]

            assign_asset(asset_id, employee_id)

            return redirect(url_for("assign_asset_route"))

        employees = get_all_employees()
        assets = get_available_assets()

        return render_template(
            "assignments/assign.html",
            employees=employees,
            assets=assets
        )


    @app.route("/assignments")
    def list_assignments():
        data = get_assignments()
        return render_template("assignments/list.html", assignments=data)


    @app.route("/return/<int:assignment_id>")
    def return_asset_route(assignment_id):
        return_asset(assignment_id)
        return redirect(url_for("list_assignments"))