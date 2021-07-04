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