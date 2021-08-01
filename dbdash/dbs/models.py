from datetime import datetime
from dbdash import db

class Databases(db.Model):
    DID = db.Column(db.Integer, primary_key=True)
    DDBNAME = db.Column(db.String(16),nullable=False)
    DHOSTNAME = db.Column(db.String(64), nullable=False)
    DPORT = db.Column(db.String(8), nullable=False)
    DSERVICENAME = db.Column(db.String(64), nullable=False)
    DUSERNAME = db.Column(db.String(32))
    DUSERPASSWORD = db.Column(db.String(256))
    DTYPE = db.Column(db.String(16), nullable=False)

class DbInstInfo(db.Model):
    DID = db.Column(db.Integer, nullable=False)
    DBID = db.Column(db.Integer, primary_key=True)
    DBINSTID = db.Column(db.Integer, primary_key=True)
    DBSTARTUPTIME = db.Column(db.String(16), nullable=False)
    DBVERSION = db.Column(db.String(16), nullable=False)
    DBNAME = db.Column(db.String(32))
    DBINSTNAME = db.Column(db.String(32))
    DBHOSTNAME = db.Column(db.String(256))
    DBPLATFROM = db.Column(db.String(16), nullable=False)
    DBCPUCNT = db.Column(db.Integer, nullable=False)
    DBCPUCORECNT = db.Column(db.Integer, nullable=False)
    DBCPUSOCKETCNT = db.Column(db.Integer, nullable=False)
    DBOSMEMORY = db.Column(db.Integer, nullable=False)

class DBSNAPTBL(db.Model):
    DID = db.Column(db.Integer, primary_key=True)
    DBID = db.Column(db.Integer)
    DBINSTID = db.Column(db.Integer)
    DBSNAPID = db.Column(db.Integer)
    DBSNAPBEGINTIME = db.Column(db.String(64), nullable=False)
    DBSNAPENDTIME = db.Column(db.String(64), nullable=False)    

class SGAPGAStat(db.Model):
    DID = db.Column(db.Integer, primary_key=True) 
    DBID = db.Column(db.Integer, nullable=False)
    DBSNAPID = db.Column(db.Integer, nullable=False)
    DBINSTID = db.Column(db.Integer, nullable=False)
    DBSGA = db.Column(db.String(64), nullable=False)
    DBPGA = db.Column(db.String(64), nullable=False)
    DBMEMTOTAL = db.Column(db.String(64), nullable=False)

class DbOSStat(db.Model):
    DID = db.Column(db.Integer, primary_key=True) 
    DBID = db.Column(db.Integer, nullable=False)
    DBSNAPID = db.Column(db.Integer, nullable=False)
    DBINSTID = db.Column(db.Integer, nullable=False)
    OSLOAD = db.Column(db.Integer)
    OSCPUS = db.Column(db.Integer)
    OSCORES = db.Column(db.Integer)
    OSSOCKET = db.Column(db.Integer)
    OSTOTALMEM = db.Column(db.Integer)
    OSFREEMEM = db.Column(db.Integer)
    OSIDLE = db.Column(db.Integer)
    OSBUSY = db.Column(db.Integer)
    OSUSER = db.Column(db.Integer)
    OSSYS = db.Column(db.Integer)
    OSIOWAIT = db.Column(db.Integer)
    OSNICE = db.Column(db.Integer)
    OSCPUWAIT = db.Column(db.Integer)
    RSRCMGRWAIT = db.Column(db.Integer)
    OSVMIN = db.Column(db.Integer)
    OSVMOUT = db.Column(db.Integer)
    DBCPUCOUNT = db.Column(db.Integer)

class DbWaitClass(db.Model):
    DID = db.Column(db.Integer, primary_key=True) 
    DBID = db.Column(db.Integer, nullable=False)
    DBSNAPID = db.Column(db.Integer, nullable=False)
    DBWAITCLASS = db.Column(db.String(64), nullable=False)
    DBAVGSESS = db.Column(db.String(64))

class DbTopNWaitEvt(db.Model):
    DID = db.Column(db.Integer, primary_key=True) 
    DBID = db.Column(db.Integer, nullable=False)
    DBSNAPID = db.Column(db.Integer, nullable=False)
    INSTID = db.Column(db.Integer, nullable=False)
    DBWAITCLASS = db.Column(db.String(64), nullable=False)
    DBEVENT = db.Column(db.String(64))
    DBTPERCENT = db.Column(db.String(64))
    TOTALTIME = db.Column(db.Integer)
   
