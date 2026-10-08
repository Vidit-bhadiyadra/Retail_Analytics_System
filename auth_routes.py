from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import UserModel

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = UserModel.get_user_by_credentials(username, password)

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["full_name"] = user[2]
            session["role"] = user[3]

            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid username or password", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))