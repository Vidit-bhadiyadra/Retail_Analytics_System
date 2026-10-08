from utils.db import mysql


def get_all_categories():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, category_name FROM categories ORDER BY category_name ASC")
    categories = cursor.fetchall()
    cursor.close()
    return categories


def get_all_products():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT 
            p.id,
            p.product_name,
            p.brand,
            p.description,
            p.unit,
            c.category_name,
            p.sku,
            p.cost_price,
            p.selling_price,
            p.stock_quantity,
            p.reorder_level,
            p.status,
            p.image
        FROM products p
        JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC
    """)

    products = cursor.fetchall()
    cursor.close()
    return products


def get_product_by_id(product_id):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT 
            id,
            product_name,
            brand,
            description,
            unit,
            category_id,
            sku,
            cost_price,
            selling_price,
            stock_quantity,
            reorder_level,
            status,
            image
        FROM products
        WHERE id = %s
    """, (product_id,))

    product = cursor.fetchone()
    cursor.close()
    return product


def add_product(product_name, brand, description, unit, category_id, sku,
                cost_price, selling_price, stock_quantity, reorder_level, status, image):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO products
        (product_name, brand, description, unit, category_id, sku, cost_price, selling_price,
         stock_quantity, reorder_level, status, image)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        product_name, brand, description, unit, category_id, sku,
        cost_price, selling_price, stock_quantity, reorder_level, status, image
    ))

    mysql.connection.commit()
    cursor.close()


def update_product(product_id, product_name, brand, description, unit, category_id,
                   cost_price, selling_price, stock_quantity, reorder_level, status, image):
    cursor = mysql.connection.cursor()

    if image:
        cursor.execute("""
            UPDATE products
            SET product_name=%s, brand=%s, description=%s, unit=%s, category_id=%s,
                cost_price=%s, selling_price=%s, stock_quantity=%s,
                reorder_level=%s, status=%s, image=%s
            WHERE id=%s
        """, (
            product_name, brand, description, unit, category_id,
            cost_price, selling_price, stock_quantity,
            reorder_level, status, image, product_id
        ))
    else:
        cursor.execute("""
            UPDATE products
            SET product_name=%s, brand=%s, description=%s, unit=%s, category_id=%s,
                cost_price=%s, selling_price=%s, stock_quantity=%s,
                reorder_level=%s, status=%s
            WHERE id=%s
        """, (
            product_name, brand, description, unit, category_id,
            cost_price, selling_price, stock_quantity,
            reorder_level, status, product_id
        ))

    mysql.connection.commit()
    cursor.close()


def delete_product(product_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    mysql.connection.commit()
    cursor.close()


def generate_next_sku(category_id):
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT prefix FROM categories WHERE id = %s", (category_id,))
    category = cursor.fetchone()

    if not category:
        cursor.close()
        return None

    prefix = category[0]

    cursor.execute("""
        SELECT sku
        FROM products
        WHERE sku LIKE %s
        ORDER BY id DESC
        LIMIT 1
    """, (prefix + "%",))

    last_product = cursor.fetchone()

    if last_product:
        last_sku = last_product[0]
        number_part = last_sku.replace(prefix, "")

        if number_part.isdigit():
            next_number = int(number_part) + 1
        else:
            next_number = 1
    else:
        next_number = 1

    new_sku = prefix + str(next_number).zfill(3)

    cursor.close()
    return new_sku