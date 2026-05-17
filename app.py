from flask import Flask

from connections import db_create

from routes.assets import register_asset_routes
from routes.employees import register_employee_routes
from routes.assignments import register_assignment_routes
from routes.home import register_home_routes
from routes.export import register_export_routes

app = Flask(__name__,static_folder="design")
app.secret_key = "inventory-secret-key"

# Register routes
register_asset_routes(app)
register_employee_routes(app)
register_assignment_routes(app)
register_home_routes(app)
register_export_routes(app)

if __name__ == "__main__":
    db_create.create_tables()
    app.run(debug=True)