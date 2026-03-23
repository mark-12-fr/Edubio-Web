import random
import re


# ==============================
# GENERATE OTP
# ==============================
def generate_otp():
    return str(random.randint(100000, 999999))


# ==============================
# EMAIL VALIDATION
# ==============================
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)


# ==============================
# PASSWORD STRENGTH CHECK
# ==============================
def is_strong_password(password):
    return (
        len(password) >= 8 and       
        re.search(r"[A-Z]", password) and  
        re.search(r"[a-z]", password) and  
        re.search(r"\d", password)       
    )


# ==============================
# GENERATE TEACHER ID
# ==============================
def generate_teacher_id():
    return f"TCH{random.randint(100000, 999999)}"