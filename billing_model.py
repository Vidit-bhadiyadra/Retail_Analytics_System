from utils.db import mysql


# ============================================================
# GENERATE NEXT INVOICE NUMBER
# ============================================================

def generate_invoice_number():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id
        FROM sales
        ORDER BY id DESC
        LIMIT 1
    """)

    last_sale = cursor.fetchone()
    cursor.close()

    if last_sale:
        next_id = last_sale[0] + 1
    else:
        next_id = 1

    return f"INV-{next_id:05d}"


# ============================================================
# BILLING PRODUCTS
# ============================================================

def get_billing_products():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id,
            product_name,
            brand,
            sku,
            selling_price,
            stock_quantity,
            unit,
            image
        FROM products
        WHERE status = 'Active'
        ORDER BY product_name ASC
    """)

    products = cursor.fetchall()
    cursor.close()

    return products


# ============================================================
# BILLING CUSTOMERS
# ============================================================

def get_billing_customers():
    cursor = mysql.connection.cursor()

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
        WHERE status = 'Active'
        ORDER BY customer_name ASC
    """)

    customers = cursor.fetchall()

    cursor.close()

    return customers

# ============================================================
# GET SINGLE CUSTOMER
# ============================================================

def get_billing_customer_by_id(customer_id):
    """
    Get complete customer information for billing.
    """

    cursor = mysql.connection.cursor()

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
        LIMIT 1
    """, (customer_id,))

    customer = cursor.fetchone()
    cursor.close()

    if not customer:
        return None

    customer = list(customer)

    created_at = customer[8]

    if hasattr(created_at, "strftime"):
        customer[8] = created_at.strftime("%d %b %Y")
    elif created_at:
        customer[8] = str(created_at)

    return tuple(customer)


# ============================================================
# CREATE CUSTOMER FROM BILLING
# ============================================================

