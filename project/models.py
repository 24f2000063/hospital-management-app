from project import db, bcrypt
from flask_login import UserMixin


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    password_hash=db.Column(db.String(100),nullable=False)
    role=db.Column(db.String(20),nullable=False)
    def set_password(self,password):
        self.password_hash=bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self,password):
        return bcrypt.check_password_hash(self.password_hash,password)
    doctor = db.relationship('Doctor', backref='user_account', uselist=False, lazy=True)
    patient = db.relationship('Patient', backref='user_account', uselist=False, lazy=True)

class Department(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),unique=True, nullable=False)
    doctors=db.relationship('Doctor',backref='department',lazy=True)

class Doctor(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    specialization=db.Column(db.String(100),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),unique=True,nullable=False)
    department_id=db.Column(db.Integer,db.ForeignKey('department.id'),nullable=False)
    appointments=db.relationship('Appointment',backref='doctor',lazy=True)


    
class Patient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    age=db.Column(db.Integer)
    gender=db.Column(db.String(20))
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),unique=True,nullable=False)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Appointment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.String(20),nullable=False)
    time=db.Column(db.String(20),nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Booked')
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id=db.Column(db.Integer,db.ForeignKey('doctor.id'),nullable=False)
    treatment = db.relationship('Treatment', backref='appointment', uselist=False, lazy=True)

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), unique=True, nullable=False)