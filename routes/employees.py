from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Flask,
    Response
)

from services.add_employees import (
    add_employee,
    import_employees_from_csv,
    get_all_employees_list,
    delete_employee,
    get_employee_by_id,
    update_employee,
    employee_has_active_assignment
)

from services.logger import logger

from models.employee import Employee

import os


def register_employee_routes(app: Flask) -> None:
    """
    Register employee-related application routes.
    """

    @app.route("/employees/add", methods=["GET", "POST"])
    def add_employee_route() -> str | Response:
        """
        Handle employee creation and CSV imports.
        """

        # Manual add
        if request.method == "POST" and "add_employee" in request.form:

            first_name = request.form["first_name"].strip()
            last_name = request.form["last_name"].strip()
            department = request.form["department"].strip()

            employee = Employee(
                None,
                first_name,
                last_name,
                department
            )

            employee.normalize()

            error = employee.validate()

            if error:

                logger.warning(
                    f"Employee validation failed: {error}"
                )

                flash(error)

                return redirect(
                    url_for("add_employee_route")
                )

            db_error = add_employee(
                employee.first_name,
                employee.last_name,
                employee.department
            )

            if db_error:

                logger.warning(
                    f"Employee creation failed | "
                    f"{employee.full_name()}"
                )

                flash(db_error)

                return redirect(
                    url_for("add_employee_route")
                )

            logger.info(
                f"Employee added successfully | "
                f"{employee.full_name()}"
            )

            flash("✅ Employee added successfully")

            return redirect(
                url_for("add_employee_route")
            )

        # CSV import
        if request.method == "POST" and "import_csv" in request.form:

            file = request.files.get("csv_file")

            if not file or file.filename == "":

                logger.warning(
                    "Employee CSV import attempted "
                    "without file"
                )

                flash("❌ Please select a CSV file")

                return redirect(
                    url_for("add_employee_route")
                )

            upload_path = "temp_employees.csv"

            try:

                file.save(upload_path)

                result = import_employees_from_csv(
                    upload_path
                )

                if isinstance(result, str):

                    logger.warning(
                        f"Employee CSV import failed: "
                        f"{result}"
                    )

                    flash(result)

                    return redirect(
                        url_for("add_employee_route")
                    )

                logger.info(
                    f"Employees CSV imported | "
                    f"Imported: {result['imported']} | "
                    f"Duplicates: {result['duplicates']} | "
                    f"Invalid: {result['invalid']}"
                )

                flash(
                    f"✅ Imported {result['imported']} employees | "
                    f"⚠️ Duplicates: {result['duplicates']} | "
                    f"❌ Invalid rows: {result['invalid']}"
                )

            finally:

                if os.path.exists(upload_path):
                    os.remove(upload_path)

            return redirect(
                url_for("add_employee_route")
            )

        sort_by = request.args.get("sort", "name")

        employees = get_all_employees_list(sort_by)

        return render_template(
            "employees/add.html",
            employees=employees
        )

    @app.route("/employees/delete/<int:employee_id>")
    def delete_employee_route(
        employee_id: int
    ) -> Response:
        """
        Delete an employee if no active assignments exist.
        """

        if employee_has_active_assignment(employee_id):

            logger.warning(
                f"Attempted deletion of employee "
                f"with active assignments | "
                f"employee_id={employee_id}"
            )

            flash(
                "❌ Cannot delete employee "
                "with active assignments"
            )

            return redirect(
                url_for("add_employee_route")
            )

        delete_employee(employee_id)

        logger.info(
            f"Employee deleted successfully | "
            f"employee_id={employee_id}"
        )

        flash("✅ Employee deleted")

        return redirect(
            url_for("add_employee_route")
        )

    @app.route(
        "/employees/edit/<int:employee_id>",
        methods=["GET", "POST"]
    )
    def edit_employee(
        employee_id: int
    ) -> str | Response:
        """
        Handle employee editing operations.
        """

        if request.method == "POST":

            first_name = request.form["first_name"].strip()
            last_name = request.form["last_name"].strip()
            department = request.form["department"].strip()

            employee = Employee(
                employee_id,
                first_name,
                last_name,
                department
            )

            employee.normalize()

            error = employee.validate()

            if error:

                logger.warning(
                    f"Employee update validation failed | "
                    f"employee_id={employee_id}"
                )

                flash(error)

                return redirect(
                    url_for(
                        "edit_employee",
                        employee_id=employee_id
                    )
                )

            result = update_employee(
                employee_id,
                employee.first_name,
                employee.last_name,
                employee.department
            )

            if result:

                logger.warning(
                    f"Employee update failed | "
                    f"employee_id={employee_id}"
                )

                flash(result)

                return redirect(
                    url_for(
                        "edit_employee",
                        employee_id=employee_id
                    )
                )

            logger.info(
                f"Employee updated successfully | "
                f"employee_id={employee_id}"
            )

            flash("✅ Employee updated successfully")

            return redirect(
                url_for("add_employee_route")
            )

        employee = get_employee_by_id(employee_id)

        return render_template(
            "employees/edit.html",
            employee=employee
        )