import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt
from flask import render_template, redirect, url_for, flash, request
from forms import RegistrationForm, LoginForm

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
@login_required  # Protect the base URL
def index():
    # This route is now a "gatekeeper" that redirects based on role
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    elif current_user.role == 'patient':
        return redirect(url_for('patient_dashboard'))
    else:
        # Just in case, log them out
        logout_user()
        flash('An error occurred. Please log in again.', 'danger')
        return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form=RegistrationForm()

    if form.validate_on_submit():
        
        existing_user=User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('This username is already taken. Please Try with Different One','danger')
            return render_template('register.html', title='Register', form=form)
        
        new_user=User(
            username=form.username.data,
            role='patient'
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', title='Register', form=form)
    
@app.route('/login',methods=['GET','POST'])
def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form=LoginForm()

        if form.validate_on_submit():
            user=User.query.filter_by(username=form.username.data()).first()

            if user and user.check_password(form.password.data):
                login_user(user)

                next_url=request.args.get('next')
                
                if next_url:
                    return redirect(url_for(next_url))
                else:
                    redirect(url_for('index'))

            else:
                flash('Login Unsuccessful. Please check username and password.', 'danger')

        return render_template('login.html', title='Login', form=form)
            
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))           


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role!= 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    return f'Hello, Admin {current_user.username}'

@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
        
    return f'Hello, Doctor {current_user.username}' # Placeholder

@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
        
    return f'Hello, Patient {current_user.username}'


if __name__ == '__main__':
    app.run(debug=True)