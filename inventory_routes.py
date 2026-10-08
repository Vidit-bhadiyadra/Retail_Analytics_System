from flask import Blueprint, render_template, request, redirect, url_for, flash

from models.inventory_model import (
    get_inventory_summary,
    get_inventory_products,
    get_active_products,
    get_stock_movements,
    add_stock,
    remove_stock,
    adjust_stock
)

from utils.auth_helper import login_required


inventory_bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/inventory"
)


@inventory_bp.route("/")
@login_required
def inventory_index():

    search = request.args.get("search", "").strip()

    stock_filter = request.args.get(
        "stock_filter",
        ""
    ).strip()

    summary = get_inventory_summary()

    products = get_inventory_products(
        search=search,
        stock_filter=stock_filter
    )

    active_products = get_active_products()

    return render_template(
        "inventory.html",
        summary=summary,
        products=products,
        active_products=active_products,
        search=search,
        stock_filter=stock_filter
    )


@inventory_bp.route("/stock-in", methods=["POST"])
@login_required
def stock_in():

    product_id = request.form.get(
        "product_id",
        type=int
    )

    quantity = request.form.get(
        "quantity",
        type=int
    )

    note = request.form.get(
        "note",
        ""
    ).strip()

    if not product_id:

        flash(
            "Please select a product.",
            "danger"
        )

        return redirect(
            url_for("inventory.inventory_index")
        )

    if not quantity or quantity <= 0:

        flash(
            "Please enter a valid quantity.",
            "danger"
        )

        return redirect(
            url_for("inventory.inventory_index")
        )

    success, message = add_stock(
        product_id,
        quantity,
        note
    )

    if success:

        flash(
            message,
            "success"
        )

    else:

        flash(
            message,
            "danger"
        )

    return redirect(
        url_for("inventory.inventory_index")
    )


@inventory_bp.route("/stock-out", methods=["POST"])
@login_required
def stock_out():

    product_id = request.form.get(
        "product_id",
        type=int
    )

    quantity = request.form.get(
        "quantity",
        type=int
    )

    note = request.form.get(
        "note",
        ""
    ).strip()

    if not product_id:

        flash(
            "Please select a product.",
            "danger"
        )

        return redirect(
            url_for("inventory.inventory_index")
        )

    if not quantity or quantity <= 0:

        flash(
            "Please enter a valid quantity.",
            "danger"
        )

        return redirect(
            url_for("inventory.inventory_index")
        )

    success, message = remove_stock(
        product_id,
        quantity,
        note
    )

    if success:

        flash(
            message,
            "success"
        )

    else:

        flash(
            message,
            "danger"
        )

    return redirect(
        url_for("inventory.inventory_index")
    )


@inventory_bp.route("/adjust", methods=["POST"])
@login_required
def adjust():

    product_id = request.form.get(
        "product_id",
        type=int
    )

    new_stock = request.form.get(
        "new_stock",
        type=int
    )

    note = request.form.get(
        "note",
        ""
    ).strip()

    if not product_id:

        flash(
            "Please select a product.",
            "danger"
        )

        return redirect(
            url_for("inventory.inventory_index")
        )

    if new_stock is None or new_stock < 0:

        flash(
            "Please enter a valid stock quantity.",
            "danger"
        )

        return redirect(
            url_for("inventory.inventory_index")
        )

    success, message = adjust_stock(
        product_id,
        new_stock,
        note
    )

    if success:

        flash(
            message,
            "success"
        )

    else:

        flash(
            message,
            "danger"
        )

    return redirect(
        url_for("inventory.inventory_index")
    )


@inventory_bp.route("/movements")
@login_required
def inventory_movements():

    product_id = request.args.get(
        "product_id",
        type=int
    )

    movements = get_stock_movements(
        product_id
    )

    return render_template(
        "inventory_movements.html",
        movements=movements,
        product_id=product_id
    )


@inventory_bp.route("/item/<int:item_id>")
@login_required
def inventory_item(item_id):

    movements = get_stock_movements(
        item_id
    )

    if not movements:

        flash(
            "No inventory movement found for this product.",
            "info"
        )

        return redirect(
            url_for("inventory.inventory_index")
        )

    return render_template(
        "inventory_movements.html",
        movements=movements,
        product_id=item_id
    )