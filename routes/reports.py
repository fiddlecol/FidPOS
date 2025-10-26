# routes/reports.py

from flask import Blueprint, render_template, jsonify
from models import Sale

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.route("/")
def reports_index():
    # Example: render a report summary page
    return render_template("reports.html")

@reports_bp.route("/data")
def report_data():
    # Example: return sales data as JSON (adjust as needed)
    sales = Sale.query.all()
    data = [
        {
            "id": s.id,
            "item": s.item_name,
            "total": s.total,
            "date": s.date.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for s in sales
    ]
    return jsonify(data)