def create_billing_customer(
    customer_name,
    phone,
    email,
    gender,
    address,
    city
):
    """
    Creates a new customer directly from the Billing page.

    Returns:
        {
            "id": customer_id,
            "customer_name": ...,
            "phone": ...,
            ...
        }

    Raises:
        Exception if the phone number already exists.
    """

    cursor = mysql.connection.cursor()

    try:

        # ----------------------------------------------------
        # CHECK DUPLICATE PHONE
        # ----------------------------------------------------

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
            WHERE phone = %s
            LIMIT 1
        """, (phone,))

        existing_customer = cursor.fetchone()

        if existing_customer:

            raise Exception(
                "A customer with this phone number already exists. "
                "Please select the existing customer."
            )

        # ----------------------------------------------------
        # INSERT CUSTOMER
        # ----------------------------------------------------

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
                'Active'
            )
        """, (
            customer_name,
            phone,
            email,
            gender,
            address,
            city
        ))

        customer_id = cursor.lastrowid

        mysql.connection.commit()

        # ----------------------------------------------------
        # FETCH CREATED CUSTOMER
        # ----------------------------------------------------

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
            LIMIT 1
        """, (customer_id,))

        customer = cursor.fetchone()

        if not customer:
            raise Exception(
                "Customer was created but could not be retrieved."
            )

        customer = list(customer)

        created_at = customer[8]

        if hasattr(created_at, "strftime"):
            customer[8] = created_at.strftime("%d %b %Y")
        elif created_at:
            customer[8] = str(created_at)

        return tuple(customer)

    except Exception as e:

        mysql.connection.rollback()

        raise e

    finally:

        cursor.close()


# ============================================================
# CREATE SALE
# ============================================================

def create_sale(
    invoice_number,
    customer_id,
    user_id,
    subtotal,
    discount,
    tax,
    grand_total,
    payment_method,
    items
):

    cursor = mysql.connection.cursor()

    try:

        # ----------------------------------------------------
        # INSERT SALE
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO sales
            (
                invoice_number,
                customer_id,
                user_id,
                subtotal,
                discount,
                tax,
                grand_total,
                payment_method,
                payment_status,
                sale_status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'Paid',
                'Completed'
            )
        """, (
            invoice_number,
            customer_id,
            user_id,
            subtotal,
            discount,
            tax,
            grand_total,
            payment_method
        ))

        sale_id = cursor.lastrowid

        # ----------------------------------------------------
        # INSERT SALE ITEMS + REDUCE STOCK
        # ----------------------------------------------------

        for item in items:

            product_id = item["product_id"]
            quantity = item["quantity"]
            unit_price = item["unit_price"]
            item_discount = item["discount"]

            # -----------------------------------------------
            # LOCK PRODUCT ROW
            # -----------------------------------------------

            cursor.execute("""
                SELECT
                    product_name,
                    stock_quantity
                FROM products
                WHERE id = %s
                FOR UPDATE
            """, (product_id,))

            product = cursor.fetchone()

            if not product:

                raise Exception(
                    f"Product with ID {product_id} was not found."
                )

            product_name = product[0]
            current_stock = product[1]

            # -----------------------------------------------
            # STOCK VALIDATION
            # -----------------------------------------------

            if quantity > current_stock:

                raise Exception(
                    f"Insufficient stock for '{product_name}'. "
                    f"Available stock: {current_stock}, "
                    f"requested: {quantity}."
                )

            # -----------------------------------------------
            # ITEM TOTAL
            # -----------------------------------------------

            item_total = (
                unit_price * quantity
            ) - item_discount

            if item_total < 0:
                item_total = 0

            # -----------------------------------------------
            # INSERT SALE ITEM
            # -----------------------------------------------

            cursor.execute("""
                INSERT INTO sale_items
                (
                    sale_id,
                    product_id,
                    quantity,
                    unit_price,
                    discount,
                    total
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                sale_id,
                product_id,
                quantity,
                unit_price,
                item_discount,
                item_total
            ))

            # -----------------------------------------------
            # REDUCE STOCK
            # -----------------------------------------------

            new_stock = current_stock - quantity

            cursor.execute("""
                UPDATE products
                SET stock_quantity = %s
                WHERE id = %s
            """, (
                new_stock,
                product_id
            ))

            # -----------------------------------------------
            # STOCK MOVEMENT
            # -----------------------------------------------

            cursor.execute("""
                INSERT INTO stock_movements
                (
                    product_id,
                    movement_type,
                    quantity,
                    previous_stock,
                    new_stock,
                    note
                )
                VALUES
                (
                    %s,
                    'Stock Out',
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                product_id,
                quantity,
                current_stock,
                new_stock,
                f"Sale - {invoice_number}"
            ))

        # ----------------------------------------------------
        # PAYMENT
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO payments
            (
                sale_id,
                payment_method,
                amount,
                transaction_reference,
                payment_status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'Paid'
            )
        """, (
            sale_id,
            payment_method,
            grand_total,
            None
        ))

        # ----------------------------------------------------
        # COMMIT EVERYTHING
        # ----------------------------------------------------

        mysql.connection.commit()

        return sale_id

    except Exception as e:

        mysql.connection.rollback()

        raise e

    finally:

        cursor.close()


# ============================================================
# SALES HISTORY
# ============================================================

def get_all_sales():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            s.id,
            s.invoice_number,
            COALESCE(c.customer_name, 'Walk-in Customer'),
            s.created_at,
            s.subtotal,
            s.discount,
            s.grand_total,
            s.payment_method,
            s.payment_status,
            s.sale_status,
            COALESCE(u.full_name, 'Unknown')
        FROM sales s
        LEFT JOIN customers c
            ON s.customer_id = c.id
        LEFT JOIN users u
            ON s.user_id = u.id
        ORDER BY s.id DESC
    """)

    sales = cursor.fetchall()

    cursor.close()

    formatted_sales = []

    for sale in sales:

        sale = list(sale)

        created_at = sale[3]

        if hasattr(created_at, "strftime"):

            sale[3] = created_at.strftime(
                "%d %b %Y, %I:%M %p"
            )

        elif created_at:

            sale[3] = str(created_at)

        formatted_sales.append(tuple(sale))

    return formatted_sales


# ============================================================
# GET SINGLE SALE / INVOICE
# ============================================================

