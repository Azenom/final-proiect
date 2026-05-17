from flask import render_template, request, redirect, url_for, flash
from services.add_assets import add_asset,get_all_assets,delete_asset,update_asset,get_asset_by_id
from services.add_assets import import_assets_from_csv,asset_has_active_assignment
from models.asset import Asset
import os

def register_asset_routes(app):

    @app.route("/assets/add", methods=["GET", "POST"])
    def add_asset_route():

        # Manual add
        if request.method == "POST" and "add_asset" in request.form:
            category = request.form["category"].strip()
            brand = request.form["brand"].strip()
            serial_number = request.form["serial_number"].strip()
            purchase_date = request.form["purchase_date"].strip()

            asset = Asset(None,category,brand,serial_number,"Available",purchase_date)
            asset.normalize()

            error = asset.validate()
            if error:
                flash(error)
                return redirect(url_for("add_asset_route"))

            add_asset(asset.category,asset.brand,asset.serial_number,purchase_date)
            flash("✅ Asset added successfully")
            return redirect(url_for("add_asset_route"))

        # CSV import
        if request.method == "POST" and "import_csv" in request.form:
            file = request.files["csv_file"]
            if file:
                upload_path = "temp_assets.csv"
                file.save(upload_path)
                import_assets_from_csv(upload_path)
                flash("✅ Assets imported successfully")
                os.remove(upload_path)
            return redirect(url_for("add_asset_route"))
        
        sort_by = request.args.get("sort", "status")
        assets = get_all_assets(sort_by)
        return render_template("assets/add.html",assets=assets)

    @app.route("/assets/delete/<int:asset_id>")
    def delete_asset_route(asset_id):
        if asset_has_active_assignment(asset_id):
            flash("❌ Cannot delete assigned asset")
            return redirect(url_for("add_asset_route"))

        delete_asset(asset_id)
        flash("✅ Asset deleted")
        return redirect(url_for("add_asset_route"))

    @app.route("/assets/edit/<int:asset_id>", methods=["GET", "POST"])
    def edit_asset(asset_id):
        if request.method == "POST":
            category = request.form["category"].strip()
            brand = request.form["brand"].strip()
            serial = request.form["serial_number"].strip()
            status = request.form["status"].strip()

            asset = Asset(asset_id,category,brand,serial,status)
            asset.normalize()

            error = asset.validate()
            if error:
                flash(error)
                return redirect(url_for("edit_asset",asset_id=asset_id))

            update_asset(asset_id,asset.category,asset.brand,asset.serial_number,status)
            flash("✅ Asset updated successfully")
            return redirect(url_for("add_asset_route"))

        asset = get_asset_by_id(asset_id)
        return render_template("assets/edit.html",asset=asset)