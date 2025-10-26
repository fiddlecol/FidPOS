# routes/settings.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db  

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

@settings_bp.route("/")
def settings_index():
    return render_template("settings.html")

@settings_bp.route("/update", methods=["POST"])
def update_settings():
    # Example placeholder — modify as needed
    new_value = request.form.get("value")
    if not new_value:
        flash("Missing value", "error")
        return redirect(url_for("settings.settings_index"))

    # Example: pretend to save to DB or config file
    print(f"✅ Updated setting: {new_value}")
    flash("Settings updated successfully!", "success")
    return redirect(url_for("settings.settings_index"))
