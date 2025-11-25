import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt
from flask import render_template, redirect, url_for, flash, request
from project.forms import RegistrationForm, LoginForm

project_folder = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(project_folder, 'hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a_very_secret_key_change_this_later'

db = SQLAlchemy(app)
bcrypt=Bcrypt(app)

login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'





if __name__ == '__main__':
    app.run(debug=True)