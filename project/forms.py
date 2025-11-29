from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField , TextAreaField , IntegerField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
from wtforms.fields import DateField, TimeField
from datetime import datetime, timedelta
from project.models import User, Department,Doctor

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=20)])
    
    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=6)])
    
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    
    name = StringField('Full Name', 
                       validators=[DataRequired(), Length(min=2, max=100)])
    
    age = IntegerField('Age', 
                       validators=[DataRequired(), NumberRange(min=0, max=120)])
    
    gender = SelectField('Gender', 
                         choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                         validators=[DataRequired()])

    submit = SubmitField('Sign Up')

    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired()])
    
    password = PasswordField('Password', 
                             validators=[DataRequired()])
    
    submit = SubmitField('Login')

class AddDoctorForm(FlaskForm):
    
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=6)])
    
    name = StringField('Full Name', 
                       validators=[DataRequired(), Length(min=2, max=100)])
    
    specialization = StringField('Specialization', 
                                 validators=[DataRequired(), Length(min=2, max=100)])

    
    department = SelectField('Department', coerce=int, validators=[DataRequired()])

    submit = SubmitField('Add Doctor')

    
    def __init__(self, *args, **kwargs):
        super(AddDoctorForm, self).__init__(*args, **kwargs)
        
        self.department.choices = [(dept.id, dept.name) for dept in Department.query.order_by('name').all()]
       
        self.department.choices.insert(0, (-1, '-- Select Department --')) 

    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class UpdateDoctorForm(FlaskForm):
    username= StringField('Username', validators=[DataRequired(),Length(min=4,max=20)])
    name=StringField('Full Name',validators=[DataRequired(),Length(min=2,max=100)])
    specialization=StringField('Specialization',validators=[DataRequired(),Length(min=2,max=100)])
    department=SelectField('Department',coerce=int,validators=[DataRequired()])
    submit=SubmitField('Update Doctor Profile')

    def __init__(self,original_username,*args,**kwargs):
        super(UpdateDoctorForm,self).__init__(*args,**kwargs)

        self.original_username=original_username
        self.department.choices=[(dept.id,dept.name) for dept in Department.query.order_by('name').all()]

        def validate_username(self,username):
            if username.data != self.original_username:
                user=User.query.filter_by(username=username.data).first()
                if user:
                    raise ValidationError('That username is taken. Please choose a different one.')

class BookAppointmentForm(FlaskForm):
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    doctor = SelectField('Doctor', coerce=int, validators=[DataRequired()] , validate_choice=False)
    date=SelectField('Date',validators=[DataRequired()])
    time_slot=SelectField('Time Slot',validators=[DataRequired()],validate_choice=False)
    submit=SubmitField('Book Appointment')

    def __init__(self,*args,**kwargs):
        super(BookAppointmentForm,self).__init__(*args,**kwargs)
        self.department.choices=[(dept.id,dept.name) for dept in Department.query.order_by('name').all()]
        self.department.choices.insert(0,(-1,'--select Department'))

        self.doctor.choices = [(-1, '-- Select Department First --')]
        
        dates=[]
        today=datetime.now()
        for i in range(7):
            d=today+timedelta(days=i)
            dates.append((d.strftime('%Y-%m-%d'), d.strftime('%b %d, %Y')))
        self.date.choices = dates

        self.time_slot.choices = [(-1, '-- Select Date First --')]

class TreatmentForm(FlaskForm):
    diagnosis = TextAreaField('Diagnosis', validators=[DataRequired()])
    prescription = TextAreaField('Prescription', validators=[DataRequired()])
    notes = TextAreaField('Notes') 
    submit = SubmitField('Submit Treatment')

class EditPatientProfileForm(FlaskForm):
    name = StringField('Full Name', 
                       validators=[DataRequired(), Length(min=2, max=100)])
    
    age = IntegerField('Age', 
                       validators=[DataRequired(), NumberRange(min=0, max=120)])
    
    gender = SelectField('Gender', 
                         choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                         validators=[DataRequired()])
    
    submit = SubmitField('Update Profile')

class SearchDoctorForm(FlaskForm):
    search_by=SelectField('Search By',choices=[('name','Doctor Name'),('specialization','Specialization')],default='specialization')
    search_term=StringField('Search Term',validators=[DataRequired()])
    submit=SubmitField('Search')

class AvailabilityForm(FlaskForm):
    date = SelectField('Date', validators=[DataRequired()])
    slots=SelectMultipleField('Available Slots', choices=[],option_widget=widgets.CheckboxInput(),widget=widgets.ListWidget(prefix_label=False),validators=[DataRequired()])
    submit = SubmitField('Add Availability')

    def __init__(self,*args,**kwargs):
        super(AvailabilityForm, self).__init__(*args, **kwargs)
        dates=[]
        today= datetime.today()
        for i in range(7):
            d=today+timedelta(days=i)
            dates.append((d.strftime('%Y-%m-%d'), d.strftime('%b %d, %Y')))
        self.date.choices=dates

        slot_choices=[]
        start_hour=9
        end_hour=17

        current=datetime.strptime(f"{start_hour}:00","%H:%M")
        end_time=datetime.strptime(f"{end_hour}:00","%H:%M")

        while current<end_time:
            next_time=current+timedelta(minutes=30)
            label=f"{current.strftime('%I:%M %p')}-{next_time.strftime('%I:%M %p')}"
            value=current.strftime('%I:%M %p')
            slot_choices.append((value,label))
            current=next_time
        self.slots.choices=slot_choices



        
    
            



    





