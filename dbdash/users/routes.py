from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import form
from dbdash import db, bcrypt
from dbdash.models import User
from dbdash.users.forms import RegistrationForm, LoginForm, ForgotPasswordFrom

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    givenMsg=''
    if form.validate_on_submit():
        if form.validate_email(form.uEmail):
            hashed_password = bcrypt.generate_password_hash(form.uPassword.data).decode('utf-8')
            user = User(uFirstname=form.uFirstname.data, uLastname=form.uLastname.data, 
                    uEmail=form.uEmail.data, uPassword=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! Login to proceed.', 'success')
            return redirect(url_for('users.login'))
        else:
            givenMsg=form.uEmail.data + ' Email is already Taken !!'
    return render_template('users/register.html', title='Register',givenMsg=givenMsg, form=form)    

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    givenMsg = '';
    if form.validate_on_submit():
        user = User.query.filter_by(uEmail=form.uEmail.data).first()
        if user and bcrypt.check_password_hash(user.uPassword, form.uPassword.data):
            login_user(user, remember=form.uRemember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            givenMsg='Invalid Email or Password !'
    return render_template('users/login.html', title='Login', givenMsg=givenMsg, form=form)

@users.route("/profile", methods=['GET', 'POST'])
def profile():
    pass

@users.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('users.login'))

@users.route("/forgotpassword", methods=['GET', 'POST'])
def forgotpassword():
    form = ForgotPasswordFrom()
    givenMsg=''
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('users/forgot_password.html', title='Forgot Password', givenMsg=givenMsg, form=form)

