from services.database import get_db
from werkzeug.security import generate_password_hash, check_password_hash


# ==============================
# CREATE USER FUNCTION
# ==============================
def create_user(full_name, email, password):

    
    db = get_db()
    cursor = db.cursor(dictionary=True)

  
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        cursor.close(); db.close()
        return False, "Email already registered."

    
    hashed = generate_password_hash(password)

    
    cursor.execute("""
        INSERT INTO users (full_name, email, password, is_verified)
        VALUES (%s, %s, %s, %s)
    """, (full_name, email, hashed, 1))

    db.commit()
    user_id = cursor.lastrowid

    cursor.close()
    db.close()

   
    return True, user_id


# ==============================
# AUTHENTICATE USER FUNCTION
# ==============================
def authenticate_user(email, password):


    db = get_db()
    cursor = db.cursor(dictionary=True)

  
    cursor.execute(
        "SELECT id, full_name, password FROM users WHERE email=%s",
        (email,)
    )
    user = cursor.fetchone()

    cursor.close()
    db.close()

   
    if not user:
        return False, "Invalid credentials"

   
    if not check_password_hash(user["password"], password):
        return False, "Invalid credentials"

   
    return True, user