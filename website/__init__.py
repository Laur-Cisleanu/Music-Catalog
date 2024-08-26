from os import path
from flask import Flask
from .database import Database
from flask_login import LoginManager
from .models import Users, session
from .utils import create_folder

app = Flask(__name__)

db = Database()
cursor = db.get_cursor()


def create_app():
    app.config['SECRET_KEY'] = 'gulu gulu'

    with open(r'D:\Python\Projects\Music-Catalog\website\schema.sql') as f:
        cursor.executescript(f.read())
    db.commit()

    from .views import views, UPLOAD_FOLDER
    from .auth import auth

    create_folder(UPLOAD_FOLDER)

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return (session.query(Users).get(str(user_id)))

    return app