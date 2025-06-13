from flask import Flask
from routes import main_routes
from db import init_app_db

app = Flask(__name__)

init_app_db(app)

app.register_blueprint(main_routes)

if __name__ == '__main__':
    app.run(debug=True)
