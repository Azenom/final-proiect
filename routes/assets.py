from flask import render_template, request, redirect, url_for
from services.add_assets import add_asset

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

        return render_template("assets/add.html")