def get_sale_by_id(sale_id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            s.id,
            s.invoice_number,
            s.customer_id,
            c.customer_name,
            c.phone,
            c.email,
            c.address,
            c.city,
            u.full_name,
            s.subtotal,
            s.discount,
            s.tax,
            s.grand_total,
            s.payment_method,
            s.payment_status,
            s.sale_status,
            s.created_at,
            s.created_at
        FROM sales s
        LEFT JOIN customers c
            ON s.customer_id = c.id
        LEFT JOIN users u
            ON s.user_id = u.id
        WHERE s.id = %s
    """, (sale_id,))

    sale = cursor.fetchone()

    if not sale:

        cursor.close()

        return None, []

    # --------------------------------------------------------
    # SALE ITEMS
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            si.id,
            si.sale_id,
            p.product_name,
            p.sku,
            si.quantity,
            si.unit_price,
            si.discount,
            si.total
        FROM sale_items si
        INNER JOIN products p
            ON si.product_id = p.id
        WHERE si.sale_id = %s
        ORDER BY si.id ASC
    """, (sale_id,))

    items = cursor.fetchall()

    cursor.close()

    # --------------------------------------------------------
    # FORMAT DATE
    # --------------------------------------------------------

    sale = list(sale)

    created_at = sale[17]

    if hasattr(created_at, "strftime"):

        sale[17] = created_at.strftime(
            "%d %b %Y, %I:%M %p"
        )

    elif created_at:

        sale[17] = str(created_at)

    sale = tuple(sale)

    return sale, items


# ============================================================
# CANCEL SALE
# ============================================================

def cancel_sale(sale_id):

    cursor = mysql.connection.cursor()

    try:

        # ----------------------------------------------------
        # GET SALE
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                invoice_number,
                sale_status
            FROM sales
            WHERE id = %s
            FOR UPDATE
        """, (sale_id,))

        sale = cursor.fetchone()

        if not sale:

            raise Exception("Sale not found.")

        invoice_number = sale[0]
        sale_status = sale[1]

        # ----------------------------------------------------
        # ALREADY CANCELLED
        # ----------------------------------------------------

        if sale_status == "Cancelled":

            raise Exception(
                "This invoice has already been cancelled."
            )

        # ----------------------------------------------------
        # GET ITEMS
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                product_id,
                quantity
            FROM sale_items
            WHERE sale_id = %s
        """, (sale_id,))

        items = cursor.fetchall()

        # ----------------------------------------------------
        # RESTORE STOCK
        # ----------------------------------------------------

        for item in items:

            product_id = item[0]
            quantity = item[1]

            cursor.execute("""
                SELECT
                    product_name,
                    stock_quantity
                FROM products
                WHERE id = %s
                FOR UPDATE
            """, (product_id,))

            product = cursor.fetchone()

            if not product:

                raise Exception(
                    f"Product with ID {product_id} was not found."
                )

            current_stock = product[1]

            new_stock = current_stock + quantity

            cursor.execute("""
                UPDATE products
                SET stock_quantity = %s
                WHERE id = %s
            """, (
                new_stock,
                product_id
            ))

            # -----------------------------------------------
            # STOCK MOVEMENT
            # -----------------------------------------------

            cursor.execute("""
                INSERT INTO stock_movements
                (
                    product_id,
                    movement_type,
                    quantity,
                    previous_stock,
                    new_stock,
                    note
                )
                VALUES
                (
                    %s,
                    'Stock In',
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                product_id,
                quantity,
                current_stock,
                new_stock,
                f"Sale Cancelled - {invoice_number}"
            ))

        # ----------------------------------------------------
        # UPDATE SALE
        # ----------------------------------------------------

        cursor.execute("""
            UPDATE sales
            SET
                sale_status = 'Cancelled',
                payment_status = 'Cancelled'
            WHERE id = %s
        """, (sale_id,))

        # ----------------------------------------------------
        # UPDATE PAYMENT
        # ----------------------------------------------------

        cursor.execute("""
            UPDATE payments
            SET payment_status = 'Cancelled'
            WHERE sale_id = %s
        """, (sale_id,))

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        mysql.connection.commit()

    except Exception as e:

        mysql.connection.rollback()

        raise e

    finally:

        cursor.close()