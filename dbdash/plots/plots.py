import pandas as pd
from dbdash.dbs.models import SGAPGAStat,DbOSStat
from dbdash import db, Config
import sqlite3
import plotly as pt
import plotly.express as px
import json
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dbdash.plots.utils import FormatQuery, GETAWRTIME

def MemPlot(dbid, STSNAP=0, ENDSNAP=0):
    con = sqlite3.connect(Config.ABSOLUTE_DATABASE_URI)
    query="SELECT a.DBSNAPID,a.DBINSTID,a.DBSGA*1024,a.DBPGA*1024,a.DBMEMTOTAL*1024,b.OSTOTALMEM,b.OSTOTALMEM-b.OSFREEMEM \
               from sgapga_stat a, db_os_stat b where a.DBSNAPID=b.DBSNAPID and a.DBINSTID=b.DBINSTID and a.DBID="+str(dbid)
    query=FormatQuery(STSNAP,ENDSNAP,query)
    awrsnp=GETAWRTIME(STSNAP,ENDSNAP,dbid)
    ddf = pd.read_sql_query(query, con)
    height=400
    inst_cnt= ddf.DBINSTID.nunique()
    if inst_cnt > 1:
        height=300*(inst_cnt+1)
    df = pd.merge(ddf, awrsnp, on=['DBSNAPID','DBINSTID'])
    df.drop(['DBSNAPID'], axis=1, inplace=True)
    df.columns = ['Instance','SGA','PGA','DBTOTAL', 'OSTOTAL', 'OSUSED','Snap Time']
    colcount=len(df.columns)
    df= df.melt(id_vars=["Snap Time", "Instance"], 
        var_name="Memory_Type", 
        value_name="Size_GB")
    df['Size_GB'] = df['Size_GB'].astype(float)  
    fig = px.line(df, x="Snap Time", y="Size_GB", color='Memory_Type',height=height,
            facet_row="Instance", title="Instance Memory Distribution",
            labels={"Memory_Type":"TYPE"})
    fig.update_yaxes(ticks="outside", tickwidth=1, tickcolor='crimson', ticklen=5,nticks=10, matches=None, title='Memory Size in MB')
    fig.update_xaxes(ticks="outside", tickwidth=1, tickcolor='crimson', ticklen=5,nticks=15, matches=None, title='Awr Snap Time')
    for i in range(colcount-2):
        fig['data'][i]['line']['width']=1
    graphJSON = json.dumps(fig, cls=pt.utils.PlotlyJSONEncoder)
    return graphJSON

def CPUPlot(databases_dId,STSNAP=0, ENDSNAP=0):
    con = sqlite3.connect(Config.ABSOLUTE_DATABASE_URI)
    if STSNAP == 0 & ENDSNAP == 0 :
        query="SELECT DBSNAPID,DBINSTID,OSIDLE,OSBUSY,OSUSER,OSSYS,OSIOWAIT \
               from db_os_stat where DBID="+str(databases_dId)
    else:
        query="SELECT DBSNAPID,DBINSTID,OSIDLE,OSBUSY,OSUSER,OSSYS,OSIOWAIT \
               from db_os_stat where DBID="+str(databases_dId) \
               +" and (DBSNAPID >="+str(STSNAP)+" AND DBSNAPID <="+str(ENDSNAP)+")"
    awrsnp=GETAWRTIME(STSNAP,ENDSNAP,databases_dId)
    ddf = pd.read_sql_query(query, con)
    height=400
    inst_cnt= ddf.DBINSTID.nunique()
    if inst_cnt > 1:
        height=300*(inst_cnt+1)
    ddf = pd.merge(ddf, awrsnp, on=['DBSNAPID','DBINSTID'])
    ddf.drop(['DBSNAPID'], axis=1, inplace=True)
    ddf.columns = ['Instance','IDLE','BUSY','USER', 'SYS', 'IOWAIT','Snap Time']
    cputotal = ddf['IDLE'] + ddf['BUSY']+ ddf['USER']+ddf['SYS']+ddf['IOWAIT']
    ddf['TOTAL']=cputotal
    ddf['IDLE'] = ddf['IDLE']/(ddf['TOTAL']) *100
    ddf['BUSY'] = ddf['BUSY']/(ddf['TOTAL']) *100
    ddf['USER'] = ddf['USER']/(ddf['TOTAL']) *100
    ddf['SYS'] = ddf['SYS']/(ddf['TOTAL']) *100
    ddf['IOWAIT'] = ddf['IOWAIT']/(ddf['TOTAL']) *100
    del ddf['TOTAL']
    dff= ddf.melt(id_vars=["Snap Time", "Instance"], 
        var_name="CPU_COMP", 
        value_name="USED_PERCENT")
    dff['USED_PERCENT'] = dff['USED_PERCENT'].astype(float) 
    fig = px.area(dff, x="Snap Time", y="USED_PERCENT", color="CPU_COMP", height=height,
          facet_row="Instance", title="CPU Usage Distribution")
    for i in range(len(ddf.columns)-2):
        fig['data'][i]['line']['width']=1
    #fig = px.histogram(dff, x="DBSNAPID",y="USED_PERCENT", color="CPU_COMP")
    fig.update_yaxes(ticks="outside", tickwidth=1, tickcolor='crimson', ticklen=5,nticks=10, matches=None, title='CPU Usage in %')
    fig.update_xaxes(ticks="outside", tickwidth=1, tickcolor='crimson', ticklen=5,nticks=15, matches=None, title='Awr Snap Time')
    graphJSON = json.dumps(fig, cls=pt.utils.PlotlyJSONEncoder)
    return graphJSON

