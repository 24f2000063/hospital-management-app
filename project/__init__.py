import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

login_manager.login_view = 'main.login' 
login_manager.login_message_category = 'info'


def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    app.config['SECRET_KEY'] = 'a_very_secret_key_change_this_later_987'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'hospital.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .models import User 

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main_routes 
    
    app.register_blueprint(main_routes)

    return app

