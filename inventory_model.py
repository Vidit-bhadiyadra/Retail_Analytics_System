from utils.db import mysql


def get_inventory_summary():
    """
    Return overall inventory statistics.
    """

    cursor = mysql.connection.cursor()

    query = """
        SELECT
            COUNT(*) AS total_products,
            COALESCE(SUM(stock_quantity), 0) AS total_units,
            COALESCE(SUM(stock_quantity * cost_price), 0) AS inventory_value,

            COALESCE(
                SUM(
                    CASE
                        WHEN stock_quantity = 0 THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS out_of_stock,

            COALESCE(
                SUM(
                    CASE
                        WHEN stock_quantity > 0
                        AND stock_quantity <= reorder_level
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS low_stock

        FROM products
        WHERE status = 'Active'
    """

    cursor.execute(query)

    row = cursor.fetchone()

    cursor.close()

    if not row:
        return {
            "total_products": 0,
            "total_units": 0,
            "inventory_value": 0,
            "out_of_stock": 0,
            "low_stock": 0
        }

    return {
        "total_products": row[0] or 0,
        "total_units": row[1] or 0,
        "inventory_value": row[2] or 0,
        "out_of_stock": row[3] or 0,
        "low_stock": row[4] or 0
    }


def get_inventory_products(search="", stock_filter=""):
    """
    Get products with their inventory information.
    """

    cursor = mysql.connection.cursor()

    query = """
        SELECT
            p.id,
            p.product_name,
            p.brand,
            p.sku,
            p.unit,
            p.cost_price,
            p.selling_price,
            p.stock_quantity,
            p.reorder_level,
            p.status,
            p.image,
            c.category_name,

            CASE
                WHEN p.stock_quantity = 0
                    THEN 'Out of Stock'

                WHEN p.stock_quantity <= p.reorder_level
                    THEN 'Low Stock'

                ELSE 'In Stock'
            END AS stock_status

        FROM products p

        LEFT JOIN categories c
            ON p.category_id = c.id

        WHERE 1 = 1
    """

    params = []

    if search:

        query += """
            AND (
                p.product_name LIKE %s
                OR p.sku LIKE %s
                OR p.brand LIKE %s
                OR c.category_name LIKE %s
            )
        """

        search_value = "%" + search + "%"

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])

    if stock_filter == "in_stock":

        query += """
            AND p.stock_quantity > p.reorder_level
        """

    elif stock_filter == "low_stock":

        query += """
            AND p.stock_quantity > 0
            AND p.stock_quantity <= p.reorder_level
        """

    elif stock_filter == "out_of_stock":

        query += """
            AND p.stock_quantity = 0
        """

    elif stock_filter == "active":

        query += """
            AND p.status = 'Active'
        """

    query += """
        ORDER BY
            CASE
                WHEN p.stock_quantity = 0 THEN 1
                WHEN p.stock_quantity <= p.reorder_level THEN 2
                ELSE 3
            END,
            p.product_name ASC
    """

    cursor.execute(query, tuple(params))

    rows = cursor.fetchall()

    products = []

    for row in rows:

        products.append({
            "id": row[0],
            "product_name": row[1],
            "brand": row[2],
            "sku": row[3],
            "unit": row[4],
            "cost_price": row[5],
            "selling_price": row[6],
            "stock_quantity": row[7],
            "reorder_level": row[8],
            "status": row[9],
            "image": row[10],
            "category_name": row[11],
            "stock_status": row[12]
        })

    cursor.close()

    return products


