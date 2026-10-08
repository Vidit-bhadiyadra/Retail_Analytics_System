import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename

from utils.auth_helper import login_required

from models.product_model import (
    get_all_categories,
    get_all_products,
    get_product_by_id,
    add_product,
    update_product,
    delete_product,
    generate_next_sku
)


product_bp = Blueprint("product", __name__, url_prefix="/products")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def save_product_image(image_file, sku):
    if image_file and image_file.filename != "":
        if allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_filename = sku + "_" + filename

            upload_path = os.path.join(current_app.root_path, current_app.config["UPLOAD_FOLDER"])
            os.makedirs(upload_path, exist_ok=True)

            image_file.save(os.path.join(upload_path, image_filename))
            return image_filename

    return None


@product_bp.route("/")
@login_required
def products():
    categories = get_all_categories()
    products = get_all_products()

    return render_template(
        "products.html",
        categories=categories,
        products=products
    )


@product_bp.route("/add", methods=["POST"])
@login_required
def add_product_route():
    product_name = request.form["product_name"]
    brand = request.form["brand"]
    description = request.form["description"]
    unit = request.form["unit"]
    category_id = request.form["category_id"]
    sku = request.form["sku"]
    cost_price = request.form["cost_price"]
    selling_price = request.form["selling_price"]
    stock_quantity = request.form["stock_quantity"]
    reorder_level = request.form["reorder_level"]
    status = request.form["status"]

    image_filename = None

    if "image" in request.files:
        image_filename = save_product_image(request.files["image"], sku)

    add_product(
        product_name, brand, description, unit, category_id, sku,
        cost_price, selling_price, stock_quantity, reorder_level, status, image_filename
    )

    flash("Product added successfully!", "success")
    return redirect(url_for("product.products"))


@product_bp.route("/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product_route(product_id):
    product = get_product_by_id(product_id)
    categories = get_all_categories()

    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("product.products"))

    if request.method == "POST":
        product_name = request.form["product_name"]
        brand = request.form["brand"]
        description = request.form["description"]
        unit = request.form["unit"]
        category_id = request.form["category_id"]
        cost_price = request.form["cost_price"]
        selling_price = request.form["selling_price"]
        stock_quantity = request.form["stock_quantity"]
        reorder_level = request.form["reorder_level"]
        status = request.form["status"]

        image_filename = None

        if "image" in request.files:
            image_filename = save_product_image(request.files["image"], product[6])

        update_product(
            product_id, product_name, brand, description, unit, category_id,
            cost_price, selling_price, stock_quantity, reorder_level, status, image_filename
        )

        flash("Product updated successfully!", "success")
        return redirect(url_for("product.products"))

    return render_template(
        "edit_product.html",
        product=product,
        categories=categories
    )


@product_bp.route("/delete/<int:product_id>")
@login_required
def delete_product_route(product_id):
    delete_product(product_id)

    flash("Product deleted successfully!", "danger")
    return redirect(url_for("product.products"))


@product_bp.route("/generate-sku/<int:category_id>")
@login_required
def generate_sku(category_id):
    sku = generate_next_sku(category_id)

    if sku:
        return jsonify({"success": True, "sku": sku})

    return jsonify({"success": False, "sku": ""})