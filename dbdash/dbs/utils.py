from dbdash.dbs.models import (DbInstInfo , SGAPGAStat, DbOSStat, DbWaitClass,
                OverallMetric, IORequestByFun, DBSNAPTBL)
import pandas as pd
import cx_Oracle
from dbdash.main.utils import DecryptValue
from dbdash import db

def GetOracleConn(dbs):
    datasource = cx_Oracle.makedsn(dbs.DHOSTNAME, dbs.DPORT, service_name=dbs.DSERVICENAME)
    conn = None;
    try:
        conn = cx_Oracle.connect(
            user=dbs.DUSERNAME,
            password=DecryptValue(dbs.DUSERPASSWORD),
            dsn=datasource
            )

    # show the version of the Oracle Database
    #    print(conn.version)
        return conn
    except cx_Oracle.Error as error:
        print(error)
        return False

def GetInstanceDetails(dbs):
    conn = GetOracleConn(dbs)
    if conn:
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
            )")
        dbinfo=cur.fetchall()
        DbInstInfo.query.filter_by(DBID=dbinfo[0][0]).delete()
        dbDetail = DbInstInfo(DID=dbs.DID,DBID=dbinfo[0][0],DBINSTID=dbinfo[0][1],DBSTARTUPTIME=dbinfo[0][2],
                            DBVERSION=dbinfo[0][3],DBNAME=dbinfo[0][4],DBINSTNAME=dbinfo[0][5],
                            DBHOSTNAME=dbinfo[0][6], DBPLATFROM=dbinfo[0][7],DBCPUCNT=dbinfo[0][8],
                            DBCPUCORECNT=dbinfo[0][9], DBCPUSOCKETCNT=dbinfo[0][10],DBOSMEMORY=dbinfo[0][11])
        db.session.add(dbDetail)
        db.session.commit()
        cur.close()
        return dbinfo[0][0]
    else:
        return False

def GetDBAwrSnap(dbs, dbid):
    conn = GetOracleConn(dbs)
    cur = conn.cursor()
    cur.execute("\
        select instance_number, \
        snap_id, \
        begin_interval_time \
        from dba_hist_snapshot\
        where DBID="+str(dbid) \
        +" order by snap_id")
    DBSNAPTBL.query.filter_by(DBID=dbid).delete()
    db.session.commit()
    dbinfo=cur.fetchall()
    for rows in dbinfo:
        awrHist = DBSNAPTBL(DBID=dbid,DBINSTID=rows[0],DBSNAPID=rows[1],
                            DBSNAPBEGINTIME=rows[2])
        db.session.add(awrHist)
        #print(rows[2])
    db.session.commit()
    return 0

def GetSGAPGAStat(dbs, dbid):
    conn = GetOracleConn(dbs)
    cur = conn.cursor()
    cur.execute(" \
    SELECT snap_id, instance_number, \
    MAX (DECODE (stat_name, 'SGA', stat_value, NULL)) SGA, \
    MAX (DECODE (stat_name, 'PGA', stat_value, NULL)) PGA, \
    MAX (DECODE (stat_name, 'SGA', stat_value, NULL)) + MAX (DECODE (stat_name, 'PGA', stat_value,NULL)) TOTAL \
   FROM \
    (SELECT snap_id, instance_number, \
        ROUND (SUM (bytes) / (1024 * 1024 * 1024), 1) stat_value, MAX ('SGA') stat_name \
     FROM dba_hist_sgastat \
     GROUP BY snap_id, instance_number \
    UNION ALL \
     SELECT snap_id, instance_number, \
        ROUND (value / (1024 * 1024 * 1024), 1) stat_value, 'PGA' stat_name \
       FROM dba_hist_pgastat \
      WHERE  NAME = 'total PGA allocated' \
    ) \
    GROUP BY snap_id, instance_number \
    ORDER BY snap_id, instance_number \
    ")
    SGAPGAStat.query.filter_by(DBID=dbid).delete()
    db.session.commit()
    dbinfo=cur.fetchall()
    for rows in dbinfo:
        memDetail = SGAPGAStat(DBID=dbid,DBSNAPID=rows[0],DBINSTID=rows[1],DBSGA=rows[2],
                          DBPGA=rows[3],DBMEMTOTAL=rows[4])
        db.session.add(memDetail)
    db.session.commit()
    return 0

