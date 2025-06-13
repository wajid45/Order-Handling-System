import mysql.connector
from datetime import datetime
from flask import g

DATABASE_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "order_db"
}

def get_connection():
    if 'db' not in g:
        g.db = mysql.connector.connect(**DATABASE_CONFIG)
    return g.db

def log_action(action, user="System"):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (action, performed_by, timestamp) VALUES (%s, %s, %s)",
                   (action, user, timestamp))
    conn.commit()
    # The connection will be closed by close_db

def init_app_db(app):
    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()