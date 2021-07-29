from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class RegisterDBForm(FlaskForm):
    DDBNAME = StringField('Database Name', validators=[DataRequired(), Length(min=2, max=20)])
    DHOSTNAME = StringField('Database Hostname', validators=[DataRequired(), Length(min=2, max=64)])    
    DPORT = IntegerField('Connection Port', validators=[DataRequired()])
    DSERVICENAME = StringField('Service Name', validators=[DataRequired(), Length(min=2, max=64)])
    DTYPE = StringField('Database Type', validators=[DataRequired(), Length(min=2, max=64)])
    DUSERNAME = StringField('Service Name', validators=[DataRequired(), Length(min=2, max=32)])
    DUSERPASSWORD = PasswordField('Password', validators=[DataRequired(),Length(min=2, max=32)])
    DSUBMIT = SubmitField('Add Database')

class EditDBForm(FlaskForm):
    DDBNAME = StringField('Database Name', validators=[DataRequired(), Length(min=2, max=20)])
    DHOSTNAME = StringField('Database Hostname', validators=[DataRequired(), Length(min=2, max=64)])    
    DPORT = IntegerField('Connection Port', validators=[DataRequired()])
    DSERVICENAME = StringField('Service Name', validators=[DataRequired(), Length(min=2, max=64)])
    DTYPE = StringField('Database Type', validators=[DataRequired(), Length(min=2, max=64)])
    DUSERNAME = StringField('Service Name', validators=[DataRequired(), Length(min=2, max=32)])
    DUSERPASSWORD = PasswordField('Password', validators=[DataRequired(),Length(min=2, max=32)])
    DSUBMIT = SubmitField('Update Database')

class FilterForm(FlaskForm):
    STARTSNAP=IntegerField('Start Snapshot', validators=[DataRequired()])
    ENDTSNAP=IntegerField('Start Snapshot', validators=[DataRequired()])
    DSUBMIT = SubmitField('Show Details')