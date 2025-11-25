
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from project import db, bcrypt
from project.models import User, Patient, Doctor, Appointment, Treatment, Department
from project.forms import RegistrationForm, LoginForm, AddDoctorForm,UpdateDoctorForm,TreatmentForm
from sqlalchemy.orm import joinedload
from project.forms import BookAppointmentForm



main_routes = Blueprint('main', __name__)



@main_routes.route('/')
@main_routes.route('/index')
@login_required  # Protect the base URL
def index():
    
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif current_user.role == 'doctor':
        return redirect(url_for('main.doctor_dashboard'))
    elif current_user.role == 'patient':
        return redirect(url_for('main.patient_dashboard'))
    else:
        logout_user()
        flash('An error occurred. Please log in again.', 'danger')
        return redirect(url_for('main.login'))



@main_routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()


    if form.validate_on_submit():
        
        
        new_user = User(
            username=form.username.data,
            role='patient'

        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        
        
        new_patient = Patient(
            name=form.name.data,
            user_id=new_user.id,
            age=form.age.data,     
            gender=form.gender.data 
        )
        db.session.add(new_patient)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', title='Register', form=form)

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            
            
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')

    return render_template('login.html', title='Login', form=form)

@main_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))



@main_routes.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    
    doc_count = Doctor.query.count()
    pat_count = Patient.query.count()
    appt_count = Appointment.query.count()
    
    return render_template('admin/dashboard.html', title='Admin Dashboard',
                           doc_count=doc_count, pat_count=pat_count, appt_count=appt_count)

@main_routes.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    doctor = current_user.doctor

    upcoming_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        status='Booked'
    ).order_by(Appointment.date.asc(), Appointment.time.asc()).all()

    return render_template('doctor/dashboard.html', 
                           title='Doctor Dashboard',
                           upcoming_appointments=upcoming_appointments)
        
    

@main_routes.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    patient = current_user.patient

    upcoming_appointments =Appointment.query.filter_by(
        patient_id=patient.id,
        status='Booked').order_by(Appointment.date.asc(),Appointment.time.asc()).all()
    
    past_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status.in_(['Completed', 'Cancelled']) 
    ).order_by(Appointment.date.desc()).all()

        
    return render_template('patient/dashboard.html', 
                           title='Patient Dashboard',
                           upcoming_appointments=upcoming_appointments,
                           past_appointments=past_appointments)

