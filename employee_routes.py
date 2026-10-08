from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from models.employee_model import (
    get_all_employees,
    get_employee_by_id,
    generate_employee_code,
    add_employee,
    update_employee,
    delete_employee,
    get_employee_summary
)

from utils.auth_helper import login_required


employee_bp = Blueprint(
    "employee",
    __name__,
    url_prefix="/employees"
)


# ============================================================
# EMPLOYEE LIST
# ============================================================

@employee_bp.route("/")
@login_required
def employee_index():

    employees = get_all_employees()
    summary = get_employee_summary()

    return render_template(
        "employees.html",
        employees=employees,
        summary=summary
    )


# ============================================================
# ADD EMPLOYEE
# ============================================================

@employee_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_employee_route():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        date_of_birth = request.form.get(
            "date_of_birth"
        ) or None

        joining_date = request.form.get(
            "joining_date"
        ) or None

        department = request.form.get(
            "department",
            ""
        ).strip()

        designation = request.form.get(
            "designation",
            ""
        ).strip()

        salary = request.form.get(
            "salary",
            "0"
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        emergency_contact = request.form.get(
            "emergency_contact",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Active"
        ).strip()

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not full_name:
            flash(
                "Employee name is required.",
                "danger"
            )
            return redirect(
                url_for("employee.add_employee_route")
            )

        if not phone:
            flash(
                "Phone number is required.",
                "danger"
            )
            return redirect(
                url_for("employee.add_employee_route")
            )

        if not joining_date:
            flash(
                "Joining date is required.",
                "danger"
            )
            return redirect(
                url_for("employee.add_employee_route")
            )

        try:
            salary = float(salary or 0)

            if salary < 0:
                raise ValueError

        except ValueError:

            flash(
                "Please enter a valid salary.",
                "danger"
            )

            return redirect(
                url_for("employee.add_employee_route")
            )

        # ----------------------------------------------------
        # EMPLOYEE CODE
        # ----------------------------------------------------

        employee_code = generate_employee_code()

        # ----------------------------------------------------
        # PROFILE PHOTO
        # ----------------------------------------------------

        profile_photo = None

        photo = request.files.get(
            "profile_photo"
        )

        if photo and photo.filename:

            profile_photo = photo.filename

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        add_employee(
            employee_code=employee_code,
            full_name=full_name,
            profile_photo=profile_photo,
            phone=phone,
            email=email,
            gender=gender,
            date_of_birth=date_of_birth,
            joining_date=joining_date,
            department=department,
            designation=designation,
            salary=salary,
            address=address,
            city=city,
            emergency_contact=emergency_contact,
            status=status
        )

        flash(
            f"Employee {employee_code} added successfully.",
            "success"
        )

        return redirect(
            url_for("employee.employee_index")
        )

    employee_code = generate_employee_code()

    return render_template(
        "employee_form.html",
        employee=None,
        employee_code=employee_code
    )


# ============================================================
# EMPLOYEE DETAILS
# ============================================================

@employee_bp.route("/details/<int:employee_id>")
@login_required
def employee_details(employee_id):

    employee = get_employee_by_id(
        employee_id
    )

    if not employee:

        flash(
            "Employee not found.",
            "danger"
        )

        return redirect(
            url_for("employee.employee_index")
        )

    return render_template(
        "employee_details.html",
        employee=employee
    )


# ============================================================
# EDIT EMPLOYEE
# ============================================================

@employee_bp.route(
    "/edit/<int:employee_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_employee_route(employee_id):

    employee = get_employee_by_id(
        employee_id
    )

    if not employee:

        flash(
            "Employee not found.",
            "danger"
        )

        return redirect(
            url_for("employee.employee_index")
        )

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        date_of_birth = request.form.get(
            "date_of_birth"
        ) or None

        joining_date = request.form.get(
            "joining_date"
        ) or None

        department = request.form.get(
            "department",
            ""
        ).strip()

        designation = request.form.get(
            "designation",
            ""
        ).strip()

        salary = request.form.get(
            "salary",
            "0"
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        emergency_contact = request.form.get(
            "emergency_contact",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Active"
        ).strip()

        if not full_name:

            flash(
                "Employee name is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "employee.edit_employee_route",
                    employee_id=employee_id
                )
            )

        if not phone:

            flash(
                "Phone number is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "employee.edit_employee_route",
                    employee_id=employee_id
                )
            )

        if not joining_date:

            flash(
                "Joining date is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "employee.edit_employee_route",
                    employee_id=employee_id
                )
            )

        try:

            salary = float(
                salary or 0
            )

            if salary < 0:
                raise ValueError

        except ValueError:

            flash(
                "Please enter a valid salary.",
                "danger"
            )

            return redirect(
                url_for(
                    "employee.edit_employee_route",
                    employee_id=employee_id
                )
            )

        # Keep existing photo
        profile_photo = employee[3]

        photo = request.files.get(
            "profile_photo"
        )

        if photo and photo.filename:
            profile_photo = photo.filename

        update_employee(
            employee_id=employee_id,
            full_name=full_name,
            profile_photo=profile_photo,
            phone=phone,
            email=email,
            gender=gender,
            date_of_birth=date_of_birth,
            joining_date=joining_date,
            department=department,
            designation=designation,
            salary=salary,
            address=address,
            city=city,
            emergency_contact=emergency_contact,
            status=status
        )

        flash(
            "Employee updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "employee.employee_details",
                employee_id=employee_id
            )
        )

    return render_template(
        "employee_form.html",
        employee=employee,
        employee_code=employee[1]
    )


# ============================================================
# DELETE EMPLOYEE
# ============================================================

@employee_bp.route(
    "/delete/<int:employee_id>",
    methods=["POST"]
)
@login_required
def delete_employee_route(employee_id):

    employee = get_employee_by_id(
        employee_id
    )

    if not employee:

        flash(
            "Employee not found.",
            "danger"
        )

        return redirect(
            url_for("employee.employee_index")
        )

    delete_employee(
        employee_id
    )

    flash(
        "Employee deleted successfully.",
        "success"
    )

    return redirect(
        url_for("employee.employee_index")
    )