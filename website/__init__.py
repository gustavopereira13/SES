from flask import Flask
from flask_login import LoginManager
from .models import get_user
from .models import db
from os import path

DB_NAME = "database.db"
UPLOAD_FOLDER = 'C:/Users/gusta/PycharmProjects/Server/files'
app = Flask(__name__)


def create_app():
    app.config['SECRET_KEY'] = 'shavkbjlnkjsl'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    from .views import views
    from .auth import auth
    from .models import User, File
    db.init_app(app)

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