def AASWaits(databases_dId):
    con = sqlite3.connect(Config.ABSOLUTE_DATABASE_URI)
    ddf = pd.read_sql_query("SELECT DBWAITCLASS,sum(DBAVGSESS) \
    from db_wait_class where DBID="+str(databases_dId)+" group by DBWAITCLASS", con)
    ddf.columns = ['DBWAITCLASS','TOTALWAIT']
    total = ddf['TOTALWAIT'].sum()
    ddf['TOTALWAIT'] = ((ddf['TOTALWAIT']/total)*100).astype(float).round(2) 
    fig = px.bar(ddf, y='TOTALWAIT', x='DBWAITCLASS',color="DBWAITCLASS", text='TOTALWAIT',title='Wait Class for Over all Snapshots')
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig.update_xaxes(matches=None, showticklabels=False, title='Wait Class')
    fig.update_yaxes(ticks="outside", tickwidth=1, tickcolor='crimson', ticklen=5,nticks=10, matches=None, title='Percent %')
    graphJSON = json.dumps(fig, cls=pt.utils.PlotlyJSONEncoder)
    return graphJSON

def AAS():
    con = sqlite3.connect(Config.ABSOLUTE_DATABASE_URI)
    ddf = pd.read_sql_query("SELECT DBWAITCLASS,sum(DBAVGSESS) \
    from db_wait_class group by DBWAITCLASS", con)
    ddf.columns = ['DBWAITCLASS','TOTALWAIT']
    total = ddf['TOTALWAIT'].sum()
    print(total)
    #fig = px.histogram(sptuar, 
    #        x="years", 
    #        y="visitors", 
    #        color="Country Name", 
    #        barmode="group",
    #        title=f"Visitors in Aruba, Spain, Turkey - {barmode}")
    #fig.update_layout(yaxis_title="Number of Visitors")
    #fig.update_xaxes(type='category')

