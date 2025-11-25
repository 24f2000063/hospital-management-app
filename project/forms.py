from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from wtforms.fields import DateField, TimeField

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
    doctor = SelectField('Doctor', coerce=int, validators=[DataRequired()])

    date=DateField('Date',format='%Y-%m-%d',validators=[DataRequired()])
    time=TimeField('Time',format='%H:%M',validators=[DataRequired()])

    submit = SubmitField('Book Appointment')

    def __init__(self,*args,**kwargs):
        super(BookAppointmentForm,self).__init__(*args,**kwargs)
        self.department.choices=[(dept.id,dept.name) for dept in Department.query.order_by('name').all()]
        self.department.choices.insert(0,(-1,'--select Department'))

        self.doctor.choices = [(doc.id, f"Dr. {doc.name} ({doc.specialization})") for doc in Doctor.query.all()]
        self.doctor.choices.insert(0, (-1, '-- Select Doctor --'))
        