class OverallMetric(db.Model):
    DID = db.Column(db.Integer, primary_key=True) 
    DBID = db.Column(db.Integer, nullable=False)
    DBSNAPID = db.Column(db.Integer, nullable=False)
    INSTID = db.Column(db.Integer, nullable=False)
    NUMINTERVAL = db.Column(db.String(64), nullable=False)
    ENDTIME = db.Column(db.String(64), nullable=False)
    OSCPU = db.Column(db.String(64))
    OSCPUMAX = db.Column(db.String(64))
    OSCPUSD = db.Column(db.String(64))
    DBWAITRATIO = db.Column(db.String(64))
    DBCPURATIO = db.Column(db.String(64))
    CPUPERSSEC = db.Column(db.String(64))
    CPUPERSSECSD = db.Column(db.String(64))
    HCPUPERS = db.Column(db.String(64)) ## host cpu per sec
    HCPUPERSSD = db.Column(db.String(64)) ## host cpu per sec sd
    AAS = db.Column(db.String(64)) ## Active Average Session
    AASSD = db.Column(db.String(64)) ## Active Average Session sd
    AASMAX = db.Column(db.String(64)) ## Active Average Session max
    DBTIME = db.Column(db.String(64)) ## 
    DBTIMESD = db.Column(db.String(64)) ## 
    SQLRESTCS = db.Column(db.String(64)) ## Sql response time
    BKGDTPERS= db.Column(db.String(64))
    LOGONSS= db.Column(db.String(64))
    LOGONSTOTAL= db.Column(db.String(64))
    EXECS= db.Column(db.String(64))
    HARDPS= db.Column(db.String(64))
    LREADSS= db.Column(db.String(64))
    COMMITSS= db.Column(db.String(64))
    READMBS= db.Column(db.String(64))
    READMBSMAX= db.Column(db.String(64))
    READIOPS= db.Column(db.String(64))
    READIOPSMAX= db.Column(db.String(64))
    READBKS= db.Column(db.String(64))
    READBKSDIRECT= db.Column(db.String(64))
    WRITEMBS= db.Column(db.String(64))
    WRITEMBSMAX= db.Column(db.String(64))
    WRITEIOPS= db.Column(db.String(64))
    WRITEIOPSMAX= db.Column(db.String(64))
    WRITEBKS= db.Column(db.String(64))
    WRITEBKSDIRECT= db.Column(db.String(64))
    REDOMBS= db.Column(db.String(64))
    DBBLOCKGETSS= db.Column(db.String(64))
    DBBLOCKCHANGESS= db.Column(db.String(64))
    GCCRRECS= db.Column(db.String(64))
    GCCURECS= db.Column(db.String(64))
    GCCRGETCS= db.Column(db.String(64))
    GCCUGETCS= db.Column(db.String(64))
    GCBKCORRUPTED= db.Column(db.String(64))
    GCBKLOST= db.Column(db.String(64))
    PXSESS= db.Column(db.String(64))
    SESESS= db.Column(db.String(64))
    SBLKRLAT= db.Column(db.String(64))
    CELLIOINTMB= db.Column(db.String(64))
    CELLIOINTMBMAX= db.Column(db.String(64))
    SWAPINSEC= db.Column(db.String(64))
    SWAPOUTSEC= db.Column(db.String(64))
    ROLLBACKSPERSEC= db.Column(db.String(64))
    PQTOSERIALPERSEC= db.Column(db.String(64))
    LONGTBLSCANPERSEC= db.Column(db.String(64))

class IORequestByFun(db.Model):
    DID = db.Column(db.Integer, primary_key=True) 
    DBID = db.Column(db.Integer, nullable=False)
    SNAPID = db.Column(db.Integer, nullable=False)
    INSTID = db.Column(db.Integer, nullable=False)
    FUNCNAME = db.Column(db.String(64))
    SMRREQS = db.Column(db.Integer, nullable=False) # Small Read Requests
    SMWREQS = db.Column(db.Integer, nullable=False) # Small WRITE Requests
    LGRREQS = db.Column(db.Integer, nullable=False) # Large Read Requests
    LGWREQS = db.Column(db.Integer, nullable=False) # Large Read Requests