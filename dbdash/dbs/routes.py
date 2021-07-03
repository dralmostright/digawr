from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import form
from dbdash import db, bcrypt
from dbdash.models import User
from dbdash.dbs.forms import RegisterDBForm

dbs = Blueprint('dbs', __name__)

@dbs.route("/adddbs", methods=['GET', 'POST'])
def adddbs():
    if current_user.is_authenticated:
        givenMsg=''
        status='add'
        form = RegisterDBForm()
        return render_template('dbs/adddbs.html', title='Add Database',givenMsg=givenMsg,status=status, form=form) 
    else:
        flash('Your must Login to access request page','info')
        return redirect(url_for('users.login'))