def IOPLOT(databases_dId):
    con = sqlite3.connect(Config.ABSOLUTE_DATABASE_URI)
    ddf = pd.read_sql_query("SELECT ENDTIME,INSTID, READMBS, \
    READMBSMAX, \
    READIOPS , \
    READIOPSMAX, \
    WRITEMBS, \
    WRITEMBSMAX, \
    WRITEIOPS, \
    WRITEIOPSMAX \
    from overall_metric where DBID="+str(databases_dId), con)
    cols = ['READMBS', 'READMBSMAX', 'READIOPS', 'READIOPSMAX','WRITEMBS','WRITEMBSMAX','WRITEIOPS','WRITEIOPSMAX']
    ddf[cols] = ddf[cols].apply(pd.to_numeric, errors='coerce', axis=1)
    cols = ['READMBS','READMBSMAX','ENDTIME','INSTID']
    inst_cnt= ddf.INSTID.nunique()
    height=400
    readdf=ddf[cols]
    if inst_cnt > 1:
        dft=readdf.groupby(['ENDTIME']).sum().reset_index()
        dft['INSTID']='*'
        dft=dft[cols]
        height=300*(inst_cnt+1)
        readdf=pd.concat([readdf,dft])
    readdf.columns = ['Avg Read MB/S','Max Read MB/S','AWR Snap Time', 'Instance']
    dff= readdf.melt(id_vars=["AWR Snap Time","Instance"], 
        var_name="OPERATION", 
        value_name="VALUE")
    fig = px.bar(dff, x="AWR Snap Time", y="VALUE", color="OPERATION", facet_row="Instance",barmode="group",
          text='VALUE',
          title=f"I/O - Reads in MB",
          height=height,
          labels={"OPERATION": "Operation","VALUE":"Reads In MB/S"})
    fig.update_traces(texttemplate='%{text:}', textposition='outside')
    fig.update_layout(xaxis_title="Time for AWR Snapshot")
    graphJSON = json.dumps(fig, cls=pt.utils.PlotlyJSONEncoder)

    cols = ['READIOPS','READIOPSMAX','ENDTIME','INSTID']
    readdf=ddf[cols]
    if inst_cnt > 1:
        dft=readdf.groupby(['ENDTIME']).sum().reset_index()
        dft['INSTID']='*'
        dft=dft[cols]
        height=300*(inst_cnt+1)
        readdf=pd.concat([readdf,dft])
    readdf.columns = ['Avg IO/S (IOPS)','Max IO/S (IOPS)','AWR Snap Time', 'Instance']
    dff= readdf.melt(id_vars=["AWR Snap Time","Instance"], 
        var_name="OPERATION", 
        value_name="VALUE")
    fig1 = px.bar(dff, x="AWR Snap Time", y="VALUE", color="OPERATION", facet_row="Instance",barmode="group",
          text='VALUE',
          title=f"I/O - Avg vs Max Read IO/S (IOPS)",
          height=height,
          labels={"OPERATION": "Operation","VALUE":"IOPS"})
    fig1.update_traces(texttemplate='%{text:}', textposition='outside')
    #fig1.update_layout(yaxis_title="IOPS")
    fig1.update_layout(xaxis_title="Time for AWR Snapshot")
    graphJSON1 = json.dumps(fig1, cls=pt.utils.PlotlyJSONEncoder)

    cols = ['WRITEMBS','WRITEMBSMAX','ENDTIME','INSTID']
    readdf=ddf[cols]
    if inst_cnt > 1:
        dft=readdf.groupby(['ENDTIME']).sum().reset_index()
        dft['INSTID']='*'
        dft=dft[cols]
        height=300*(inst_cnt+1)
        readdf=pd.concat([readdf,dft])
    readdf.columns = ['Avg Write MB/S','Max Write MB/S','AWR Snap Time', 'Instance']
    dff= readdf.melt(id_vars=["AWR Snap Time","Instance"], 
        var_name="OPERATION", 
        value_name="VALUE")
    fig = px.bar(dff, x="AWR Snap Time", y="VALUE", color="OPERATION", facet_row="Instance",barmode="group",
          text='VALUE',
          height=height,
          title=f"I/O : Avg vs Max Write MB/S",
          labels={"OPERATION": "Operation","VALUE":"Write in MB/S"})
    fig.update_traces(texttemplate='%{text:}', textposition='outside')
    #fig.update_layout(yaxis_title="Write in MB/S")
    fig.update_layout(xaxis_title="Time for AWR Snapshot")
    graphJSON2 = json.dumps(fig, cls=pt.utils.PlotlyJSONEncoder)

    cols = ['WRITEIOPS','WRITEIOPSMAX','ENDTIME','INSTID']
    readdf=ddf[cols]
    if inst_cnt > 1:
        dft=readdf.groupby(['ENDTIME']).sum().reset_index()
        dft['INSTID']='*'
        dft=dft[cols]
        height=300*(inst_cnt+1)
        readdf=pd.concat([readdf,dft])
    readdf.columns = ['Avg Write IO/S (IOPS)','Max Write IO/S (IOPS)','AWR Snap Time', 'Instance']
    dff= readdf.melt(id_vars=["AWR Snap Time","Instance"], 
        var_name="OPERATION", 
        value_name="VALUE")
    fig = px.bar(dff, x="AWR Snap Time", y="VALUE", color="OPERATION", facet_row="Instance",barmode="group",
          text='VALUE',
          height=height,
          title=f"I/O : Avg vs Max Write IOPS",
          labels={"OPERATION": "Operation","VALUE":"IOPS"})
    fig.update_traces(texttemplate='%{text:}', textposition='outside')
    #fig.update_layout(yaxis_title="IOPS")
    fig.update_layout(xaxis_title="Time for AWR Snapshot")
    graphJSON3 = json.dumps(fig, cls=pt.utils.PlotlyJSONEncoder)

    return graphJSON,graphJSON1,graphJSON2,graphJSON3

