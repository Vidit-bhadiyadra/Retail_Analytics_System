from utils.db import mysql


def get_dashboard_stats():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE status = 'Active'")
    active_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE stock_quantity <= reorder_level")
    low_stock = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE stock_quantity = 0")
    out_of_stock = cursor.fetchone()[0]

    cursor.execute("""
        SELECT 
            p.id,
            p.product_name,
            p.sku,
            p.stock_quantity,
            p.reorder_level,
            p.selling_price,
            p.image,
            c.category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC
        LIMIT 5
    """)
    recent_products = cursor.fetchall()

    cursor.execute("""
        SELECT c.category_name, COUNT(p.id)
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        GROUP BY c.category_name
        ORDER BY c.category_name ASC
    """)
    category_data = cursor.fetchall()

    cursor.close()

    category_labels = [row[0] for row in category_data]
    category_values = [row[1] for row in category_data]

    normal_stock = total_products - low_stock

    return {
        "total_products": total_products,
        "active_products": active_products,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "normal_stock": normal_stock,
        "recent_products": recent_products,
        "category_labels": category_labels,
        "category_values": category_values,
        "total_customers": 0,
        "total_sales": 0,
        "total_revenue": 0
    }