def GetOStat(dbs, dbid):
    conn = GetOracleConn(dbs)
    cur = conn.cursor()
    cur.execute("\
    SELECT snap_id,  \
    INSTANCE_NUMBER,  \
    MAX(DECODE(STAT_NAME,'LOAD', round(value,1),0)) load,  \
    MAX(DECODE(STAT_NAME,'NUM_CPUS', value,0)) cpus,  \
    MAX(DECODE(STAT_NAME,'NUM_CPU_CORES', value,0)) cores,  \
    MAX(DECODE(STAT_NAME,'NUM_CPU_SOCKETS', value,0)) sockets,  \
    MAX(DECODE(STAT_NAME,'PHYSICAL_MEMORY_BYTES', ROUND(value/1024/1024),0)) mem_mb,  \
    MAX(DECODE(STAT_NAME,'FREE_MEMORY_BYTES', ROUND(value    /1024/1024),0)) mem_free_mb,  \
    MAX(DECODE(STAT_NAME,'IDLE_TIME', value,0)) idle,  \
    MAX(DECODE(STAT_NAME,'BUSY_TIME', value,0)) busy,  \
    MAX(DECODE(STAT_NAME,'USER_TIME', value,0)) usert,  \
    MAX(DECODE(STAT_NAME,'SYS_TIME', value,0)) sys,  \
    MAX(DECODE(STAT_NAME,'IOWAIT_TIME', value,0)) iowait,  \
    MAX(DECODE(STAT_NAME,'NICE_TIME', value,0)) nice,  \
    MAX(DECODE(STAT_NAME,'OS_CPU_WAIT_TIME', value,0)) cpu_wait,  \
    MAX(DECODE(STAT_NAME,'RSRC_MGR_CPU_WAIT_TIME', value,0)) rsrc_mgr_wait,  \
    MAX(DECODE(STAT_NAME,'VM_IN_BYTES', value,0)) vm_in,  \
    MAX(DECODE(STAT_NAME,'VM_OUT_BYTES', value,0)) vm_out,  \
    MAX(DECODE(STAT_NAME,'cpu_count', value,0)) cpu_count  \
    FROM  \
    (SELECT snap_id,  \
        INSTANCE_NUMBER,  \
        STAT_NAME,  \
        value  \
    FROM DBA_HIST_OSSTAT  \
    union all  \
    SELECT SNAP_ID,  \
    INSTANCE_NUMBER,  \
    PARAMETER_NAME STAT_NAME,  \
    to_number(VALUE) value  \
    FROM DBA_HIST_PARAMETER  \
    where PARAMETER_NAME = 'cpu_count'  \
    )  \
    GROUP BY snap_id,  \
    INSTANCE_NUMBER  \
    ORDER BY snap_id,  \
    INSTANCE_NUMBER")
    DbOSStat.query.filter_by(DBID=dbid).delete()
    dbinfo=cur.fetchall()
    for rows in dbinfo:
        ostat = DbOSStat(DBID=dbid,
                            DBSNAPID=rows[0],
                            DBINSTID=rows[1],
                            OSLOAD = rows[2],
                            OSCPUS = rows[3],
                            OSCORES = rows[4],
                            OSSOCKET = rows[5],
                            OSTOTALMEM = rows[6],
                            OSFREEMEM = rows[7],
                            OSIDLE = rows[8],
                            OSBUSY = rows[9],
                            OSUSER = rows[10],
                            OSSYS = rows[11],
                            OSIOWAIT = rows[12],
                            OSNICE = rows[13],
                            OSCPUWAIT = rows[14],
                            RSRCMGRWAIT = rows[15],
                            OSVMIN = rows[16],
                            OSVMOUT = rows[17],
                            DBCPUCOUNT =rows[18])
        db.session.add(ostat)
    db.session.commit()
    return 0

