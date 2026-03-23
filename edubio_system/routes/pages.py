from flask import Blueprint, render_template, session, redirect, url_for
from utils.decorators import login_required
from services.database import get_db



pages_bp = Blueprint("pages", __name__)


# ==============================
# ROOT ROUTE
# ==============================

@pages_bp.route("/")
def index():
    return redirect(url_for("pages.mainn"))


# ==============================
# PUBLIC ABOUT PAGE
# ==============================

@pages_bp.route("/aboutt")
def aboutt():
    return render_template("aboutt.html")


# ==============================
# PUBLIC HELP PAGE
# ==============================

@pages_bp.route("/helpp")
def helpp():
    return render_template("helpp.html")


# ==============================
# PUBLIC MAIN PAGE
# ==============================

@pages_bp.route("/mainn")
def mainn():
    return render_template(
        "mainn.html",
        name=session.get("user_name")
    )


# ==============================
# PRIVATE ABOUT PAGE
# ==============================

@pages_bp.route("/about")
@login_required
def about():
    return render_template("about.html")


# ==============================
# PRIVATE HELP PAGE
# ==============================

@pages_bp.route("/help")
@login_required
def help():
    return render_template("help.html")


# ==============================
# PRIVATE MAIN DASHBOARD
# ==============================

@pages_bp.route("/main")
@login_required
def main():

    
    conn = get_db()
    cur = conn.cursor()

    
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    
    cur.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cur.fetchone()[0]

    cur.close()
    conn.close()


    return render_template(
        "main.html",
        name=session.get("user_name"),
        total_students=total_students,
        total_teachers=total_teachers
    )