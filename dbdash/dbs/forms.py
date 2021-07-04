from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class RegisterDBForm(FlaskForm):
    dDBname = StringField('Database Name', validators=[DataRequired(), Length(min=2, max=20)])
    dHostName = StringField('Database Hostname', validators=[DataRequired(), Length(min=2, max=64)])    
    dPort = IntegerField('Connection Port', validators=[DataRequired()])
    dServiceName = StringField('Service Name', validators=[DataRequired(), Length(min=2, max=64)])
    dType = StringField('Database Type', validators=[DataRequired(), Length(min=2, max=64)])
    dUserName = StringField('Service Name', validators=[DataRequired(), Length(min=2, max=32)])
    dUserPassword = PasswordField('Password', validators=[DataRequired(),Length(min=2, max=32)])
    dSubmit = SubmitField('Add Database')