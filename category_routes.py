from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.auth_helper import login_required

from models.category_model import (
    get_all_categories_with_count,
    add_category,
    get_category_by_id,
    update_category,
    delete_category,
    category_has_products
)


category_bp = Blueprint("category", __name__, url_prefix="/categories")


@category_bp.route("/")
@login_required
def categories():
    categories = get_all_categories_with_count()
    return render_template("categories.html", categories=categories, edit_category=None)


@category_bp.route("/add", methods=["POST"])
@login_required
def add_category_route():
    category_name = request.form["category_name"]
    prefix = request.form["prefix"]

    add_category(category_name, prefix)

    flash("Category added successfully!", "success")
    return redirect(url_for("category.categories"))


@category_bp.route("/edit/<int:category_id>")
@login_required
def edit_category_route(category_id):
    categories = get_all_categories_with_count()
    edit_category = get_category_by_id(category_id)

    if not edit_category:
        flash("Category not found!", "danger")
        return redirect(url_for("category.categories"))

    return render_template(
        "categories.html",
        categories=categories,
        edit_category=edit_category
    )


@category_bp.route("/update/<int:category_id>", methods=["POST"])
@login_required
def update_category_route(category_id):
    category_name = request.form["category_name"]
    prefix = request.form["prefix"]

    update_category(category_id, category_name, prefix)

    flash("Category updated successfully!", "success")
    return redirect(url_for("category.categories"))


@category_bp.route("/delete/<int:category_id>")
@login_required
def delete_category_route(category_id):
    if category_has_products(category_id):
        flash("Cannot delete this category because products are linked with it.", "danger")
        return redirect(url_for("category.categories"))

    delete_category(category_id)

    flash("Category deleted successfully!", "success")
    return redirect(url_for("category.categories"))