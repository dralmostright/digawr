from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import current_user
from dbdash import db
from dbdash.dbs.models import Databases
from dbdash.dbs.forms import RegisterDBForm
from dbdash.main.utils import EncValue
from dbdash.dbs.utils import GetOracleConn

dbs = Blueprint('dbs', __name__)

@dbs.route("/adddbs", methods=['GET', 'POST'])
def adddbs():
    if current_user.is_authenticated:
        givenMsg=''
        status='add'
        form = RegisterDBForm()
        if form.validate_on_submit():
            digDatabase = Databases.query.filter_by(dDBname=form.dDBname.data, dHostName=form.dHostName.data).first()
            passwordHash= EncValue(form.dUserPassword.data)
            if digDatabase:
                givenMsg='Database have been already Added !'
            else:
                digDatabase = Databases(dDBname=form.dDBname.data, dHostName=form.dHostName.data, 
                                          dPort=form.dPort.data, dServiceName=form.dServiceName.data, dUserName=form.dUserName.data,
                                          dUserPassword=passwordHash,dType=form.dType.data)
                db.session.add(digDatabase)
                db.session.commit()
                next_page = request.args.get('next')
                flash('Database have been successfully added.','success')
                return redirect(next_page) if next_page else redirect(url_for('dbs.listdbs'))
        return render_template('dbs/adddbs.html', title='Add Database',givenMsg=givenMsg,status=status, form=form) 
    else:
        flash('Your must Login to access request page','info')
        return redirect(url_for('users.login'))

@dbs.route("/listdbs")
def listdbs():
    status='list'
    if current_user.is_authenticated:
        dbs = Databases.query.all()
        return render_template('dbs/listdbs.html', dbs=dbs,status=status)
    else:
        flash('Your must Login to access request page','info')
        return redirect(url_for('users.login'))

@dbs.route("/listdbs/<int:databases_dId>")
def checkdbs(databases_dId):
    dbs = Databases.query.get_or_404(databases_dId)
    GetOracleConn(dbs)
    return redirect(url_for('dbs.listdbs'))