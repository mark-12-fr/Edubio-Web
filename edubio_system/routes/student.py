# Import Flask tools for routing, templates, JSON, session handling
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from utils.decorators import login_required
from services.student_service import (
    get_all_students,
    update_student,
    delete_student_by_id
)
from services.database import get_db



student_bp = Blueprint("student", __name__)


# ==============================
# STUDENT LIST PAGE
# ==============================
@student_bp.route("/stslist")
@login_required
def stslist():

  
    students = get_all_students()

    return render_template(
        "stslist.html",
        students=students,
        name=session.get("user_name")
    )


# ==============================
# EDIT STUDENT
# ==============================

@student_bp.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):

   
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students WHERE id=%s", (student_id,))
    student = cursor.fetchone()

    cursor.close()
    conn.close()

 
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("student.stslist"))

 
    if request.method == "POST":
        full_name = request.form.get("full_name")
        course = request.form.get("course")
        year_level = request.form.get("year_level")
        section = request.form.get("section")
        status = request.form.get("status")

 
        update_student(
            student_id,
            full_name,
            course,
            year_level,
            section,
            status
        )
        return redirect(url_for("student.stslist"))


    return render_template("edit_student.html", student=student)


# ==============================
# DELETE SINGLE STUDENT
# ==============================
@student_bp.route("/delete_student/<int:student_id>")
@login_required
def delete_student(student_id):
    try:
        delete_student_by_id(student_id)
    except Exception as e:
        print("DELETE STUDENT ERROR:", e)
        flash("Error deleting student.", "error")

    return redirect(url_for("student.stslist"))


# ==============================
# BULK DELETE STUDENTS
# ==============================

@student_bp.route("/delete_students_bulk", methods=["POST"])
@login_required
def delete_students_bulk():
    try:
        data = request.get_json()
        ids = data.get("ids", [])

      
        if not ids:
            return jsonify({"success": False})

      
        db = get_db()
        cursor = db.cursor()

        
        format_strings = ",".join(["%s"] * len(ids))

       
        cursor.execute(
            f"DELETE FROM students WHERE id IN ({format_strings})",
            ids
        )

        db.commit()
        cursor.close()
        db.close()

        return jsonify({"success": True})

    except Exception as e:
        print("BULK DELETE ERROR:", e)
        return jsonify({"success": False})


# ==============================
# DELETE ALL STUDENTS
# ==============================
@student_bp.route("/delete_all_students", methods=["POST"])
@login_required
def delete_all_students():
    try:

      
        db = get_db()
        cursor = db.cursor()

       
        cursor.execute("DELETE FROM students")

        db.commit()
        cursor.close()
        db.close()

        return jsonify({"success": True})

    except Exception as e:
        print("DELETE ALL ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Failed to delete all students."
        })


# ==============================
# API GET STUDENTS (FOR MOBILE / EXTERNAL)
# ==============================

@student_bp.route("/api/students", methods=["GET"])
def api_students():
    try:
        students = get_all_students()
        return jsonify(students)   
    except Exception as e:
        print("API STUDENTS ERROR:", e)
        return jsonify([])