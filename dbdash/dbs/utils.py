import pandas as pd
import cx_Oracle
from dbdash.main.utils import DecryptValue

def GetOracleConn(dbs):
    datasource = cx_Oracle.makedsn(dbs.dHostName, dbs.dPort, service_name=dbs.dServiceName)
    conn = cx_Oracle.connect(
            user=dbs.dUserName,
            password=DecryptValue(dbs.dUserPassword),
            dsn=datasource
            )
    print(conn.version)
    #return conn