def get_active_products():
    """
    Return active products for stock operations.
    """

    cursor = mysql.connection.cursor()

    query = """
        SELECT
            id,
            product_name,
            sku,
            stock_quantity,
            unit
        FROM products
        WHERE status = 'Active'
        ORDER BY product_name ASC
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    products = []

    for row in rows:

        products.append({
            "id": row[0],
            "product_name": row[1],
            "sku": row[2],
            "stock_quantity": row[3],
            "unit": row[4]
        })

    cursor.close()

    return products


def get_stock_movements(product_id=None):
    """
    Return stock movement history.

    If product_id is supplied,
    only that product's movements are returned.
    """

    cursor = mysql.connection.cursor()

    query = """
        SELECT
            sm.id,
            sm.product_id,
            p.product_name,
            p.sku,
            sm.movement_type,
            sm.quantity,
            sm.previous_stock,
            sm.new_stock,
            sm.note,
            sm.created_at

        FROM stock_movements sm

        INNER JOIN products p
            ON sm.product_id = p.id
    """

    params = []

    if product_id is not None:

        query += """
            WHERE sm.product_id = %s
        """

        params.append(product_id)

    query += """
        ORDER BY sm.created_at DESC, sm.id DESC
    """

    cursor.execute(query, tuple(params))

    rows = cursor.fetchall()

    movements = []

    for row in rows:

        movements.append({
            "id": row[0],
            "product_id": row[1],
            "product_name": row[2],
            "sku": row[3],
            "movement_type": row[4],
            "quantity": row[5],
            "previous_stock": row[6],
            "new_stock": row[7],
            "note": row[8],
            "created_at": row[9]
        })

    cursor.close()

    return movements


def add_stock(product_id, quantity, note=""):
    """
    Add stock to a product.
    """

    if quantity <= 0:
        return False, "Quantity must be greater than zero."

    cursor = mysql.connection.cursor()

    try:

        cursor.execute(
            """
            SELECT stock_quantity
            FROM products
            WHERE id = %s
            FOR UPDATE
            """,
            (product_id,)
        )

        row = cursor.fetchone()

        if not row:

            mysql.connection.rollback()
            cursor.close()

            return False, "Product not found."

        previous_stock = int(row[0] or 0)

        new_stock = previous_stock + quantity

        cursor.execute(
            """
            UPDATE products
            SET stock_quantity = %s
            WHERE id = %s
            """,
            (new_stock, product_id)
        )

        cursor.execute(
            """
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
            (%s, 'Stock In', %s, %s, %s, %s)
            """,
            (
                product_id,
                quantity,
                previous_stock,
                new_stock,
                note
            )
        )

        mysql.connection.commit()

        cursor.close()

        return True, "Stock added successfully."

    except Exception as e:

        mysql.connection.rollback()
        cursor.close()

        return False, "Error while adding stock: " + str(e)


def remove_stock(product_id, quantity, note=""):
    """
    Remove stock from a product.
    Negative stock is not allowed.
    """

    if quantity <= 0:
        return False, "Quantity must be greater than zero."

    cursor = mysql.connection.cursor()

    try:

        cursor.execute(
            """
            SELECT stock_quantity
            FROM products
            WHERE id = %s
            FOR UPDATE
            """,
            (product_id,)
        )

        row = cursor.fetchone()

        if not row:

            mysql.connection.rollback()
            cursor.close()

            return False, "Product not found."

        previous_stock = int(row[0] or 0)

        if quantity > previous_stock:

            mysql.connection.rollback()
            cursor.close()

            return (
                False,
                "Insufficient stock. Available stock: "
                + str(previous_stock)
            )

        new_stock = previous_stock - quantity

        cursor.execute(
            """
            UPDATE products
            SET stock_quantity = %s
            WHERE id = %s
            """,
            (new_stock, product_id)
        )

        cursor.execute(
            """
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
            (%s, 'Stock Out', %s, %s, %s, %s)
            """,
            (
                product_id,
                quantity,
                previous_stock,
                new_stock,
                note
            )
        )

        mysql.connection.commit()

        cursor.close()

        return True, "Stock removed successfully."

    except Exception as e:

        mysql.connection.rollback()
        cursor.close()

        return False, "Error while removing stock: " + str(e)


def adjust_stock(product_id, new_stock, note=""):
    """
    Set the stock to the actual physical quantity.
    """

    if new_stock < 0:
        return False, "Stock cannot be negative."

    cursor = mysql.connection.cursor()

    try:

        cursor.execute(
            """
            SELECT stock_quantity
            FROM products
            WHERE id = %s
            FOR UPDATE
            """,
            (product_id,)
        )

        row = cursor.fetchone()

        if not row:

            mysql.connection.rollback()
            cursor.close()

            return False, "Product not found."

        previous_stock = int(row[0] or 0)

        if previous_stock == new_stock:

            mysql.connection.rollback()
            cursor.close()

            return False, "New stock is the same as current stock."

        difference = abs(new_stock - previous_stock)

        cursor.execute(
            """
            UPDATE products
            SET stock_quantity = %s
            WHERE id = %s
            """,
            (new_stock, product_id)
        )

        cursor.execute(
            """
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
            (%s, 'Adjustment', %s, %s, %s, %s)
            """,
            (
                product_id,
                difference,
                previous_stock,
                new_stock,
                note
            )
        )

        mysql.connection.commit()

        cursor.close()

        return True, "Stock adjusted successfully."

    except Exception as e:

        mysql.connection.rollback()
        cursor.close()

        return False, "Error while adjusting stock: " + str(e)