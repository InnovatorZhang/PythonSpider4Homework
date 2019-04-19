import pymysql as sql
from config import *

def connectMysql():
    conn = sql.connect(host='127.0.0.1',user=mysql_user,passwd=mysql_passwd,db=mysql_database,charset='utf8')
    return conn

def tableExsist(cur,tableName):
    cur.execute('show tables;')
    items = cur.fetchall()
    for item in items:
        if item[0] == tableName:
            return True
    return False