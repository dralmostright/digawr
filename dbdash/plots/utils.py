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
        " and (a.DBSNAPID >="+str(STSNAP)+" AND a.DBSNAPID <="+str(ENDSNAP)+")"
    ddf = pd.read_sql_query(query, con)
    #print(ddf['DBSNAPENDTIME'].head(10))
    #print(ddf.dtypes)
    #df['A'].apply(lambda x: x.strftime('%d%m%Y'))
    #ddf['DBSNAPENDTIME'] = ddf['DBSNAPENDTIME'].apply(lambda x: str(x))
    #ddf['DBSNAPENDTIME'] = ddf['DBSNAPENDTIME'].apply(lambda x: x.strftime("%m/%d/%Y, %H:%M:%S"))
    #print(ddf.dtypes)
    #.str.strftime("%m/%d/%Y, %H:%M:%S")

    #print(ddf['DBSNAPENDTIME'].head(10))
    return ddf