@main_routes.route('/admin/add_doctor',methods=['GET','POST'])
@login_required
def add_doctor():
    if current_user.role != 'admin':
        flash("You don't have access to this page","danger")
        return redirect(url_for('main.index'))
    form=AddDoctorForm()

    if form.validate_on_submit():
        new_user= User(
            username=form.username.data,
            role='doctor'
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        new_doctor= Doctor(
            name=form.name.data,
            specialization=form.specialization.data,
            department_id=form.department.data,
            user_id=new_user.id
        )
        db.session.add(new_doctor)
        db.session.commit()

        flash(f'Doctor {form.name.data} Account is Created ','success')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('admin/add_doctor.html',title="Add New Doctor",form=form)

@main_routes.route('/admin/manage_doctors')
@login_required
def manage_doctors():
    if current_user.role!='admin':
        flash('You are not permitted to view this page.','danger')
        return redirect(url_for('main.index'))
    all_doctors=Doctor.query.order_by(Doctor.id).all()
    return render_template('admin/manage_doctors.html',title='Manage Doctors',doctors_list=all_doctors)

@main_routes.route('/admin/delete_doctor/<int:doctor_id>',methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    if current_user.role!='admin':
        flash("You don't have access to this page","danger")
        return redirect(url_for('main.index'))
    doctor_to_delete=Doctor.query.get_or_404(doctor_id)
    user_to_delete=User.query.get_or_404(doctor_to_delete.user_id)

    try:
        Appointment.query.filter_by(doctor_id=doctor_to_delete.id).delete()
        db.session.delete(doctor_to_delete)

        if user_to_delete:
            db.session.delete(user_to_delete)
        db.session.commit()

        flash(f'Doctor {doctor_to_delete.name} and his account Deleted Successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Some Error Occured While Deleting: {e}', 'danger')

    return redirect(url_for('main.manage_doctors'))

@main_routes.route('/admin/edit_doctor/<int:doctor_id>',methods=['GET','POST'])
@login_required
def edit_doctor(doctor_id):
    if current_user.role!= 'admin':
        flash("You don't have access to this page","danger")
        return redirect(url_for('main.index'))
    doctor_to_edit = Doctor.query.get_or_404(doctor_id)
    form = UpdateDoctorForm(original_username=doctor_to_edit.user_account.username)

    if form.validate_on_submit():
        doctor_to_edit.user_account.username = form.username.data
        doctor_to_edit.name = form.name.data
        doctor_to_edit.specialization = form.specialization.data
        doctor_to_edit.department_id = form.department.data
    
        db.session.commit()
        flash(f'Doctor {doctor_to_edit.name} Profile is Updated Successfully!', 'success')
        return redirect(url_for('main.manage_doctors'))
    elif request.method=='GET':
        form.name.data = doctor_to_edit.name
        form.specialization.data = doctor_to_edit.specialization
        form.department.data = doctor_to_edit.department_id
        form.username.data = doctor_to_edit.user_account.username

    return render_template('admin/edit_doctor.html', 
                           title=f'Edit {doctor_to_edit.name}', 
                           form=form,
                           doctor_id=doctor_to_edit.id)

@main_routes.route('/admin/manage_appointments')
@login_required
def manage_appointments():
    if current_user.role != 'admin':
        flash('You are not permited to view this page','danger')
        return redirect(url_for('main.index'))
    all_appointments = Appointment.query \
        .options(joinedload(Appointment.patient),joinedload(Appointment.doctor).joinedload(Doctor.department))\
        .order_by(Appointment.date.desc(),Appointment.time.desc()).all()
    return render_template('admin/manage_appointments.html', 
        title='Manage Appointments', 
        all_appointments=all_appointments)

@main_routes.route('/patient/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if current_user.role != 'patient':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    form = BookAppointmentForm()
    if form.validate_on_submit():
        doctor_id=form.doctor.data
        if doctor_id==-1:
            flash('Please select a valid doctor.', 'danger')
            return render_template('patient/book_appointment.html', form=form)
        existing_appt=Appointment.query.filter_by(
        doctor_id=doctor_id,
        date=str(form.date.data),
        time=str(form.time.data)).first()
        if existing_appt:
            flash('This doctor is already booked at this time. Please choose another slot.', 'danger')
            return render_template('patient/book_appointment.html', form=form)
        new_appointment = Appointment(
            patient_id=current_user.patient.id, 
            doctor_id=doctor_id,
            date=str(form.date.data),
            time=str(form.time.data),
            status='Booked'
        )
        db.session.add(new_appointment)
        db.session.commit()
        
        flash('Your appointment has been booked successfully!', 'success')
        return redirect(url_for('main.patient_dashboard'))
    return render_template('patient/book_appointment.html', title='Book Appointment', form=form)

@main_routes.route('/patient/cancel_appointment/<int:appt_id>', methods=['POST'])
@login_required
def cancel_appointment(appt_id):
    if current_user.role != 'patient':
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.index'))
    

    appt = Appointment.query.get_or_404(appt_id)
    

    if appt.patient_id != current_user.patient.id:
        flash('You cannot cancel someone else\'s appointment!', 'danger')
        return redirect(url_for('main.patient_dashboard'))
    
    
    if appt.status != 'Cancelled':
        appt.status = 'Cancelled'
        db.session.commit()
        flash('Appointment cancelled successfully.', 'success')
    else:
        flash('This appointment is already cancelled.', 'info')
        
    return redirect(url_for('main.patient_dashboard'))

@main_routes.route('/doctor/treat_patient/<int:appt_id>', methods=['GET', 'POST'])
@login_required
def treat_patient(appt_id):
    if current_user.role != 'doctor':
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.index'))
    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != current_user.doctor.id:
        flash('You cannot treat a patient not assigned to you.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    
    form = TreatmentForm()
    if form.validate_on_submit():
        treatment = Treatment(
            diagnosis=form.diagnosis.data,
            prescription=form.prescription.data,
            notes=form.notes.data,
            appointment_id=appt.id
        )
        db.session.add(treatment)

        appt.status = 'Completed'
        
        db.session.commit()

        flash('Patient treated successfully!', 'success')
        return redirect(url_for('main.doctor_dashboard'))
    
    return render_template('doctor/treat_patient.html', 
                           title='Treat Patient', 
                           form=form, 
                           appt=appt)

    
    




    
    
    