def MainActivity(databases_dId,STSNAP=0, ENDSNAP=0):
    con = sqlite3.connect(Config.ABSOLUTE_DATABASE_URI)
    if STSNAP == 0 & ENDSNAP == 0 :
        query="SELECT DBSNAPID,INSTID,COMMITSS,EXECS,HARDPS,LOGONSTOTAL,LOGONSS,REDOMBS,PXSESS,SESESS,SQLRESTCS \
               from overall_metric where DBID="+str(databases_dId)
    else:
        query="SELECT DBSNAPID,INSTID,COMMITSS,EXECS,HARDPS,LOGONSTOTAL,LOGONSS,REDOMBS,PXSESS,SESESS,SQLRESTCS \
               from overall_metric where DBID="+str(databases_dId) \
               +" and (DBSNAPID >="+str(STSNAP)+" AND DBSNAPID <="+str(ENDSNAP)+")"
    ddf = pd.read_sql_query(query, con)
    columns=['COMMITSS','EXECS','HARDPS','LOGONSTOTAL','LOGONSS','REDOMBS','PXSESS','SESESS','SQLRESTCS']
    ddf[columns] = ddf[columns].apply(pd.to_numeric, errors='coerce', axis=1)
    ddf.columns = ['DBSNAPID','Instance','Commits/s','Execs/s','Hard Parses/s', 'Logons Total', 'Logons/s',
               'Redo MB/s','Sessions Parallel','Sessions Serial','SQL Resp (cs)']
    dff= ddf.melt(id_vars=["DBSNAPID","Instance"], 
    var_name="OPERATION", 
    value_name="VALUE")
    fig = px.line(dff, x="DBSNAPID", y="VALUE",color="OPERATION",height=1400,
            facet_row="OPERATION",facet_col="Instance", title="Main Acitivity of Database",
            labels={"DBSNAPID": "Awr Snap ID"})
    for i in range(len(columns)):
        fig['data'][i]['line']['width']=1
    fig.update_yaxes(matches=None, title=None)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(showlegend=False)
    graphJSON = json.dumps(fig, cls=pt.utils.PlotlyJSONEncoder)
    return graphJSON

def PlotTopNWaitEvents(databases_dId,STSNAP=0, ENDSNAP=0):
    con = sqlite3.connect(Config.ABSOLUTE_DATABASE_URI)
    #        query="SELECT DBSNAPID,INSTID,DBWAITCLASS,DBEVENT,DBTPERCENT,TOTALTIME \
    #           from db_top_n_wait_evt where DBID="+str(databases_dId)
    if STSNAP == 0 & ENDSNAP == 0 :
        query="SELECT DBEVENT,DBTPERCENT \
               from db_top_n_wait_evt where DBID="+str(databases_dId)
    else:
        query="SELECT DBEVENT,DBTPERCENT \
               from db_top_n_wait_evt where DBID="+str(databases_dId) \
               +" and (DBSNAPID >="+str(STSNAP)+" AND DBSNAPID <="+str(ENDSNAP)+")"
    ddf = pd.read_sql_query(query, con)
    columns=['DBTPERCENT']
    ddf[columns] = ddf[columns].apply(pd.to_numeric, errors='coerce', axis=1)
    ddf = ddf.groupby(['DBEVENT']).sum().reset_index()
    #print(ddf.head(10))
    total = ddf['DBTPERCENT'].sum()
    ddf['DBTPERCENT'] = ((ddf['DBTPERCENT']/total)*100).astype(float).round(2) 
    fig = px.bar(ddf, y='DBTPERCENT', x='DBEVENT',color="DBEVENT", text='DBTPERCENT', title="Top N wait events of Database")
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig.update_xaxes(matches=None, showticklabels=False, title='Top N Wait Events')
    #fig.update_yaxes()
    fig.update_yaxes(ticks="outside", tickwidth=1, tickcolor='crimson', ticklen=5,nticks=10, matches=None, title='Percent %')
    graphJSON = json.dumps(fig, cls=pt.utils.PlotlyJSONEncoder)
    return graphJSON