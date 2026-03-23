import mysql.connector


# ==============================
# DATABASE CONNECTION FUNCTION
# ==============================
def get_db():

    return mysql.connector.connect(
        host="localhost",        
        user="flaskuser",       
        password="flask123",     
        database="enrollment_db",
        autocommit=False         
    )