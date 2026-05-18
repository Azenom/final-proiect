from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Flask,
    Response
)

from services.assignments import (
    assign_asset,
    return_asset,
    get_all_employees,
    get_available_assets,
    get_active_assignments,
    get_asset_history,
    get_asset_details
)

from services.logger import logger


def register_assignment_routes(app: Flask) -> None:
    """
    Register assignment-related application routes.
    """

    @app.route("/assign", methods=["GET", "POST"])
    def assign_asset_route() -> str | Response:
        """
        Handle asset assignment operations.
        """

        if request.method == "POST":

            employee_id = request.form["employee_id"].strip()
            asset_id = request.form["asset_id"].strip()

            if not employee_id or not asset_id:

                logger.warning(
                    "Assignment attempt with missing fields"
                )

                flash("❌ Please fill all required fields")

                return redirect(
                    url_for("assign_asset_route")
                )

            result = assign_asset(
                asset_id,
                employee_id
            )

            if result:

                logger.warning(
                    f"Asset assignment failed | "
                    f"asset_id={asset_id} | "
                    f"employee_id={employee_id}"
                )

                flash(result)

            else:

                logger.info(
                    f"Asset assigned successfully | "
                    f"asset_id={asset_id} | "
                    f"employee_id={employee_id}"
                )

                flash("✅ Asset assigned successfully")

            return redirect(
                url_for("assign_asset_route")
            )

        employees = get_all_employees()

        assets = get_available_assets()

        return render_template(
            "assignments/assign.html",
            employees=employees,
            assets=assets
        )

    @app.route("/assignments")
    def list_assignments() -> str:
        """
        Display all active assignments.
        """

        sort_by = request.args.get("sort", "date")

        data = get_active_assignments(sort_by)

        return render_template(
            "assignments/list.html",
            assignments=data
        )

    @app.route("/return/<int:assignment_id>")
    def return_asset_route(
        assignment_id: int
    ) -> Response:
        """
        Handle asset return operations.
        """

        result = return_asset(assignment_id)

        if result:

            logger.warning(
                f"Asset return failed | "
                f"assignment_id={assignment_id}"
            )

            flash(result)

        else:

            logger.info(
                f"Asset returned successfully | "
                f"assignment_id={assignment_id}"
            )

            flash("✅ Asset returned successfully")

        return redirect(
            url_for("list_assignments")
        )

    @app.route("/asset/<int:asset_id>")
    def asset_history(asset_id: int) -> str:
        """
        Display asset assignment history.
        """

        history = get_asset_history(asset_id)

        asset = get_asset_details(asset_id)

        return render_template(
            "assignments/history.html",
            history=history,
            asset=asset
        )