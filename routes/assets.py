from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Flask,
    Response
)

from services.add_assets import (
    add_asset,
    get_all_assets,
    delete_asset,
    update_asset,
    get_asset_by_id,
    import_assets_from_csv,
    asset_has_active_assignment
)

from services.logger import logger

from models.asset import Asset

import os


def register_asset_routes(app: Flask) -> None:
    """
    Register asset-related application routes.
    """

    @app.route("/assets/add", methods=["GET", "POST"])
    def add_asset_route() -> str | Response:
        """
        Handle asset creation and CSV asset imports.
        """

        # Manual add
        if request.method == "POST" and "add_asset" in request.form:

            category = request.form["category"].strip()
            brand = request.form["brand"].strip()
            serial_number = request.form["serial_number"].strip()
            purchase_date = request.form["purchase_date"].strip()

            asset = Asset(
                None,
                category,
                brand,
                serial_number,
                "Available",
                purchase_date
            )

            asset.normalize()

            error = asset.validate()

            if error:

                logger.warning(
                    f"Asset validation failed: {error}"
                )

                flash(error)

                return redirect(url_for("add_asset_route"))

            db_error = add_asset(
                asset.category,
                asset.brand,
                asset.serial_number,
                asset.purchase_date
            )

            if db_error:

                logger.warning(
                    f"Asset creation failed: "
                    f"{asset.serial_number}"
                )

                flash(db_error)

                return redirect(url_for("add_asset_route"))

            logger.info(
                f"Asset added successfully: "
                f"{asset.serial_number}"
            )

            flash("✅ Asset added successfully")

            return redirect(url_for("add_asset_route"))

        # CSV import
        if request.method == "POST" and "import_csv" in request.form:

            file = request.files.get("csv_file")

            if not file or file.filename == "":

                logger.warning(
                    "CSV import attempted without file"
                )

                flash("❌ Please select a CSV file")

                return redirect(url_for("add_asset_route"))

            upload_path = "temp_assets.csv"

            try:

                file.save(upload_path)

                result = import_assets_from_csv(upload_path)

                if isinstance(result, str):

                    logger.warning(
                        f"CSV import failed: {result}"
                    )

                    flash(result)

                    return redirect(url_for("add_asset_route"))

                logger.info(
                    f"Assets CSV imported | "
                    f"Imported: {result['imported']} | "
                    f"Duplicates: {result['duplicates']} | "
                    f"Invalid: {result['invalid']}"
                )

                flash(
                    f"✅ Imported {result['imported']} assets | "
                    f"⚠️ Duplicates: {result['duplicates']} | "
                    f"❌ Invalid rows: {result['invalid']}"
                )

            finally:

                if os.path.exists(upload_path):
                    os.remove(upload_path)

            return redirect(url_for("add_asset_route"))

        sort_by = request.args.get("sort", "status")

        assets = get_all_assets(sort_by)

        return render_template(
            "assets/add.html",
            assets=assets
        )

    @app.route("/assets/delete/<int:asset_id>")
    def delete_asset_route(asset_id: int) -> Response:
        """
        Delete an asset if it has no active assignment.
        """

        if asset_has_active_assignment(asset_id):

            logger.warning(
                f"Attempted deletion of assigned asset: "
                f"{asset_id}"
            )

            flash("❌ Cannot delete assigned asset")

            return redirect(url_for("add_asset_route"))

        delete_asset(asset_id)

        logger.info(
            f"Asset deleted successfully: {asset_id}"
        )

        flash("✅ Asset deleted")

        return redirect(url_for("add_asset_route"))

    @app.route("/assets/edit/<int:asset_id>", methods=["GET", "POST"])
    def edit_asset(asset_id: int) -> str | Response:
        """
        Handle asset editing operations.
        """

        if request.method == "POST":

            category = request.form["category"].strip()
            brand = request.form["brand"].strip()
            serial = request.form["serial_number"].strip()
            status = request.form["status"].strip()

            asset = Asset(
                asset_id,
                category,
                brand,
                serial,
                status
            )

            asset.normalize()

            error = asset.validate()

            if error:

                logger.warning(
                    f"Asset update validation failed: "
                    f"{asset_id}"
                )

                flash(error)

                return redirect(
                    url_for(
                        "edit_asset",
                        asset_id=asset_id
                    )
                )

            result = update_asset(
                asset_id,
                asset.category,
                asset.brand,
                asset.serial_number,
                status
            )

            if result:

                logger.warning(
                    f"Asset update failed: "
                    f"{asset_id}"
                )

                flash(result)

                return redirect(
                    url_for(
                        "edit_asset",
                        asset_id=asset_id
                    )
                )

            logger.info(
                f"Asset updated successfully: "
                f"{asset_id}"
            )

            flash("✅ Asset updated successfully")

            return redirect(url_for("add_asset_route"))

        asset = get_asset_by_id(asset_id)

        return render_template(
            "assets/edit.html",
            asset=asset
        )