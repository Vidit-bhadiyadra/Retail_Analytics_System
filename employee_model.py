from utils.db import mysql


# ============================================================
# GET ALL EMPLOYEES
# ============================================================

def get_all_employees():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id,
            employee_code,
            full_name,
            profile_photo,
            phone,
            email,
            gender,
            date_of_birth,
            joining_date,
            department,
            designation,
            salary,
            address,
            city,
            emergency_contact,
            status,
            created_at,
            updated_at
        FROM employees
        ORDER BY id DESC
    """)

    employees = cursor.fetchall()
    cursor.close()

    return employees


# ============================================================
# GET EMPLOYEE BY ID
# ============================================================

def get_employee_by_id(employee_id):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id,
            employee_code,
            full_name,
            profile_photo,
            phone,
            email,
            gender,
            date_of_birth,
            joining_date,
            department,
            designation,
            salary,
            address,
            city,
            emergency_contact,
            status,
            created_at,
            updated_at
        FROM employees
        WHERE id = %s
    """, (employee_id,))

    employee = cursor.fetchone()

    cursor.close()

    return employee


# ============================================================
# GENERATE EMPLOYEE CODE
# ============================================================

def generate_employee_code():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id
        FROM employees
        ORDER BY id DESC
        LIMIT 1
    """)

    last_employee = cursor.fetchone()

    cursor.close()

    if last_employee:
        next_id = last_employee[0] + 1
    else:
        next_id = 1

    return f"EMP-{next_id:04d}"


# ============================================================
# ADD EMPLOYEE
# ============================================================

def add_employee(
    employee_code,
    full_name,
    profile_photo,
    phone,
    email,
    gender,
    date_of_birth,
    joining_date,
    department,
    designation,
    salary,
    address,
    city,
    emergency_contact,
    status
):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO employees
        (
            employee_code,
            full_name,
            profile_photo,
            phone,
            email,
            gender,
            date_of_birth,
            joining_date,
            department,
            designation,
            salary,
            address,
            city,
            emergency_contact,
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
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """, (
        employee_code,
        full_name,
        profile_photo,
        phone,
        email,
        gender,
        date_of_birth,
        joining_date,
        department,
        designation,
        salary,
        address,
        city,
        emergency_contact,
        status
    ))

    mysql.connection.commit()

    cursor.close()


# ============================================================
# UPDATE EMPLOYEE
# ============================================================

def update_employee(
    employee_id,
    full_name,
    profile_photo,
    phone,
    email,
    gender,
    date_of_birth,
    joining_date,
    department,
    designation,
    salary,
    address,
    city,
    emergency_contact,
    status
):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE employees
        SET
            full_name = %s,
            profile_photo = %s,
            phone = %s,
            email = %s,
            gender = %s,
            date_of_birth = %s,
            joining_date = %s,
            department = %s,
            designation = %s,
            salary = %s,
            address = %s,
            city = %s,
            emergency_contact = %s,
            status = %s
        WHERE id = %s
    """, (
        full_name,
        profile_photo,
        phone,
        email,
        gender,
        date_of_birth,
        joining_date,
        department,
        designation,
        salary,
        address,
        city,
        emergency_contact,
        status,
        employee_id
    ))

    mysql.connection.commit()

    cursor.close()


# ============================================================
# DELETE EMPLOYEE
# ============================================================

def delete_employee(employee_id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM employees
        WHERE id = %s
    """, (employee_id,))

    mysql.connection.commit()

    cursor.close()


# ============================================================
# EMPLOYEE SUMMARY
# ============================================================

def get_employee_summary():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_employees,

            SUM(
                CASE
                    WHEN status = 'Active'
                    THEN 1
                    ELSE 0
                END
            ) AS active_employees,

            SUM(
                CASE
                    WHEN status = 'Inactive'
                    THEN 1
                    ELSE 0
                END
            ) AS inactive_employees,

            COUNT(
                DISTINCT department
            ) AS total_departments

        FROM employees
    """)

    summary = cursor.fetchone()

    cursor.close()

    return summary