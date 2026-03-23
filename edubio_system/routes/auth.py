from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_dance.contrib.google import google
from services.database import get_db



auth_bp = Blueprint("auth", __name__)


# ==============================
# SIGNUP ROUTE
# ==============================
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm = request.form.get('confirm_password')

           
            if email:
                email = email.lower().strip()

            
            if not full_name or not email or not password:
                flash("All fields required.", "error")
                return redirect(url_for('auth.signup'))

            
            if password != confirm:
                flash("Passwords do not match.", "error")
                return redirect(url_for('auth.signup'))

            
            db = get_db()
            cursor = db.cursor(dictionary=True)

           
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                flash("Email already registered.", "error")
                cursor.close()
                db.close()
                return redirect(url_for('auth.signup'))

           
            hashed = generate_password_hash(password)

            
            cursor.execute("""
                INSERT INTO users (full_name, email, password, is_verified)
                VALUES (%s, %s, %s, %s)
            """, (full_name, email, hashed, 1))

            db.commit()

            
            session['user_id'] = cursor.lastrowid
            session['user_name'] = full_name
            session.permanent = True

            cursor.close()
            db.close()

            flash("Signup successful!", "success")
            return redirect(url_for('pages.main'))

        except Exception as e:
            print("SIGNUP ERROR:", e)
            flash("Database error during signup.", "error")
            return redirect(url_for('auth.signup'))

    
    return render_template('sign.html')


# ==============================
# LOGIN ROUTE
# ==============================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:

            email = request.form.get('email', '').lower().strip()
            password = request.form.get('password', '')

            
            if not email or not password:
                flash("Please enter both email and password.", "error")
                return redirect(url_for('auth.login'))

            
            db = get_db()
            cursor = db.cursor(dictionary=True)

            
            cursor.execute(
                "SELECT id, full_name, password FROM users WHERE email=%s",
                (email,)
            )
            user = cursor.fetchone()

            cursor.close()
            db.close()

            
            if not user or not check_password_hash(user['password'], password):
                flash("Invalid login credentials.", "error")
                return redirect(url_for('auth.login'))

            
            session['user_id'] = user["id"]
            session['user_name'] = user["full_name"]
            session.permanent = True

            flash("Login successful. Welcome back!", "success")
            return redirect(url_for('pages.main'))

        except Exception as e:
            print("LOGIN ERROR:", e)
            flash("System error during login.", "error")
            return redirect(url_for('auth.login'))

   
    return render_template('login.html')


# ==============================
# GOOGLE OAUTH CALLBACK
# ==============================

@auth_bp.route("/google")
def google_login_callback():

    if not google.authorized:
        return redirect(url_for("google.login"))

    try:
        
        resp = google.get("/oauth2/v2/userinfo")

        if not resp.ok:
            flash("Google login failed.", "error")
            return redirect(url_for("auth.login"))

        info = resp.json()

        email = info.get("email")
        name = info.get("name")
        picture = info.get("picture")

        
        db = get_db()
        cursor = db.cursor(dictionary=True)

      
        cursor.execute(
            "SELECT id FROM users WHERE email=%s",
            (email,)
        )
        user = cursor.fetchone()

        
        if not user:
            cursor.execute("""
                INSERT INTO users (full_name, email, password, is_verified)
                VALUES (%s, %s, %s, %s)
            """, (
                name,
                email,
                generate_password_hash("google_oauth_user"),
                1
            ))
            db.commit()
            user_id = cursor.lastrowid
            user_name = name
        else:
            user_id = user["id"]
            user_name = name

        
        session["user_id"] = user_id
        session["user_name"] = user_name
        session["user_picture"] = picture
        session.permanent = True

        cursor.close()
        db.close()

        return redirect(url_for("pages.main"))

    except Exception as e:
        print("GOOGLE ERROR:", e)
        flash("Google authentication error.", "error")
        return redirect(url_for("auth.login"))


# ==============================
# LOGOUT ROUTE
# ==============================
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))