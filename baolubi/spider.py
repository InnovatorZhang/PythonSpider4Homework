import requests
import time
import mysqlconnect
from pyquery import PyQuery as pq


#拿到数据库的游标
conn = mysqlconnect.connectMysql()
cur = conn.cursor()

#获取返回数据并转换为pyquery格式
def getDoc(url):
    try:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        doc = pq(response.text)
    except Exception:
        #服务器出问题的话就等五秒再请求
        print('something bad happend,but I will try agin')
        time.sleep(5)
        doc = getDoc(url)
    finally:
        return doc

#创建数据表,如果已存在就不建
def createTables():
    if not mysqlconnect.tableExsist(cur,'information'):
        cur.execute('''
        create table information(
        id int unsigned primary key auto_increment,
        schoolname varchar(32) not null,
        link text
        )default charset=utf8;
        ''')
    if not mysqlconnect.tableExsist(cur, '34college'):
        cur.execute('''
        create table 34college(
        id int unsigned primary key auto_increment,
        schoolname varchar(32) not null,
        link text
        )default charset=utf8;
        ''')
    if not mysqlconnect.tableExsist(cur, 'baolubi'):
        cur.execute('''
        create table baolubi(
        id int unsigned primary key auto_increment,
        schoolname varchar(32) not null,
        title varchar(128) not null,
        link text
        )default charset=utf8;
        ''')

#将34所自划线的学校的数据保存到数据库中
def get_34college():
    doc = getDoc('http://www.kaoyan.com/baolubi/')
    # 三十四所自划线高校
    items1 = doc('.fsScoreline34#baolubiTable tr td span a').items()
    for item in items1:
        # 消去北航中的\xa0和空格
        schoolname = item.text().replace('\xa0', '').replace(' ', '')
        link = item.attr('href')
        # 如果数据库中还没有当前学校数据就将数据插入数据表中
        if not cur.execute('select * from 34college where schoolname="{}";'.format(schoolname)):
            cur.execute("insert into 34college (schoolname,link) values ('{}','{}');".format(schoolname, link))
        # 这一步很重要，将更改提交到数据库https://www.kancloud.cn/kancloud/python-basic/41705
        conn.commit()

#获取其他所有学校的信息并存入数据库
def get_allCollege():
    doc = getDoc("http://www.kaoyan.com/baolubi/")
    items2 = doc('.w1000 .fsCon .fsTable li a').items()
    for item in items2:
        # 消去北航中的\xa0和空格
        schoolname = item.text().replace('\xa0', '').replace(' ', '')
        link = item.attr('href')
        # 如果数据库中还没有当前学校数据就将数据插入数据表中
        if not cur.execute('select * from information where schoolname="{}";'.format(schoolname)):
            cur.execute("insert into information (schoolname,link) values ('{}','{}');".format(schoolname, link))
        # 这一步很重要，将更改提交到数据库https://www.kancloud.cn/kancloud/python-basic/41705
        conn.commit()


#获取所有学校的报录比信息
def store_allCollege_baolubi():
    get_34college()
    get_allCollege()
    cur.execute('select link,schoolname from information where id > 860')
    items3 = cur.fetchall()
    # 拿到每个大学第一个报录比信息页面的地址
    for item in items3:
        getInformation(item[0], item[1])
        # 休眠一秒，不然服务器遭不住
        time.sleep(1)

def getInformation(url,schoolname):
    doc = getDoc(url)
    items4 = doc('.subList li a').items()
    nextpages = doc('.tPage a').items()
    for item1 in items4:
        print(item1.text(),item1.attr('href'))
        if not cur.execute('select * from baolubi where title="{}"'.format(item1.text())):
            cur.execute('insert into baolubi (schoolname,title,link) values("{}","{}","{}")'.format(schoolname,item1.text(),item1.attr('href')))
    conn.commit()
    for i in nextpages:
        if i.text() == '下一页':
            print(i.attr('href'))
            #判断是否到了最后一页
            if i.attr('href'):
                getInformation(i.attr('href'),schoolname)


if __name__== '__main__':
    createTables()
    #抓取这一部分可以改成多线程的，先完成功能了再说
    store_allCollege_baolubi()
