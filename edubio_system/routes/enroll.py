from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify

from utils.decorators import login_required

from services.database import get_db

from flask import current_app

from services.extensions import socketio



enroll_bp = Blueprint("enroll", __name__)





@enroll_bp.route("/enrollform", methods=["GET", "POST"])

@login_required

def enrollform():

    if request.method == "POST":

        session["enroll_data"] = {

            "student_id": request.form.get("student_id"),

            "full_name": request.form.get("full_name"),

            "course": request.form.get("course"),

            "year_level": request.form.get("year_level"),

            "section": request.form.get("section"),

        }



        session["enrolling_student"] = request.form.get("full_name")

        return redirect(url_for("enroll.fingerprint_scan"))



    return render_template(

        "enrollform.html",

        name=session.get("user_name")

    )







@enroll_bp.route("/fingerprint_scan")

@login_required

def fingerprint_scan():

    if "enroll_data" not in session:

        return redirect(url_for("enroll.enrollform"))



    return render_template(

        "scanner.html",

        name=session.get("user_name")

    )







@enroll_bp.route("/start_scan")

@login_required

def start_scan():

    socketio.emit("start_scan", {})

    return jsonify({

        "success": True,

        "message": "Scanner triggered"

    })







@socketio.on("fingerprint_result")

def fingerprint_result(data):

    status = data.get("status")



    if status == "already_enrolled":

        fid = data.get("fingerprint_id")

        db = get_db()

        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT full_name FROM students WHERE fingerprint_id=%s", (fid,))

        student = cursor.fetchone()

        cursor.close()

        db.close()



        name = student["full_name"] if student else "Unknown Student"




        socketio.emit("already_enrolled_web", {"name": name})



        

        socketio.emit("duplicate_name", {"full_name": name}, broadcast=True)

        return


    if status == "ok":

        fid = data.get("fingerprint_id")



        session["fingerprint_ok"] = True

        session["fingerprint_id"] = fid



        current_app.config["LAST_FINGERPRINT_OK"] = True

        current_app.config["LAST_FINGERPRINT_ID"] = fid



    else:

        session["fingerprint_ok"] = False

        current_app.config["LAST_FINGERPRINT_OK"] = False



    socketio.emit("fingerprint_result", data)







@enroll_bp.route("/confirm_enroll", methods=["POST"])

@login_required

def confirm_enroll():

    try:

        finger_ok = session.get("fingerprint_ok") or current_app.config.get("LAST_FINGERPRINT_OK")



        if not finger_ok:

            return jsonify({

                "success": False,

                "message": "Fingerprint not captured."

            })



        data = session.get("enroll_data")

        fingerprint_id = session.get("fingerprint_id") or current_app.config.get("LAST_FINGERPRINT_ID")



        if not fingerprint_id:

            return jsonify({

                "success": False,

                "message": "Fingerprint ID missing."

            })



        if not data:

            return jsonify({

                "success": False,

                "message": "No enrollment data found."

            })



        db = get_db()

        cursor = db.cursor()



        cursor.execute("""

            INSERT INTO students

            (student_id, full_name, course, year_level, section, fingerprint_id, status)

            VALUES (%s,%s,%s,%s,%s,%s,%s)

        """, (

            data["student_id"],

            data["full_name"],

            data["course"],

            data["year_level"],

            data["section"],

            fingerprint_id,

            "Enrolled"

        ))



        db.commit()

        cursor.close()

        db.close()



        socketio.emit("display_name", {

            "name": data["full_name"]

        })


        session.pop("enroll_data", None)

        session.pop("enrolling_student", None)

        session.pop("fingerprint_ok", None)

        session.pop("fingerprint_id", None)



        current_app.config["LAST_FINGERPRINT_OK"] = False

        current_app.config["LAST_FINGERPRINT_ID"] = None



        return jsonify({

            "success": True,

            "message": "Enrollment saved successfully!"

        })



    except Exception as e:

        print("ENROLL SAVE ERROR:", e)

        return jsonify({

            "success": False,

            "message": "Database error during enrollment."

        })

       

@enroll_bp.route("/get_student_by_fid/<fid>")

@login_required

def get_student_by_fid(fid):

    db = get_db()

    cursor = db.cursor(dictionary=True)



    cursor.execute("SELECT full_name FROM students WHERE fingerprint_id=%s", (fid,))

    student = cursor.fetchone()



    cursor.close()

    db.close()



    if student:

        return jsonify({

        "found": True,

        "name": student["full_name"]

})



    return jsonify({"found": False})