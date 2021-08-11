import pandas as pd
from dbdash import Config
from datetime import datetime
import sqlite3

def FormatQuery(STSNAP,ENDSNAP,query):
    if STSNAP == 0 & ENDSNAP == 0 :
        return query
    else:
        query=query +" and (a.DBSNAPID >="+str(STSNAP)+" AND a.DBSNAPID <="+str(ENDSNAP)+")"
        return query

def GETAWRTIME(STSNAP,ENDSNAP,DBID):
    con = sqlite3.connect(Config.ABSOLUTE_DATABASE_URI)
    if STSNAP == 0 & ENDSNAP == 0 :
        query="SELECT DBSNAPID, DBSNAPENDTIME,DBINSTID from dbsnaptbl where DBID="+str(DBID)
    else: 
        query="SELECT DBSNAPID, DBSNAPENDTIME,DBINSTID from dbsnaptbl where DBID="+str(DBID)+ \
        " and (DBSNAPID >="+str(STSNAP)+" AND DBSNAPID <="+str(ENDSNAP)+")"
    ddf = pd.read_sql_query(query, con)
    return ddf

