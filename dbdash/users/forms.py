from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from dbdash.users.models import User

class RegistrationForm(FlaskForm):
    uFirstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    uLastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])    
    uEmail = StringField('Email', validators=[DataRequired(), Email()])
    uPassword = PasswordField('Password', validators=[DataRequired()])
    confirm_uPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('uPassword')])
    uSubmit = SubmitField('Register Account')

    def validate_email(self, uEmail):
        user = User.query.filter_by(uEmail=uEmail.data).first()
        if user:
            return False
        else:
            return True

class LoginForm(FlaskForm):
    uEmail = StringField('Email', validators=[DataRequired(), Email()])
    uPassword = PasswordField('Password', validators=[DataRequired()])
    uRemember = BooleanField('Remember Me')
    uSubmit = SubmitField('Login')

class ForgotPasswordFrom(FlaskForm):
    uEmail = StringField('Email', validators=[DataRequired(), Email()])
    uPassword = PasswordField('Password', validators=[DataRequired()])
    uRemember = BooleanField('Remember Me')
    uSubmit = SubmitField('Login')