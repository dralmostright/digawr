from flask import Blueprint, render_template,request,url_for, redirect,flash
from dbdash.models import User
from flask_login import current_user
from flask import Blueprint, render_template, url_for, flash, redirect, request

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    if current_user.is_authenticated:
        users = User.query.all()
        return render_template('home.html', users=users)
    else:
        flash('Your must Login to access request page','info')
        return redirect(url_for('users.login'))

@main.route("/about")
def about():
    return render_template('about.html', title='About')