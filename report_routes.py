from flask import Blueprint, render_template

report_bp = Blueprint('report', __name__, url_prefix='/reports')

@report_bp.route('/')
def reports_index():
    # TODO: reports list
    return render_template('reports.html')

@report_bp.route('/<int:report_id>')
def report_detail(report_id):
    # TODO: show report
    return f"Report {report_id}"
