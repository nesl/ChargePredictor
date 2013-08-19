#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys
from visualization.models import Client
import json
import time
con = None

try:

    con=mdb.connect(host="localhost", user="root", db="service")
    cur = con.cursor()
    sql_query = "show tables like 'systemsens_%';"
    cur.execute(sql_query)
    tables = []
    for table in cur.fetchall():
        tables.append(table[0])
    cur.close()
    print tables
    for table in tables:
        if table == 'systemsens_':
            continue
        sql_query = 'SELECT message, dt_record FROM ' + table + ' order by dt_record desc LIMIT 1'
        cur = None
        while True:
            try:
                db=mdb.connect(host="localhost", user="root", db="service")
                cur = db.cursor()
                cur.execute(sql_query)
                break
            except Exception as e:
                print >> sys.stderr, table, e
                time.sleep(5)

        ret = cur.fetchone()
        if ret == None:
            continue
        rec = json.loads(ret[0])
        ver = rec["ver"]
        last_upload = ret[1]
        if "phone" in rec:
            Client.update(imei=table.split("_")[1], version=ver, last_upload=last_upload, phone=rec["phone"], model=rec["model"])
        else:
            Client.update(imei=table.split("_")[1], version=ver, last_upload=last_upload)
        cur.close()  
    print "Database version : %s " % data
    
except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
        
    if con:    
        con.close()

