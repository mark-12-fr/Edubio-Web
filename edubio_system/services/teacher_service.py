from services.database import get_db


# ==============================
# CREATE TEACHER
# ==============================
def create_teacher(teacher_id, full_name, email, subject, password):

  
    db = get_db()
    cursor = db.cursor()


    cursor.execute("""
        INSERT INTO teachers
        (teacher_id, full_name, email, subject, password, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (teacher_id, full_name, email, subject, password, "Active"))

    db.commit()
    cursor.close()
    db.close()


# ==============================
# GET ALL TEACHERS
# ==============================
def get_all_teachers():

 
    db = get_db()
    cursor = db.cursor(dictionary=True)

   
    cursor.execute("SELECT * FROM teachers")
    teachers = cursor.fetchall()

    cursor.close()
    db.close()

    return teachers


# ==============================
# DELETE TEACHER
# ==============================
def delete_teacher_by_id(teacher_id):

   
    db = get_db()
    cursor = db.cursor()

   
    cursor.execute(
        "DELETE FROM teachers WHERE teacher_id=%s",
        (teacher_id,)
    )

    db.commit()
    cursor.close()
    db.close()


# ==============================
# UPDATE TEACHER
# ==============================
def update_teacher(teacher_id, full_name, email, subject, status):

 
    db = get_db()
    cursor = db.cursor()

 
    cursor.execute("""
        UPDATE teachers
        SET full_name=%s,
            email=%s,
            subject=%s,
            status=%s
        WHERE teacher_id=%s
    """, (full_name, email, subject, status, teacher_id))

    db.commit()
    cursor.close()
    db.close()