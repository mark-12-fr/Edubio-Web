from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.teacher_service import (
    create_teacher,
    get_all_teachers,
    delete_teacher_by_id,
    update_teacher
)


from services.database import get_db



teacher_bp = Blueprint("teacher", __name__)


# ==============================
# WEB ROUTES (FOR WEBSITE)
# ==============================
@teacher_bp.route("/teacher_list")
def teacher_list():
    teachers = get_all_teachers()
    return render_template("teacher_list.html", teachers=teachers)


@teacher_bp.route("/teacher_registration", methods=["GET", "POST"])
def teacher_registration():
    if request.method == "POST":


        teacher_id = request.form.get("teacher_id")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        password = request.form.get("password")


        create_teacher(
            teacher_id,
            full_name,
            email,
            subject,
            password
        )

        return redirect(url_for("teacher.teacher_list"))

    return render_template("teacher_registration.html")

@teacher_bp.route("/edit_teacher/<teacher_id>", methods=["GET", "POST"])
def edit_teacher(teacher_id):

    if request.method == "POST":


        full_name = request.form.get("full_name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        status = request.form.get("status")

        update_teacher(
            teacher_id,
            full_name,
            email,
            subject,
            status
        )

        flash("Teacher updated successfully!", "success")
        return redirect(url_for("teacher.teacher_list"))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM teachers WHERE teacher_id=%s",
        (teacher_id,)
    )

    teacher = cursor.fetchone()

    cursor.close()
    conn.close()

    if not teacher:
        flash("Teacher not found.", "danger")
        return redirect(url_for("teacher.teacher_list"))

    return render_template("edit_teacher.html", teacher=teacher)


@teacher_bp.route("/delete_teacher/<teacher_id>")
def delete_teacher(teacher_id):

    delete_teacher_by_id(teacher_id)

    flash("Teacher deleted successfully!", "success")

    return redirect(url_for("teacher.teacher_list"))


# ==============================
# MOBILE API LOGIN (FOR APP)
# ==============================
@teacher_bp.route("/api/mobile-login", methods=["POST"])
def mobile_login():
    try:

        
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No input data"
            }), 400

        teacher_id = str(data.get("teacher_id", "")).strip()
        password = str(data.get("password", "")).strip()

        print("MOBILE LOGIN:", teacher_id)

        
        if teacher_id == "" or password == "":
            return jsonify({
                "status": "error",
                "message": "Teacher ID and Password required"
            }), 400

    
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT teacher_id, full_name
            FROM teachers
            WHERE teacher_id = %s
            AND password = %s
            LIMIT 1
            """,
            (teacher_id, password)
        )

        teacher = cursor.fetchone()

        cursor.close()
        conn.close()

        if teacher:
            print("LOGIN SUCCESS:", teacher["teacher_id"])

            return jsonify({
                "status": "success",
                "teacher_id": teacher["teacher_id"],
                "teacher_name": teacher["full_name"]
            }), 200

        print("INVALID LOGIN:", teacher_id)

        return jsonify({
            "status": "error",
            "message": "Invalid Teacher ID or Password"
        }), 401

    except Exception as e:
        print("LOGIN ERROR:", str(e))

        return jsonify({
            "status": "error",
            "message": "Server error"
        }), 500


# ==============================
# GET TEACHER SUBJECT + SECTIONS
# ==============================
@teacher_bp.route("/api/teacher-subject/<teacher_id>")
def get_teacher_subject(teacher_id):

    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    print("FETCH SUBJECT + REAL SECTION:", teacher_id)

   
    cursor.execute("""
        SELECT subject, full_name
        FROM teachers
        WHERE teacher_id = %s
    """, (teacher_id,))

    teacher = cursor.fetchone()

    
    if not teacher:
        cursor.close()
        conn.close()
        return jsonify([])

    subject = teacher["subject"]

 
    cursor.execute("""
        SELECT DISTINCT section
        FROM students
        ORDER BY section ASC
    """)

    sections = cursor.fetchall()

    cursor.close()
    conn.close()

    result = []

    
    for sec in sections:
        result.append({
            "subject_name": subject,
            "teacher_name": teacher["full_name"],
            "section": sec["section"]
        })

    return jsonify(result)