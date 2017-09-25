#-*-coding:utf-8-*-
#reference:
#https://zhuanlan.zhihu.com/p/28806210
#https://github.com/Ehco1996/Python-crawler/blob/master/ithome/spider.py

'''
ubuntu16.04+python2.7.12
>>apt-get install mysql-server 

>>apt-get install  mysql-client

>>apt-get install python-mysqldb

>>apt-get install python-pip

>>pip install requests

>>pip install BeautifulSoup

'''

import requests
from bs4 import BeautifulSoup
import time
import sys
import MySQLdb
import random
from multiprocessing import Pool

#chinese character error,change the system character into utf-8
reload(sys)
sys.setdefaultencoding('utf-8')


def genheaders():
    headers = {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0",
        "client-ip":"192.168.{c}.{d}".format(c=random.randint(0,255),d=random.randint(0,255))}
    return headers

def getnewsid(categoryid,pagestart=1):

    news_url = 'http://it.ithome.com/ithome/getajaxdata.aspx'
    headers = genheaders()
    #get news
    #categoryid=150&type=pccategorypage&page=2
    data = {'categoryid':categoryid,
        'type':'pccategorypage',
        'page':pagestart}

    response = requests.post(news_url,headers=headers,data=data)
    if response.content == None:
        exit()

    for page in xrange(pagestart,pagestart+10):
        data['page'] = str(page)
        try:
            response = requests.post(news_url,headers=headers,data=data)
            # print response.content

            soup = BeautifulSoup(response.content,'html5lib')
            # print soup

            hrefs = soup.find_all('a',attrs={'class':'list_thumbnail'})
            for href in hrefs:
                #<a class="list_thumbnail" href="https://www.ithome.com/html/digi/323893.htm" target="_blank"><img src="http://img.ithome.com/newsuploadfiles/thumbnail/2017/8/323893_240.jpg"/></a>
                #print href['href'].split('/')[-1].split('.')[0]
                yield href['href'].split('/')[-1].split('.')[0]

        except requests.RequestException as e:
            print(e)
            exit()
    

def gethotcomments(newsid):
    hotcomment_url = 'https://dyn.ithome.com/ithome/getajaxdata.aspx'
    headers = genheaders()
    # print headers['client-ip']
    # proxies = {"https":"222.139.194.28:8118"}
    # print newsid
    data = {'newsID':newsid,'type':'hotcomment'}
    comment_details = []
    try:
        response = requests.post(hotcomment_url,headers=headers,data=data)
        # print response.content
        if response.content:
            soup = BeautifulSoup(response.content.decode('utf-8'),'html5lib')
            # print soup
            for info in soup.find('ul',attrs={'class':'list hot'}):
                nickname = info.find('strong',attrs={'class':'nick'}).get_text()
                try:
                    phonebrand = info.find('div',attrs={'class':'info rmp'}).span.a.get_text()
                except:
                    phonebrand = None
                posandtime = info.find('span',attrs={'class':'posandtime'}).get_text()

                #\xa0 decode error,solved at https://stackoverflow.com/questions/36087057/unicodedecodeerror-ascii-codec-cant-decode-byte-0xa0-in-position-0-ordinal
                location = posandtime.replace('IT之家','').replace('网友','').replace(u'\xa0',' ').split(' ')[0]

                posttime = posandtime.split(u'\xa0')[1]
                
                contents = info.find('p').get_text()
                # print nickname,phonebrand,location,posttime,contents
                comment_details.append({'nickname':nickname,'phonebrand':phonebrand,'location':location,'posttime':posttime,'contents':contents})
            
            return comment_details
            
    except requests.RequestException as e:
        print(e)



conn= MySQLdb.connect(
        host='localhost',
        port = 3306,
        user='root',
        passwd='root',
        db ='ithome',
        charset='utf8'
        )
cur = conn.cursor()
sqli = "insert into hotcomment values(%s,%s,%s,%s,%s)"

def savetodb(comment_details):
    # sqli2 = "insert into hotcomment values('脱离了低价趣味的cxy','这个解决办法很简单的，在浏览器里输入www.google.com就能检测到墙壁了。','诺基亚 Lumia 1520',' 江苏扬州','2017-8-31 7:49:39')"
    # cur.execute(sqli2)
    # conn.commit()
    for single in comment_details:
        print single['nickname'],single['phonebrand'],single['location'],single['posttime'],single['contents']
        cur.execute(sqli,(single['nickname'],single['phonebrand'],single['location'],single['posttime'],single['contents']))
        conn.commit()
    

def main(pagestart):
    # categoryid=150
    # categoryid=27
    # categoryid=28
    for categoryid in xrange(151,176):
        newsids = getnewsid(str(categoryid),pagestart)
        if newsids:
            # print newsids.next()
            for newsid in newsids:
                comment_details = gethotcomments(newsid)
                # time.sleep(random.randint(1,1))
                if comment_details:
                    savetodb(comment_details)

            
    
if __name__ == '__main__':
    # main(1)

    pool = Pool()
    pagelists = ([x for x in xrange(1,100,10)])
    pool.map(main,pagelists)
    pool.close()
    pool.join()











