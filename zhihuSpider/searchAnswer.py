# -*- coding: UTF-8 -*-
#抓取的知乎搜索界面关于考研的回答
import requests
import mysqlconnect
from urllib.parse import urlencode
from pyquery import PyQuery as pq
import time

urlSearch = 'https://www.zhihu.com/api/v4/search_v3?'
headers={
    'cookie': 'd_c0="AJDAEUUImwqPTkKyoYgudon8wR6W8cgZ_gM=|1474982733"; q_c1=23b9eda7df81459c9789a908930cca72|1507096790000|1474982733000; _zap=55c589c0-280d-4fe5-8a8d-f5aaa935ad0c; _xsrf=Gs0BGPtSCbvuI78Y3ma5t01tgIhum0RR; q_c1=23b9eda7df81459c9789a908930cca72|1533896590000|1474982733000; __utma=155987696.718434429.1525358318.1533909362.1533971909.3; __gads=ID=a5be66fc4c81514b:T=1554558539:S=ALNI_MZ2Wtus8SRwdPsdt5NIdcbqpzUDcg; tgw_l7_route=4860b599c6644634a0abcd4d10d37251; capsion_ticket="2|1:0|10:1555688182|14:capsion_ticket|44:ODgwMzMxNmYwOWFkNDllOWE1NmEzMzAxNjdkMGJkNDE=|6c9064c327dd03cc62dcbed0c978b3cbcfc872a83df6efef02724e6549cb879d"; z_c0="2|1:0|10:1555688239|4:z_c0|92:Mi4xOXhCWkF3QUFBQUFBa01BUlJRaWJDaWNBQUFDRUFsVk5MM2poWEFCUmpFRl9hSU12ckJPUU13Qk53WlRFWEFvX0tR|574bfa02342878f5394354e72dfc9ab57f324c1e1893d1ab531861041f70421d"; tst=r',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}

#拿到数据库的游标
conn = mysqlconnect.connectMysql()
cur = conn.cursor()

#创建数据表,如果已存在就不建
def createTables():
    #存放知乎精选回答
    if not mysqlconnect.tableExsist(cur,'searchanswer'):
        cur.execute('''
        create table searchanswer(
        id int unsigned primary key auto_increment,
        title text not null,
        author text,
        article mediumtext
        )default charset=utf8mb4;
        ''')


def get_start_url(question):
    data ={'t': 'general',
    'q': question,
    'correction': 1,
    'offset': 0,
    'limit': 20,
    #'lc_idx': 23,
    #'show_all_topics': 0,
    #'search_hash_id': 'a816bc31cec37a086ebb84d447b92bcb',
    #'vertical_info': '1,1,1,1,0,1,1,1,0,1'
    }
    urlInformation = urlSearch + urlencode(data)
    return urlInformation


def get_jsondata(url):
    return requests.get(url,headers=headers).json()


def save_answer(content,name,title):
    #因为content是html的形式，所以要用pyquery解析一下
    doc = pq(content)
    #将<字符替换掉不然小程序显示会有问题
    article = doc.text().replace('<','')
    #标题中有标签，所以要提取文本
    doc = pq(title)
    #标题中的 / 字符需要替换掉，还有就是必须要添上后面这个？号的替换，我也不知道为什么要加
    title = doc.text().replace('/','').replace('?','')
    #数据存入数据库
    try:
        cur.execute("insert into searchanswer(title,author,article) values ('{}','{}','{}');".format(title,name,article))
        conn.commit()
    except Exception as e:
        print('wrong!!!')
    # 存到文件中的代码
    # filepath = './answers/标题-{}-作者-{}.txt'.format(title,name)
    # with open(filepath,'w',encoding='utf-8') as f:
    #     f.write(article)


def search_answer(data):
    temp={}
    i=0
    for item in data:
        if item.get('object'):
            temp = item.get('object')
            if temp.get('type') == 'answer':
                save_answer(temp.get('content'),temp['author']['name'],temp['question']['name'])


def get_articles(url):
    print('正在爬取：' + url)
    jsondata = get_jsondata(url)
    #拿到json中的data
    search_answer(jsondata['data'])
    #通过json中的is_end判断是否到了最后一页
    if not jsondata['paging']['is_end']:
        next_page_url = jsondata['paging']['next']
        #睡五秒，太快会被封
        time.sleep(5)
        get_articles(next_page_url)


if __name__== '__main__':
    #建立数据表
    createTables()
    get_articles(get_start_url('考研'))