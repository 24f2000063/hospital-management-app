
from flask import render_template, redirect, url_for, flash, request, Blueprint,jsonify
from flask_login import login_user, logout_user, current_user, login_required
from project import db, bcrypt
from project.models import User, Patient, Doctor, Appointment, Treatment, Department,Availability
from project.forms import RegistrationForm, LoginForm, AddDoctorForm,UpdateDoctorForm,TreatmentForm,EditPatientProfileForm,BookAppointmentForm,SearchDoctorForm,AvailabilityForm
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from datetime import datetime, timedelta



main_routes = Blueprint('main', __name__)



@main_routes.route('/')
@main_routes.route('/index')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('main.doctor_dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('main.patient_dashboard'))
        else:
            
            logout_user()
            return redirect(url_for('main.login'))
    
    
    return render_template('home.html')


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

@main_routes.route('/admin/manage_patients',methods=['GET'])
@login_required
def manage_patients():
    if current_user.role!='admin':
        flash('You do not have permission to access this page','danger')
        return redirect(url_for('main.index'))
    
    query_string=request.args.get('search_query',default='',type=str)

    query=Patient.query.options(joinedload(Patient.user_account))

    if query_string:
        search_term= f"%{query_string}%"
        query=query.join(Patient.user_account).filter(
            or_(
                Patient.name.ilike(search_term),
                User.username.ilike(search_term)
            )
        )
    all_patients=query.order_by(Patient.id).all()

    return render_template('admin/manage_patients.html',
                           title='Manage Patients',
                           all_patients=all_patients,
                           search_query=query_string)

    

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
        .order_by(Appointment.id.asc()).all()
    return render_template('admin/manage_appointments.html', 
        title='Manage Appointments', 
        all_appointments=all_appointments)

@main_routes.route('/patient/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if current_user.role != 'patient':
        return redirect(url_for('main.index'))
    
    form = BookAppointmentForm()
    
    if request.method == 'POST':
        
        slot_id = form.time_slot.data
        
        slot = Availability.query.get(slot_id)
        
        if not slot:
            flash('Invalid slot selected.', 'danger')
        elif slot.is_booked:
            flash('This slot has already been booked.', 'danger')
        else:
      
            new_appt = Appointment(
                patient_id=current_user.patient.id, 
                doctor_id=slot.doctor_id, 
                date=slot.date, 
                time=slot.start_time, 
                status='Booked'
            )
            slot.is_booked = True
            db.session.add(new_appt)
            db.session.commit()
            flash('Appointment booked successfully!', 'success')
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
    
    
    if appt.status=='Booked':
        appt.status = 'Cancelled'

        slot = Availability.query.filter_by(
            doctor_id=appt.doctor_id,
            date=appt.date,
            start_time=appt.time
        ).first()

        if slot:
            slot.is_booked=False
        
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


@main_routes.route('/patient/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    
    if current_user.role != 'patient':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    form = EditPatientProfileForm()
    patient = current_user.patient 
    
   
    if form.validate_on_submit():
        patient.name = form.name.data
        patient.age = form.age.data
        patient.gender = form.gender.data
        
        db.session.commit()
        
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.patient_dashboard'))
    
  
    elif request.method == 'GET':
        form.name.data = patient.name
        form.age.data = patient.age
        form.gender.data = patient.gender
        
    return render_template('patient/edit_profile.html', title='Edit Profile', form=form)   
    
@main_routes.route('/patient/search_doctor',methods=['GET','POST'])
@login_required
def search_doctor():
    if current_user.role!='patient':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    form=SearchDoctorForm()
    doctors=[]
    if form.validate_on_submit():
        search_by=form.search_by.data
        term=form.search_term.data

        if search_by=='name':
            doctors=Doctor.query.filter(Doctor.name.ilike(f'%{term}%')).all()
        elif search_by=='specialization':
            doctors=Doctor.query.filter(Doctor.specialization.ilike(f'%{term}%')).all()
        if not doctors:
            flash('No doctors found matching your search.', 'info')
    
    elif request.method=='GET':
        doctors=Doctor.query.all()
    
    return render_template('patient/search_doctor.html',title='Search Doctor',form=form,doctors=doctors)

@main_routes.route('/doctor/manage_availability', methods=['GET', 'POST'])
@login_required
def manage_availability():

    if current_user.role != 'doctor':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    form = AvailabilityForm()
    doctor = current_user.doctor

  
    if form.validate_on_submit():
        selected_date=form.date.data
        selected_slots=form.slots.data

        count=0
        for start_time in selected_slots:
            start_dt=datetime.strptime(start_time,"%I:%M %p")
            end_dt=start_dt+timedelta(minutes=30)
            end_time_str = end_dt.strftime("%I:%M %p")

            existing = Availability.query.filter_by(
                doctor_id=doctor.id,
                date=selected_date,
                start_time=start_time
            ).first()

            if not existing:
                new_slot = Availability(
                    doctor_id=doctor.id,
                    date=selected_date,
                    start_time=start_time,
                    end_time=end_time_str
                )
                db.session.add(new_slot)
                count += 1
            db.session.commit()

        if count > 0:
            flash(f'{count} slots added successfully for {selected_date}!', 'success')
        else:
            flash('No new slots added', 'warning')
            
        return redirect(url_for('main.manage_availability'))
    
    raw_slot = Availability.query.filter_by(doctor_id=doctor.id).all()
    my_slots=sorted(raw_slot,key=lambda x:(
        x.date,
        datetime.strptime(x.start_time,"%I:%M %p")
    ))

    return render_template('doctor/manage_availability.html', 
                           title='Manage Availability', 
                           form=form, 
                           my_slots=my_slots)

@main_routes.route('/doctor/delete_availability/<int:slot_id>',methods=['POST'])
@login_required
def delete_availability(slot_id):
    if current_user.role!='doctor':
        flash('Access Denied','danger')
        return redirect(url_for('main.index'))
    slot=Availability.query.get_or_404(slot_id)

    if slot.doctor_id!=current_user.doctor.id:
        flash('You Cannot delete this slot','danger')
        return redirect(url_for('main.manage_availability'))
    
    if slot.is_booked:
        flash('Cannot delete a book slot')
        return redirect(url_for('main.manage_availability'))
    
    db.session.delete(slot)
    db.session.commit()
    flash('Slot delted successfully','danger')

    return redirect(url_for('main.manage_availability'))

@main_routes.route('/api/doctors/<int:department_id>') 
@login_required
def get_doctor_by_department(department_id):
    doctors=Doctor.query.filter_by(department_id=department_id).all()
    data=[{'id':d.id,'name':f"{d.name}({d.specialization})"} for d in doctors]

    return jsonify({'doctors': data})
    
@main_routes.route('/api/get_slots/<int:doctor_id>/<string:selected_date>')
@login_required
def get_slots(doctor_id,selected_date):
    available_slots=Availability.query.filter_by(
        doctor_id=doctor_id,
        date=selected_date,
        is_booked=False
    ).all()

    available_slots.sort(key=lambda x: datetime.strptime(x.start_time, "%I:%M %p"))

    data=[]
    for slot in available_slots:
        label=f"{slot.start_time}-{slot.end_time}"
        data.append({'id':slot.id,'label':label})
    return jsonify({'slots':data})


    



    
    














