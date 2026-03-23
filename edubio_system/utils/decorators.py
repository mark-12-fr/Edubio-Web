from functools import wraps
from flask import session, redirect, url_for, flash


# ==============================
# LOGIN REQUIRED DECORATOR
# ==============================
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        
        if "user_id" not in session:

        
            flash("Please login first.", "error")

           
            return redirect(url_for("auth.login"))

       
        return f(*args, **kwargs)

    return decorated_function