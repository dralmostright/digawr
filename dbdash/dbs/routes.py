from flask import Blueprint, render_template, url_for, flash, redirect, request, send_file
from flask_login import current_user
from dbdash import db
from dbdash.dbs.models import Databases, DbInstInfo, SGAPGAStat, DbOSStat, OverallMetric,DbWaitClass,DBSNAPTBL
from dbdash.dbs.forms import RegisterDBForm, EditDBForm,FilterForm
from dbdash.main.utils import EncValue
from dbdash.dbs.utils import (GetInstanceDetails, GetSGAPGAStat, GetOStat,
                                 GetDbWaitClass, GetOverallMetric, GetIOStatByFun, GetDBAwrSnap)
from dbdash.plots.plots import MemPlot, CPUPlot, AASWaits, IOPLOT, MainActivity

dbs = Blueprint('dbs', __name__)

@dbs.route("/adddbs", methods=['GET', 'POST'])
def adddbs():
    if current_user.is_authenticated:
        givenMsg=''
        status='add'
        form = RegisterDBForm()
        if form.validate_on_submit():
            digDatabase = Databases.query.filter_by(DDBNAME=form.DDBNAME.data, DHOSTNAME=form.DHOSTNAME.data).first()
            passwordHash= EncValue(form.DUSERPASSWORD.data)
            if digDatabase:
                givenMsg='Database have been already Added !'
            else:
                digDatabase = Databases(DDBNAME=form.DDBNAME.data, DHOSTNAME=form.DHOSTNAME.data, 
                                          DPORT=form.DPORT.data, DSERVICENAME=form.DSERVICENAME.data, DUSERNAME=form.DUSERNAME.data,
                                          DUSERPASSWORD=passwordHash,DTYPE=form.DTYPE.data)
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

@dbs.route("/collectdbs/<int:databases_dId>")
def collectdbs(databases_dId):
    if current_user.is_authenticated:
        dbs = Databases.query.get_or_404(databases_dId)
        dbinfo = GetInstanceDetails(dbs)
        if dbinfo:
            aaa= GetSGAPGAStat(dbs,dbinfo)
            bbb= GetOStat(dbs,dbinfo)
            ccc= GetDbWaitClass(dbs,dbinfo)
            ddd= GetOverallMetric(dbs,dbinfo)
            eee= GetIOStatByFun(dbs,dbinfo)
            ddd= GetDBAwrSnap(dbs,dbinfo)
            flash('Information have been successfully recollected','success')
            return redirect(url_for('dbs.listdbs'))
        else:
            flash('Something went wrong while collect information! Please verify the connection details for database.','danger')
            return redirect(url_for('dbs.listdbs'))

    else:
        flash('Your must Login to access request page','info')
        return redirect(url_for('users.login'))

@dbs.route("/delete/<int:databases_dId>")
def deletedbs(databases_dId):
    if current_user.is_authenticated:
        dbs = DbInstInfo.query.filter_by(DID=databases_dId).first()
        if dbs:
            DbInstInfo.query.filter_by(DBID=dbs.DBID).delete()
            SGAPGAStat.query.filter_by(DBID=dbs.DBID).delete()
            DbOSStat.query.filter_by(DBID=dbs.DBID).delete()
            DbWaitClass.query.filter_by(DBID=dbs.DBID).delete()
            OverallMetric.query.filter_by(DBID=dbs.DBID).delete()
            GetDBAwrSnap.query.filter_by(DBID=dbs.DBID).delete()
        Databases.query.filter_by(DID=databases_dId).delete()
        db.session.commit()
        flash('Database have been successfully deleted.','success')
        return redirect(url_for('dbs.listdbs'))
    else:
        flash('Your must Login to access request page','info')
        return redirect(url_for('users.login'))

@dbs.route("/viewdbs/<int:databases_dId>", methods=['GET', 'POST'])
def viewdbs(databases_dId):
    if current_user.is_authenticated:
        form=FilterForm()
        status='viewdb'
        strtSnap=0
        endSnap=0
        if form.validate_on_submit():
            strtSnap=form.STARTSNAP.data
            endSnap=form.ENDTSNAP.data
            if strtSnap >= endSnap:
                flash('Start Snap should be less than End Snap','danger')
                return redirect(url_for('dbs.viewdbs',databases_dId=databases_dId))

        dbs = DbInstInfo.query.filter_by(DID=databases_dId)
        DBID = DbInstInfo.query.filter_by(DID=databases_dId).first()
        snapshots= DBSNAPTBL.query.filter_by(DBID=DBID.DBID)
        plot = MemPlot(DBID.DBID,strtSnap,endSnap)
        plot2 = CPUPlot(DBID.DBID,strtSnap,endSnap)
        plot3,plot4 = AASWaits(DBID.DBID)
        plot5,plot6,plot7,plot8= IOPLOT(DBID.DBID)
        osinfo = DbOSStat.query.filter_by(DBID=DBID.DBID)
        plot9= MainActivity(DBID.DBID,strtSnap,endSnap)
        return render_template('dbs/viewdetail.html', dbs=dbs,form=form,status=status,osinfo=osinfo, plot=plot, plot2=plot2,
                                plot3=plot3, plot4=plot4, plot5=plot5,plot6=plot6,plot7=plot7,plot8=plot8,
                                plot9=plot9, snapshots=snapshots)
    else:
        flash('Your must Login to access request page','info')
        return redirect(url_for('users.login'))

@dbs.route("/editdbs/<int:databases_dId>", methods=['GET', 'POST'])
def editdbs(databases_dId):
    if current_user.is_authenticated:
        status='editdbs'
        form = EditDBForm()
        dbs = Databases.query.get_or_404(databases_dId)
        if form.validate_on_submit():
            passwordHash= EncValue(form.DUSERPASSWORD.data)
            dbs.DDBNAME=form.DDBNAME.data
            dbs.DHOSTNAME=form.DHOSTNAME.data
            dbs.DPORT=form.DPORT.data
            dbs.DSERVICENAME=form.DSERVICENAME.data
            dbs.DUSERNAME=form.DUSERNAME.data
            dbs.DUSERPASSWORD=passwordHash
            dbs.DTYPE=form.DTYPE.data
            db.session.commit()
            flash('Database information have been successfully updated.','success')
            return redirect(url_for('dbs.listdbs'))
        else:
            return render_template('dbs/editdbs.html', title='Edit Database',status=status, dbs=dbs, form=form)
    else:
        flash('Your must Login to access request page','info')
        return redirect(url_for('users.login'))