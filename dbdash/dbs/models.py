from datetime import datetime
from dbdash import db

class Databases(db.Model):
    dId = db.Column(db.Integer, primary_key=True)
    dDBname = db.Column(db.String(16),nullable=False)
    dHostName = db.Column(db.String(64), nullable=False)
    dPort = db.Column(db.String(8), nullable=False)
    dServiceName = db.Column(db.String(64), nullable=False)
    dUserName = db.Column(db.String(32))
    dUserPassword = db.Column(db.String(256))
    dType = db.Column(db.String(16), nullable=False)

class DbInstInfo(db.Model):
    dId = db.Column(db.Integer, primary_key=True)
    dbid = db.Column(db.Integer,nullable=False)
    dbinstid = db.Column(db.Integer, nullable=False)
    dbstartuptime = db.Column(db.String(16), nullable=False)
    dbversion = db.Column(db.String(16), nullable=False)
    dbname = db.Column(db.String(32))
    dbinstname = db.Column(db.String(32))
    dbhostname = db.Column(db.String(256))
    dbplatfrom = db.Column(db.String(16), nullable=False)
    dbcpucnt = db.Column(db.Integer, nullable=False)
    dbcpucorecnt = db.Column(db.Integer, nullable=False)
    dbcpusocketcnt = db.Column(db.Integer, nullable=False)
    dbosmemory = db.Column(db.Integer, nullable=False)