import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    password_hash=db.Column(db.String(100),nullable=False)
    role=db.Column(db.String(20),nullable=False)
    def set_password(self,password):
        self.password_hash=bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self,password):
        return bcrypt.check_password_hash(self.password_hash,password)

class Department(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),unique=True, nullable=False)
    doctors=db.relationship('Doctor',backref='department',lazy=True)

class Doctor(db.Model):
    doctor_id=db.Column(db.Integer,primary_key=True)
    doctor_name=db.Column(db.String(100),nullable=False)
    specialization=db.Column(db.String(100),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),unique=True,nullable=False)
    department_id=db.Column(db.Integer,db.ForeignKey('department.id'),nullable=False)
    appointments=db.relationship('Appointment',backref='doctor',lazy=True)


    
class Patient(db.Model):
    patient_id=db.Column(db.Integer,primary_key=True)
    patient_name=db.Column(db.String(100),nullable=False)
    patient_age=db.Column(db.Integer,nullable=False)
    patient_gender=db.Column(db.String(20),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),unique=True,nullable=False)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Appointment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.String(20),nullable=False)
    time=db.Column(db.String(20),nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Booked')
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    doctor_id=db.Column(db.Integer,db.ForeignKey('doctor.doctor_id'),nullable=False)
    treatment = db.relationship('Treatment', backref='appointment', uselist=False, lazy=True)

class Treatment(db.Model):
    treatment_id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), unique=True, nullable=False)


    







@app.route('/')
def index():
    return "Hello, your Hospital Management Server is running!"





if __name__ == '__main__':
    app.run(debug=True)