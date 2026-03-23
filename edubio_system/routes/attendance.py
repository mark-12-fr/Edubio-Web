from flask import Blueprint, jsonify, request
from services.database import get_db
from services.extensions import socketio
from datetime import datetime, time

attendance_bp = Blueprint("attendance", __name__)

# ==============================
# AUTO RESET FUNCTION
# ==============================
def auto_reset_attendance(subject):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE attendance
            SET status = NULL,
                time_in = NULL
            WHERE subject = %s
            AND date = CURDATE()
        """, (subject,))
        conn.commit()
        print(f"AUTO RESET DONE for subject: {subject}")
    except Exception as e:
        print("AUTO RESET ERROR:", e)
    finally:
        cursor.close()
        conn.close()


# ==============================
# RELAY ATTENDANCE FROM MOBILE → PYTHON BRIDGE
# ==============================
@socketio.on("start_attendance")
def relay_attendance(data):
    try:
        now = datetime.now().time()
        # FIX: Maximum is 23:59:59 para indi mag-error ang Python
        cutoff = time(23, 59, 59) 

        if now > cutoff:
            print(">>> Attendance CLOSED")
            socketio.emit("attendance_closed")
            return

        print(">>> Relay attendance event - Python bridge started")
        socketio.emit("start_attendance", data)
    except Exception as e:
        print(">>> Error in relay_attendance:", e)


# ==============================
# FINGERPRINT MATCH RECEIVED
# ==============================
@socketio.on("attendance_match")
def attendance_match(data):
    fingerprint_id = int(data.get("fingerprint_id"))
    subject = data.get("subject")

    conn = None
    cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # 1. Check kon existing ang student
        cursor.execute("""
            SELECT student_id, full_name
            FROM students
            WHERE fingerprint_id = %s
        """, (fingerprint_id,))
        student = cursor.fetchone()

        if not student:
            print(f">>> Fingerprint {fingerprint_id} not found.")
            socketio.emit("attendance_not_found")
            return

        now = datetime.now()
        current_time = now.time()
        current_date = now.strftime("%B %d, %Y")
        current_time_str = now.strftime("%I:%M %p")

        # ==============================
        #  DYNAMIC STATUS RULES (TESTING)
        # ==============================
        start = time(7, 55)        
        late = time(7, 56)         

        if current_time <= start:
            status = "Present"
        elif current_time <= late:
            status = "Late"
        else:
            status = "Absent"

        # ==============================
        #  DATABASE UPDATE/INSERT
        # ==============================
        cursor.execute("""
            SELECT id FROM attendance
            WHERE student_id=%s AND subject=%s AND date=CURDATE()
        """, (student["student_id"], subject))

        existing = cursor.fetchone()
        time_now_sql = now.strftime("%H:%M:%S")

        if existing:
            cursor.execute("""
                UPDATE attendance SET status=%s, time_in=%s
                WHERE id=%s
            """, (status, time_now_sql, existing["id"]))
        else:
            cursor.execute("""
                INSERT INTO attendance (student_id, subject, date, status, time_in)
                VALUES (%s, %s, CURDATE(), %s, %s)
            """, (student["student_id"], subject, status, time_now_sql))

        conn.commit()

        # ===================================================
        # SOCKET EMITS
        # ===================================================
        socketio.emit("attendance_update", {
            "student_id": student["student_id"],
            "full_name": student["full_name"],
            "status": status,
            "time": current_time_str,
            "date": current_date
        })

        socketio.emit("attendance_match_result", {
            "name": student["full_name"],
            "status": status,
            "time": current_time_str
        })

        print(f">>> Success: {student['full_name']} marked as {status}")

    except Exception as e:
        print(">>> Attendance error:", e)
        
    finally:
        # Diri ang plastar nga indentation para indi mag-pula:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ==============================
# REALTIME LIST FOR MOBILE
# ==============================
@attendance_bp.route("/api/realtime-attendance")
def realtime_attendance():

    subject = request.args.get("subject")

    if not subject:
        return jsonify([])

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
        s.id,
        s.full_name,
        s.student_id,
        s.section,
        IFNULL(a.status,'') AS status,
        CASE 
        WHEN a.time_in IS NOT NULL 
        THEN CONCAT(a.date,' ',a.time_in)
        ELSE NULL
        END AS time_in
        FROM students s
        LEFT JOIN attendance a
        ON s.student_id = a.student_id
        AND a.subject = %s
        AND a.date = CURDATE()
        ORDER BY s.full_name ASC
        """

    cursor.execute(query, (subject,))
    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(students)

# ==============================
# STOP ATTENDANCE (New Event)
# ==============================
@socketio.on("stop_attendance")
def stop_attendance():
    print("Stopping Attendance Mode...")
    
    socketio.emit("stop_scanning")
    
@attendance_bp.route('/api/attendance-history', methods=['GET'])
def get_history():
    try:
        query = """
            SELECT 
                a.id, 
                s.full_name, 
                a.status, 
                a.date, 
                a.time,
                sub.subject_name,
                s.section
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            JOIN subjects sub ON a.subject_id = sub.id
            ORDER BY a.date DESC, a.time DESC
        """
        
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        
        return jsonify(records)
        
    except Exception as e:
        print(f"Error sa History: {e}")
        return jsonify({"error": str(e)}), 500
    
@attendance_bp.route('/api/check-fingerprint', methods=['POST'])
def check_fingerprint():
    data = request.json
    student_id = data.get('student_id')
    subject = data.get('subject')
    today = datetime.now().strftime('%Y-%m-%d')

    cursor = get_db().cursor(dictionary=True)

   
    cursor.execute("""
        SELECT a.*, s.full_name 
        FROM attendance a 
        JOIN students s ON a.student_id = s.student_id 
        WHERE a.student_id = %s AND a.subject_name = %s AND a.date = %s
    """, (student_id, subject, today))
    
    existing = cursor.fetchone()

    if existing:
        socketio.emit('already_attended', {'full_name': existing['full_name']})
        return jsonify({"status": "already_recorded", "message": "Already Attendance"}), 200

    
    socketio.emit('attendance_update')
    return jsonify({"status": "success"}), 200