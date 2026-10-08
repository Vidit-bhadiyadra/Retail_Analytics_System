from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from models.billing_model import (
    generate_invoice_number,
    get_billing_products,
    get_billing_customers,
    create_sale,
    get_all_sales,
    get_sale_by_id,
    cancel_sale
)

from utils.auth_helper import login_required


billing_bp = Blueprint(
    "billing",
    __name__,
    url_prefix="/billing"
)


# =========================================================
# BILLING PAGE
# =========================================================

@billing_bp.route("/")
@login_required
def billing_index():

    products = get_billing_products()

    customers = get_billing_customers()

    invoice_number = generate_invoice_number()

    return render_template(
        "billing.html",
        products=products,
        customers=customers,
        invoice_number=invoice_number
    )


# =========================================================
# CREATE BILL
# =========================================================

@billing_bp.route("/create", methods=["POST"])
@login_required
def create_billing():

    try:

        customer_id = request.form.get("customer_id")

        if customer_id == "":
            customer_id = None

        payment_method = request.form.get(
            "payment_method",
            "Cash"
        )

        subtotal = float(
            request.form.get("subtotal", 0)
        )

        discount = float(
            request.form.get("discount", 0)
        )

        tax = float(
            request.form.get("tax", 0)
        )

        grand_total = float(
            request.form.get("grand_total", 0)
        )


        product_ids = request.form.getlist(
            "product_id[]"
        )

        quantities = request.form.getlist(
            "quantity[]"
        )

        unit_prices = request.form.getlist(
            "unit_price[]"
        )

        item_discounts = request.form.getlist(
            "item_discount[]"
        )


        if not product_ids:

            flash(
                "Please add at least one product to the bill.",
                "danger"
            )

            return redirect(
                url_for(
                    "billing.billing_index"
                )
            )


        items = []


        for i in range(len(product_ids)):

            if not product_ids[i]:
                continue


            quantity = int(
                quantities[i]
            )

            unit_price = float(
                unit_prices[i]
            )

            item_discount = float(
                item_discounts[i]
            )


            if quantity <= 0:

                flash(
                    "Product quantity must be greater than zero.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "billing.billing_index"
                    )
                )


            items.append({

                "product_id":
                    int(product_ids[i]),

                "quantity":
                    quantity,

                "unit_price":
                    unit_price,

                "discount":
                    item_discount

            })


        if not items:

            flash(
                "Please add valid products to the bill.",
                "danger"
            )

            return redirect(
                url_for(
                    "billing.billing_index"
                )
            )


        user_id = session.get(
            "user_id"
        )


        if not user_id:

            flash(
                "Your session has expired. Please login again.",
                "danger"
            )

            return redirect(
                url_for(
                    "auth.login"
                )
            )


        invoice_number = generate_invoice_number()


        sale_id = create_sale(

            invoice_number=invoice_number,

            customer_id=customer_id,

            user_id=user_id,

            subtotal=subtotal,

            discount=discount,

            tax=tax,

            grand_total=grand_total,

            payment_method=payment_method,

            items=items

        )


        flash(
            f"Invoice {invoice_number} created successfully.",
            "success"
        )


        return redirect(
            url_for(
                "billing.invoice",
                sale_id=sale_id
            )
        )


    except ValueError:

        flash(
            "Invalid billing data. Please check the entered values.",
            "danger"
        )

        return redirect(
            url_for(
                "billing.billing_index"
            )
        )


    except Exception as e:

        flash(
            str(e),
            "danger"
        )

        return redirect(
            url_for(
                "billing.billing_index"
            )
        )


# =========================================================
# CREATE CUSTOMER FROM BILLING PAGE
# =========================================================

@billing_bp.route(
    "/create-customer",
    methods=["POST"]
)
@login_required
def create_billing_customer_route():

    try:

        data = request.get_json()

        if not data:

            return {
                "success": False,
                "message": "Invalid customer data."
            }, 400


        customer_name = data.get(
            "customer_name",
            ""
        ).strip()

        phone = data.get(
            "phone",
            ""
        ).strip()

        email = data.get(
            "email",
            ""
        ).strip()

        gender = data.get(
            "gender",
            ""
        ).strip()

        address = data.get(
            "address",
            ""
        ).strip()

        city = data.get(
            "city",
            ""
        ).strip()

        status = data.get(
            "status",
            "Active"
        ).strip()


        # ---------------------------------------------
        # VALIDATION
        # ---------------------------------------------

        if not customer_name:

            return {
                "success": False,
                "message": "Customer name is required."
            }, 400


        if not phone:

            return {
                "success": False,
                "message": "Phone number is required."
            }, 400


        # ---------------------------------------------
        # DATABASE CONNECTION
        # ---------------------------------------------

        from utils.db import mysql

        cursor = mysql.connection.cursor()


        # ---------------------------------------------
        # CHECK DUPLICATE PHONE
        # ---------------------------------------------

        cursor.execute("""
            SELECT id
            FROM customers
            WHERE phone = %s
            LIMIT 1
        """, (phone,))


        existing_customer = cursor.fetchone()


        if existing_customer:

            cursor.close()

            return {
                "success": False,
                "message":
                    "A customer with this phone number already exists."
            }, 400


        # ---------------------------------------------
        # INSERT CUSTOMER
        # ---------------------------------------------

        cursor.execute("""
            INSERT INTO customers
            (
                customer_name,
                phone,
                email,
                gender,
                address,
                city,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (

            customer_name,

            phone,

            email,

            gender,

            address,

            city,

            status

        ))


        new_customer_id = cursor.lastrowid


        mysql.connection.commit()


        # ---------------------------------------------
        # GET NEW CUSTOMER
        # ---------------------------------------------

        cursor.execute("""
            SELECT
                id,
                customer_name,
                phone,
                email,
                gender,
                address,
                city,
                status,
                created_at
            FROM customers
            WHERE id = %s
        """, (
            new_customer_id,
        ))


        customer = cursor.fetchone()


        cursor.close()


        if not customer:

            return {
                "success": False,
                "message":
                    "Customer was created but could not be loaded."
            }, 500


        # ---------------------------------------------
        # RETURN CUSTOMER TO JAVASCRIPT
        # ---------------------------------------------

        return {

            "success": True,

            "message":
                "Customer created successfully.",

            "customer":
                list(customer)

        }


    except Exception as e:

        try:
            mysql.connection.rollback()
        except:
            pass


        return {

            "success": False,

            "message":
                str(e)

        }, 500


# =========================================================
# SALES HISTORY
# =========================================================

@billing_bp.route("/sales")
@login_required
def sales_history():

    sales = get_all_sales()

    return render_template(
        "sales_history.html",
        sales=sales
    )


# =========================================================
# INVOICE
# =========================================================

@billing_bp.route("/invoice/<int:sale_id>")
@login_required
def invoice(sale_id):

    sale, items = get_sale_by_id(
        sale_id
    )


    if not sale:

        flash(
            "Invoice not found.",
            "danger"
        )

        return redirect(
            url_for(
                "billing.sales_history"
            )
        )


    return render_template(
        "invoice.html",
        sale=sale,
        items=items
    )


# =========================================================
# CANCEL SALE
# =========================================================

@billing_bp.route(
    "/cancel/<int:sale_id>",
    methods=["POST"]
)
@login_required
def cancel_billing(sale_id):

    try:

        cancel_sale(
            sale_id
        )


        flash(
            "Sale cancelled successfully and stock has been restored.",
            "success"
        )


    except Exception as e:

        flash(
            str(e),
            "danger"
        )


    return redirect(
        url_for(
            "billing.invoice",
            sale_id=sale_id
        )
    )