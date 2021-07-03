from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_login import current_user
from dbdash.models import ListDatabase

class RegisterDBForm(FlaskForm):
    dDBname = StringField('Database Name', validators=[DataRequired(), Length(min=2, max=16)])
    dHostName = StringField('Database Hostname', validators=[DataRequired(), Length(min=2, max=64)])    
    dPort = IntegerField('Connection Port', validators=[DataRequired(), Length(min=2, max=64)])
    dServiceName = StringField('Service Name', validators=[DataRequired(), Length(min=2, max=64)])
    dType = PasswordField('Database Type', validators=[DataRequired(), Length(min=2, max=64)])
    dUserName = StringField('Service Name', validators=[DataRequired(), Length(min=2, max=32)])
    dUserPassword = PasswordField('Password', validators=[DataRequired()])
    dSubmit = SubmitField('Add Database')