def GetDbWaitClass(dbs, dbid):
    conn = GetOracleConn(dbs)
    cur = conn.cursor()
    cur.execute("\
    SELECT snap_id, \
    wait_class, \
    ROUND (SUM (pSec), 2) avg_sess \
    FROM \
    (SELECT snap_id, \
        wait_class, \
        p_tmfg / 1000000 / ela pSec \
       FROM \
        (SELECT (CAST (s.end_interval_time AS DATE) - CAST (s.begin_interval_time AS DATE)) * 24 * \
            3600 ela, \
            s.snap_id, \
            wait_class, \
            e.event_name, \
            CASE WHEN s.begin_interval_time = s.startup_time \
                THEN e.TIME_WAITED_MICRO \
                ELSE e.TIME_WAITED_MICRO - lag (e.TIME_WAITED_MICRO) over (partition BY \
                    event_id, e.dbid, e.instance_number, s.startup_time order by e.snap_id) \
            END p_tmfg \
           FROM dba_hist_snapshot s, \
            dba_hist_system_event e \
          WHERE s.dbid = e.dbid \
            AND s.instance_number = e.instance_number \
            AND s.snap_id = e.snap_id \
            AND e.wait_class != 'Idle' \
      UNION ALL \
         SELECT (CAST (s.end_interval_time AS DATE) - CAST (s.begin_interval_time AS DATE)) * 24 * \
            3600 ela,\
            s.snap_id, \
            t.stat_name wait_class, \
            t.stat_name event_name, \
            CASE WHEN s.begin_interval_time = s.startup_time \
                THEN t.value \
                ELSE t.value - lag (value) over (partition BY stat_id, t.dbid, t.instance_number, \
                    s.startup_time order by t.snap_id) \
            END p_tmfg \
           FROM dba_hist_snapshot s, \
            dba_hist_sys_time_model t \
          WHERE s.dbid = t.dbid \
            AND s.instance_number = t.instance_number \
            AND s.snap_id = t.snap_id \
            AND t.stat_name = 'DB CPU' \
        ) \
		where p_tmfg is not null \
        ) \
    GROUP BY snap_id, \
    wait_class \
    ORDER BY snap_id, \
    wait_class")
    DbWaitClass.query.filter_by(DBID=dbid).delete()
    dbinfo=cur.fetchall()
    for rows in dbinfo:
        ostat = DbWaitClass(DBID=dbid,
                            DBSNAPID=rows[0],
                            DBWAITCLASS=rows[1],
                            DBAVGSESS = rows[2])
        db.session.add(ostat)
    db.session.commit()
    return 0

