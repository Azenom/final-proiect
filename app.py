from flask import Flask

from connections import db_create
from routes.assets import register_asset_routes
from routes.employees import register_employee_routes
from routes.assignments import register_assignment_routes

app = Flask(__name__)

register_asset_routes(app)
register_employee_routes(app)
register_assignment_routes(app)

if __name__ == "__main__":
    db_create.create_tables()
    app.run(debug=True)