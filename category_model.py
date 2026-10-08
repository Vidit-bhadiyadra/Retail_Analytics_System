from utils.db import mysql


def get_all_categories_with_count():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT 
            c.id,
            c.category_name,
            c.prefix,
            COUNT(p.id) AS product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        GROUP BY c.id, c.category_name, c.prefix
        ORDER BY c.id DESC
    """)

    categories = cursor.fetchall()
    cursor.close()
    return categories


def add_category(category_name, prefix):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO categories (category_name, prefix)
        VALUES (%s, %s)
    """, (category_name, prefix.upper()))

    mysql.connection.commit()
    cursor.close()


def get_category_by_id(category_id):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id, category_name, prefix
        FROM categories
        WHERE id = %s
    """, (category_id,))

    category = cursor.fetchone()
    cursor.close()
    return category


def update_category(category_id, category_name, prefix):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE categories
        SET category_name = %s, prefix = %s
        WHERE id = %s
    """, (category_name, prefix.upper(), category_id))

    mysql.connection.commit()
    cursor.close()


def delete_category(category_id):
    cursor = mysql.connection.cursor()

    cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))

    mysql.connection.commit()
    cursor.close()


def category_has_products(category_id):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM products
        WHERE category_id = %s
    """, (category_id,))

    count = cursor.fetchone()[0]
    cursor.close()

    return count > 0