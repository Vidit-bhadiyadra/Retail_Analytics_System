from flask import Blueprint, render_template
from utils.auth_helper import login_required
from models.dashboard_model import get_dashboard_stats

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    dashboard_data = get_dashboard_stats()
    return render_template("dashboard.html", data=dashboard_data)