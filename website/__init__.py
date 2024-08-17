from os import path
from flask import Flask
from .database import Database
# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import Users, session
from .utils import create_folder

app = Flask(__name__)

db = Database()
cursor = db.get_cursor()
DB_NAME = "database.db"

def create_app():
    app.config['SECRET_KEY'] = 'gulu gulu'
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    

    with open(r'D:\Python\Projects\Music-Catalog\website\schema.sql') as f:
        cursor.executescript(f.read())
    db.commit()

    from .views import views, UPLOAD_FOLDER
    from .auth import auth

    create_folder(UPLOAD_FOLDER)

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')

    #from .models import Users, Songs

    #create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        #cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        #user = cursor.fetchone()
        #fetch_user = session.query(Users).filter_by(user_id = user_id).first()
        #user = Users(user_id = fetch_user.user_id, email = fetch_user.email, 
        #             username = fetch_user.username, password = fetch_user.password)
        return (session.query(Users).get(str(user_id)))

    return app

#def create_database(app):
#    if not path.exists('website/database.db'):
#        with app.app_context():
#            db.create_all()