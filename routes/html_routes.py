import app
from flask import render_template
from flask_smorest import Blueprint

html_bp = Blueprint("html", __name__, url_prefix="/")

@html_bp.route("/profile")
def profile_page():
    return render_template("profile/profile.html")

@html_bp.route("/profile/update")
def update_profile():
    return render_template("profile/update_profile.html")

@html_bp.route("/profile/delete")
def delete_profile():
    return render_template("profile/delete_profile.html")

@html_bp.route("/registration-page")
def registration_page():
    return render_template("registration.html")