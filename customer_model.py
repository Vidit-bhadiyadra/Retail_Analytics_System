from utils.db import mysql


def get_all_customers():
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
        ORDER BY id DESC
    """)

    customers = cursor.fetchall()
    cursor.close()

    return customers


def add_customer(customer_name, phone, email, gender, address, city, status):
    cursor = mysql.connection.cursor()

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
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        customer_name,
        phone,
        email,
        gender,
        address,
        city,
        status
    ))

    mysql.connection.commit()
    cursor.close()


def get_customer_by_id(customer_id):
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
            status
        FROM customers
        WHERE id = %s
    """, (customer_id,))

    customer = cursor.fetchone()
    cursor.close()

    return customer


def update_customer(
    customer_id,
    customer_name,
    phone,
    email,
    gender,
    address,
    city,
    status
):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE customers
        SET
            customer_name = %s,
            phone = %s,
            email = %s,
            gender = %s,
            address = %s,
            city = %s,
            status = %s
        WHERE id = %s
    """, (
        customer_name,
        phone,
        email,
        gender,
        address,
        city,
        status,
        customer_id
    ))

    mysql.connection.commit()
    cursor.close()


def delete_customer(customer_id):
    cursor = mysql.connection.cursor()

    cursor.execute(
        "DELETE FROM customers WHERE id = %s",
        (customer_id,)
    )

    mysql.connection.commit()
    cursor.close()