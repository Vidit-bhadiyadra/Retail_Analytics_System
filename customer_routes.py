from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.auth_helper import login_required

from models.customer_model import (
    get_all_customers,
    add_customer,
    get_customer_by_id,
    update_customer,
    delete_customer
)


customer_bp = Blueprint("customer", __name__, url_prefix="/customers")


@customer_bp.route("/")
@login_required
def customers():
    customers = get_all_customers()
    return render_template("customers.html", customers=customers)


@customer_bp.route("/add", methods=["POST"])
@login_required
def add_customer_route():
    customer_name = request.form["customer_name"]
    phone = request.form["phone"]
    email = request.form["email"]
    gender = request.form["gender"]
    address = request.form["address"]
    city = request.form["city"]
    status = request.form["status"]

    add_customer(customer_name, phone, email, gender, address, city, status)

    flash("Customer added successfully!", "success")
    return redirect(url_for("customer.customers"))


@customer_bp.route("/edit/<int:customer_id>", methods=["GET", "POST"])
@login_required
def edit_customer_route(customer_id):
    customer = get_customer_by_id(customer_id)

    if not customer:
        flash("Customer not found!", "danger")
        return redirect(url_for("customer.customers"))

    if request.method == "POST":
        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        gender = request.form["gender"]
        address = request.form["address"]
        city = request.form["city"]
        status = request.form["status"]

        update_customer(customer_id, customer_name, phone, email, gender, address, city, status)

        flash("Customer updated successfully!", "success")
        return redirect(url_for("customer.customers"))

    return render_template("edit_customer.html", customer=customer)


@customer_bp.route("/delete/<int:customer_id>")
@login_required
def delete_customer_route(customer_id):
    delete_customer(customer_id)

    flash("Customer deleted successfully!", "danger")
    return redirect(url_for("customer.customers"))