def GetOverallMetric(dbs, dbid):
    conn = GetOracleConn(dbs)
    cur = conn.cursor()
    cur.execute("\
    select snap_id ,inst ,num_interval dur_m, end_time , \
    max(decode(metric_name,'Host CPU Utilization (%)',					average,0)) os_cpu, \
    max(decode(metric_name,'Host CPU Utilization (%)',					maxval,null)) os_cpu_max, \
    max(decode(metric_name,'Host CPU Utilization (%)',					STANDARD_DEVIATION,null)) os_cpu_sd, \
    max(decode(metric_name,'Database Wait Time Ratio',                   round(average,1),null)) db_wait_ratio, \
    max(decode(metric_name,'Database CPU Time Ratio',                   round(average,1),null)) db_cpu_ratio, \
    max(decode(metric_name,'CPU Usage Per Sec',                   round(average/100,3),null)) cpu_per_s, \
    max(decode(metric_name,'CPU Usage Per Sec',                   round(STANDARD_DEVIATION/100,3),null)) cpu_per_s_sd, \
    max(decode(metric_name,'Host CPU Usage Per Sec',                   round(average/100,3),null)) h_cpu_per_s, \
    max(decode(metric_name,'Host CPU Usage Per Sec',                   round(STANDARD_DEVIATION/100,3),null)) h_cpu_per_s_sd, \
    max(decode(metric_name,'Average Active Sessions',                   average,null)) aas, \
    max(decode(metric_name,'Average Active Sessions',                   STANDARD_DEVIATION,null)) aas_sd, \
    max(decode(metric_name,'Average Active Sessions',                   maxval,null)) aas_max, \
    max(decode(metric_name,'Database Time Per Sec',					average,null)) db_time, \
    max(decode(metric_name,'Database Time Per Sec',					STANDARD_DEVIATION,null)) db_time_sd, \
    max(decode(metric_name,'SQL Service Response Time',                   average,null)) sql_res_t_cs, \
    max(decode(metric_name,'Background Time Per Sec',                   average,null)) bkgd_t_per_s, \
    max(decode(metric_name,'Logons Per Sec',                            average,null)) logons_s, \
    max(decode(metric_name,'Current Logons Count',                      average,null)) logons_total, \
    max(decode(metric_name,'Executions Per Sec',                        average,null)) exec_s, \
    max(decode(metric_name,'Hard Parse Count Per Sec',                  average,null)) hard_p_s, \
    max(decode(metric_name,'Logical Reads Per Sec',                     average,null)) l_reads_s, \
    max(decode(metric_name,'User Commits Per Sec',                      average,null)) commits_s, \
    max(decode(metric_name,'Physical Read Total Bytes Per Sec',         round((average)/1024/1024,1),null)) read_mb_s, \
    max(decode(metric_name,'Physical Read Total Bytes Per Sec',         round((maxval)/1024/1024,1),null)) read_mb_s_max, \
    max(decode(metric_name,'Physical Read Total IO Requests Per Sec',   average,null)) read_iops, \
    max(decode(metric_name,'Physical Read Total IO Requests Per Sec',   maxval,null)) read_iops_max, \
    max(decode(metric_name,'Physical Reads Per Sec',  			average,null)) read_bks, \
    max(decode(metric_name,'Physical Reads Direct Per Sec',  			average,null)) read_bks_direct, \
    max(decode(metric_name,'Physical Write Total Bytes Per Sec',        round((average)/1024/1024,1),null)) write_mb_s, \
    max(decode(metric_name,'Physical Write Total Bytes Per Sec',        round((maxval)/1024/1024,1),null)) write_mb_s_max, \
    max(decode(metric_name,'Physical Write Total IO Requests Per Sec',  average,null)) write_iops, \
    max(decode(metric_name,'Physical Write Total IO Requests Per Sec',  maxval,null)) write_iops_max, \
    max(decode(metric_name,'Physical Writes Per Sec',  			average,null)) write_bks, \
    max(decode(metric_name,'Physical Writes Direct Per Sec',  			average,null)) write_bks_direct, \
    max(decode(metric_name,'Redo Generated Per Sec',                    round((average)/1024/1024,1),null)) redo_mb_s, \
    max(decode(metric_name,'DB Block Gets Per Sec',                     average,null)) db_block_gets_s, \
    max(decode(metric_name,'DB Block Changes Per Sec',                   average,null)) db_block_changes_s, \
    max(decode(metric_name,'GC CR Block Received Per Second',            average,null)) gc_cr_rec_s, \
    max(decode(metric_name,'GC Current Block Received Per Second',       average,null)) gc_cu_rec_s, \
    max(decode(metric_name,'Global Cache Average CR Get Time',           average,null)) gc_cr_get_cs, \
    max(decode(metric_name,'Global Cache Average Current Get Time',      average,null)) gc_cu_get_cs, \
    max(decode(metric_name,'Global Cache Blocks Corrupted',              average,null)) gc_bk_corrupted, \
    max(decode(metric_name,'Global Cache Blocks Lost',                   average,null)) gc_bk_lost, \
    max(decode(metric_name,'Active Parallel Sessions',                   average,null)) px_sess, \
    max(decode(metric_name,'Active Serial Sessions',                     average,null)) se_sess, \
    max(decode(metric_name,'Average Synchronous Single-Block Read Latency', average,null)) s_blk_r_lat, \
    max(decode(metric_name,'Cell Physical IO Interconnect Bytes',         round((average)/1024/1024,1),null)) cell_io_int_mb, \
    max(decode(metric_name,'Cell Physical IO Interconnect Bytes',         round((maxval)/1024/1024,1),null)) cell_io_int_mb_max, \
    max(decode(metric_name,'VM in bytes Per Sec',                     average,null)) swap_in_sec, \
    max(decode(metric_name,'VM out bytes Per Sec',                     average,null)) swap_out_sec, \
    max(decode(metric_name,'User Rollbacks Per Sec',                     average,null)) rollbacks_per_sec, \
    max(decode(metric_name,'PX downgraded to serial Per Sec',                     average,null)) pq_to_serial_per_sec, \
    max(decode(metric_name,'Long Table Scans Per Sec',                     average,null)) long_tbl_scan_per_sec \
    from( \
    select  snap_id,num_interval,to_char(end_time,'DD/MM/YY HH24:MI') end_time,instance_number inst,metric_name,round(average,1) average, \
    round(maxval,1) maxval,round(standard_deviation,1) standard_deviation \
    from dba_hist_sysmetric_summary \
    where  metric_name in ('Host CPU Utilization (%)','CPU Usage Per Sec','Host CPU Usage Per Sec','Average Active Sessions','Database Time Per Sec', \
    'Executions Per Sec','Hard Parse Count Per Sec','Logical Reads Per Sec','Logons Per Sec', \
    'Physical Read Total Bytes Per Sec','Physical Read Total IO Requests Per Sec','Physical Reads Per Sec','Physical Write Total Bytes Per Sec', \
    'Redo Generated Per Sec','User Commits Per Sec','Current Logons Count','DB Block Gets Per Sec','DB Block Changes Per Sec', \
    'Database Wait Time Ratio','Database CPU Time Ratio','SQL Service Response Time','Background Time Per Sec', \
    'Physical Write Total IO Requests Per Sec','Physical Writes Per Sec','Physical Writes Direct Per Sec','Physical Writes Direct Lobs Per Sec', \
    'Physical Reads Direct Per Sec','Physical Reads Direct Lobs Per Sec', \
    'GC CR Block Received Per Second','GC Current Block Received Per Second','Global Cache Average CR Get Time','Global Cache Average Current Get Time', \
    'Global Cache Blocks Corrupted','Global Cache Blocks Lost', \
    'Active Parallel Sessions','Active Serial Sessions','Average Synchronous Single-Block Read Latency','Cell Physical IO Interconnect Bytes','VM in bytes Per Sec', \
    'VM out bytes Per Sec','User Rollbacks Per Sec','PX downgraded to serial Per Sec','Long Table Scans Per Sec' \
    ) \
    ) \
    group by snap_id,num_interval, end_time,inst \
    order by snap_id, end_time,inst")
    OverallMetric.query.filter_by(DBID=dbid).delete()
    dbinfo=cur.fetchall()
    for rows in dbinfo:
        ovelallmetric = OverallMetric(
        DBID  = dbid,
        SNAPID  = rows[0],
        INSTID  = rows[1],
        NUMINTERVAL  = rows[2],
        ENDTIME = rows[3],
        OSCPU  = rows[4],
        OSCPUMAX  = rows[5],
        OSCPUSD  = rows[6],
        DBWAITRATIO  = rows[7],
        DBCPURATIO  = rows[8],
        CPUPERSSEC  = rows[9],
        CPUPERSSECSD  = rows[10],
        HCPUPERS  = rows[11],
        HCPUPERSSD  = rows[12],
        AAS  = rows[13],
        AASSD  = rows[14],
        AASMAX  = rows[15],
        DBTIME  = rows[16],
        DBTIMESD  = rows[17],
        SQLRESTCS  = rows[18],
        BKGDTPERS = rows[19],
        LOGONSS = rows[20],
        LOGONSTOTAL = rows[21],
        EXECS = rows[22],
        HARDPS = rows[23],
        LREADSS = rows[24],
        COMMITSS = rows[25],
        READMBS = rows[26],
        READMBSMAX = rows[27],
        READIOPS = rows[28],
        READIOPSMAX = rows[29],
        READBKS = rows[30],
        READBKSDIRECT = rows[31],
        WRITEMBS = rows[32],
        WRITEMBSMAX = rows[33],
        WRITEIOPS = rows[34],
        WRITEIOPSMAX = rows[35],
        WRITEBKS = rows[36],
        WRITEBKSDIRECT = rows[37],
        REDOMBS = rows[38],
        DBBLOCKGETSS = rows[39],
        DBBLOCKCHANGESS = rows[40],
        GCCRRECS = rows[41],
        GCCURECS = rows[42],
        GCCRGETCS = rows[43],
        GCCUGETCS = rows[44],
        GCBKCORRUPTED = rows[45],
        GCBKLOST = rows[46],
        PXSESS = rows[47],
        SESESS = rows[48],
        SBLKRLAT = rows[49],
        CELLIOINTMB = rows[50],
        CELLIOINTMBMAX = rows[51],
        SWAPINSEC = rows[52],
        SWAPOUTSEC = rows[53],
        ROLLBACKSPERSEC = rows[54],
        PQTOSERIALPERSEC = rows[55],
        LONGTBLSCANPERSEC = rows[56])
        db.session.add(ovelallmetric)
    db.session.commit()
    return 0

