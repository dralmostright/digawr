from dbdash.dbs.models import DbInstInfo
import pandas as pd
import cx_Oracle
from dbdash.main.utils import DecryptValue
from dbdash import db

def GetOracleConn(dbs):
    datasource = cx_Oracle.makedsn(dbs.dHostName, dbs.dPort, service_name=dbs.dServiceName)
    conn = None;
    try:
        conn = cx_Oracle.connect(
            user=dbs.dUserName,
            password=DecryptValue(dbs.dUserPassword),
            dsn=datasource
            )

    # show the version of the Oracle Database
        print(conn.version)
        return conn
    except cx_Oracle.Error as error:
        print(error)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def GetInstanceDetails(dbs):
    conn = GetOracleConn(dbs)
    cur = conn.cursor()
    cur.execute(" \
        SELECT * FROM ( \
                SELECT dbid, a.instance_number, startup_time, a.version, \
                db_name, instance_name, host_name, platform_name, CPU_COUNT, \
                CPU_CORE_COUNT, CPU_SOCKET_COUNT ,OS_MEMORY \
        FROM DBA_HIST_DATABASE_INSTANCE a \
        JOIN \
        DBA_CPU_USAGE_STATISTICS b USING  (DBID) \
        JOIN \
        ( \
        SELECT DBID, Value OS_MEMORY , snap_id \
        FROM \
        dba_hist_osstat \
        WHERE stat_name IN ('PHYSICAL_MEMORY_BYTES') \
        AND snap_id IN (SELECT Max(snap_id) FROM dba_hist_osstat) \
        ) \
        c USING (DBID)\
        ORDER BY a.startup_time DESC\
        ) WHERE ROWNUM < 2")
    print(cur)
    dbinfo=cur.fetchall()
    print(dbinfo)
    dbDetail = DbInstInfo(dbid=dbinfo[0][0],dbinstid=dbinfo[0][1],dbstartuptime=dbinfo[0][2],
                          dbversion=dbinfo[0][3],dbname=dbinfo[0][4],dbinstname=dbinfo[0][5],
                          dbhostname=dbinfo[0][6], dbplatfrom=dbinfo[0][7],dbcpucnt=dbinfo[0][8],
                          dbcpucorecnt=dbinfo[0][9], dbcpusocketcnt=dbinfo[0][10],dbosmemory=dbinfo[0][11])
    db.session.add(dbDetail)
    db.session.commit()
    return True


