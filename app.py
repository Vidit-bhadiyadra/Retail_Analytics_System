from flask import Flask

from config import Config
from utils.db import mysql

from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.category_routes import category_bp
from routes.product_routes import product_bp
from routes.customer_routes import customer_bp
from routes.inventory_routes import inventory_bp
from routes.billing_routes import billing_bp
from routes.employee_routes import employee_bp

app = Flask(__name__)

app.config.from_object(Config)

mysql.init_app(app)


# =========================================================
# REGISTER BLUEPRINTS
# =========================================================

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(category_bp)
app.register_blueprint(product_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(employee_bp)

# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)