def GetIOStatByFun(dbs, dbid):
    conn = GetOracleConn(dbs)
    cur = conn.cursor()
    cur.execute("\
    SELECT snap_id,instance_number, \
    function_name, \
    SUM(sm_r_reqs) sm_r_reqs, \
    SUM(sm_w_reqs) sm_w_reqs, \
    SUM(lg_r_reqs) lg_r_reqs, \
    SUM(lg_w_reqs) lg_w_reqs \
    FROM \
    (SELECT s.snap_id , \
        s.instance_number , \
        s.dbid , \
        FUNCTION_NAME, \
        CASE \
        WHEN s.begin_interval_time = s.startup_time \
        THEN NVL(fn.SMALL_READ_REQS,0) \
        ELSE NVL(fn.SMALL_READ_REQS,0) - lag(NVL(fn.SMALL_READ_REQS,0),1) over (partition BY fn.FUNCTION_NAME , fn.instance_number , fn.dbid , s.startup_time order by fn.snap_id) \
        END sm_r_reqs, \
        CASE \
        WHEN s.begin_interval_time = s.startup_time \
        THEN NVL(fn.SMALL_WRITE_REQS,0) \
        ELSE NVL(fn.SMALL_WRITE_REQS,0) - lag(NVL(fn.SMALL_WRITE_REQS,0),1) over (partition BY fn.FUNCTION_NAME , fn.instance_number , fn.dbid , s.startup_time order by fn.snap_id) \
        END sm_w_reqs, \
        CASE \
        WHEN s.begin_interval_time = s.startup_time \
        THEN NVL(fn.LARGE_READ_REQS,0) \
        ELSE NVL(fn.LARGE_READ_REQS,0) - lag(NVL(fn.LARGE_READ_REQS,0),1) over (partition BY fn.FUNCTION_NAME , fn.instance_number , fn.dbid , s.startup_time order by fn.snap_id) \
        END lg_r_reqs, \
        CASE \
        WHEN s.begin_interval_time = s.startup_time \
        THEN NVL(fn.LARGE_WRITE_REQS,0) \
        ELSE NVL(fn.LARGE_WRITE_REQS,0) - lag(NVL(fn.LARGE_WRITE_REQS,0),1) over (partition BY fn.FUNCTION_NAME , fn.instance_number , fn.dbid , s.startup_time order by fn.snap_id) \
        END lg_w_reqs \
    FROM dba_hist_snapshot s , \
        DBA_HIST_IOSTAT_FUNCTION fn \
    WHERE s.dbid = fn.dbid \
    AND s.instance_number = fn.instance_number \
    AND s.snap_id     = fn.snap_id \
    ) \
    GROUP BY snap_id,instance_number, \
    function_name \
    having SUM(sm_r_reqs) is not null  \
    order by snap_id ")
    IORequestByFun.query.filter_by(DBID=dbid).delete()
    dbinfo=cur.fetchall()
    for rows in dbinfo:
        iorequestbyfun = IORequestByFun(
            DBID= dbid,
            SNAPID= rows[0],
            INSTID =rows[1],
            FUNCNAME= rows[2],
            SMRREQS= rows[3],
            SMWREQS= rows[4],
            LGRREQS= rows[5],
            LGWREQS= rows[6])
        db.session.add(iorequestbyfun)
    db.session.commit()
    return 0
