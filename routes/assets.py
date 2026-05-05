from flask import render_template, request, redirect, url_for
from services.add_assets import add_asset, get_all_assets, delete_asset, update_asset, get_asset_by_id

def register_asset_routes(app):

    @app.route("/assets/add", methods=["GET", "POST"])
    def add_asset_route():
        if request.method == "POST":
            category = request.form["category"]
            brand = request.form["brand"]
            serial_number = request.form["serial_number"]
            purchase_date = request.form["purchase_date"]
            add_asset(category, brand, serial_number, purchase_date)
            return redirect(url_for("add_asset_route"))

        assets = get_all_assets()

        return render_template(
            "assets/add.html",
            assets=assets
        )
    
    @app.route("/assets/delete/<int:asset_id>")
    def delete_asset_route(asset_id):
        delete_asset(asset_id)
        return redirect(url_for("add_asset_route"))
    
    @app.route("/assets/edit/<int:asset_id>", methods=["GET", "POST"])
    def edit_asset(asset_id):
        if request.method == "POST":
            category = request.form["category"]
            brand = request.form["brand"]
            serial = request.form["serial_number"]
            status = request.form["status"]
            update_asset(asset_id, category, brand, serial, status)
            return redirect(url_for("add_asset_route"))

        asset = get_asset_by_id(asset_id)
        return render_template("assets/edit.html", asset=asset)