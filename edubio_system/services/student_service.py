from services.database import get_db


# ==============================
# GET ALL STUDENTS
# ==============================
def get_all_students():

   
    db = get_db()
    cursor = db.cursor(dictionary=True)

    
    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    students = cursor.fetchall()

    cursor.close()
    db.close()

    return students


# ==============================
# DELETE STUDENT BY ID
# ==============================
def delete_student_by_id(student_id):

   
    db = get_db()
    cursor = db.cursor()

   
    cursor.execute(
        "DELETE FROM students WHERE id=%s",
        (student_id,)
    )

    db.commit()
    cursor.close()
    db.close()


# ==============================
# UPDATE STUDENT INFO
# ==============================
def update_student(student_id, full_name, course, year_level, section, status):

  
    db = get_db()
    cursor = db.cursor()

  
    cursor.execute("""
        UPDATE students
        SET full_name=%s,
            course=%s,
            year_level=%s,
            section=%s,
            status=%s
        WHERE id=%s
    """, (full_name, course, year_level, section, status, student_id))

    db.commit()
    cursor.close()
    db.close()