from flask import Blueprint, render_template

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
def analytics_index():
    # TODO: analytics dashboard
    return "Analytics Home"

@analytics_bp.route('/sales')
def sales_analytics():
    # TODO: sales analytics
    return "Sales Analytics"
