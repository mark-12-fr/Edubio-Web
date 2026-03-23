from flask import Flask, jsonify
from datetime import timedelta
from flask_cors import CORS
import os
from flask_dance.contrib.google import make_google_blueprint
from services.extensions import socketio


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"



app = Flask(__name__)
CORS(app)  


app.secret_key = "supersecretkey123"
app.permanent_session_lifetime = timedelta(hours=1)



socketio.init_app(app, cors_allowed_origins="*")

app.config["GOOGLE_OAUTH_CLIENT_ID"] = "CLIENT_ID"
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "CLIENT_SECRET"



google_bp = make_google_blueprint(
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    redirect_url="/google" 
)


app.register_blueprint(google_bp, url_prefix="/google_login")


@app.route("/api/test")
def test():
    print("React Native connected to Flask API!") 

    return jsonify({
        "status": "connected",
        "message": "Flask API is working!"
    })



from routes.auth import auth_bp
from routes.pages import pages_bp
from routes.enroll import enroll_bp
from routes.teacher import teacher_bp
from routes.student import student_bp
from routes.attendance import attendance_bp



app.register_blueprint(auth_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(enroll_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)
app.register_blueprint(attendance_bp)






@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")



if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",  
        port=5000,        
        debug=True,       
        use_reloader=False 
    )