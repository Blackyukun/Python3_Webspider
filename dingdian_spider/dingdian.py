# -*- coding: utf-8 -*-

import requests
import re
import os
import pymongo
from bs4 import BeautifulSoup


#连接数据库，去重
client = pymongo.MongoClient('localhost', 27017)
dingd = client['dingd']
url_list = dingd['url_list']
item_info2 = dingd['item_info2']


#网页请求的函数
def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    html = requests.get(url,headers=headers).content

    return html

#创建文件夹的函数，保存到D盘
def mkdir(path):
    #字符串去掉空格
    path = path.strip()
    isExists = os.path.exists(os.path.join("D:\dingd", path))
    if not isExists:
        print(u'建了一个名字叫做', path, u'的文件夹！')
        os.makedirs(os.path.join("D:\dingd", path))
        os.chdir(os.path.join("D:\dingd", path))
        return True
    else:
        print(u'名字叫做', path, u'的文件夹已经存在了！')
        return False

#这个函数获取所有页数，并且发送给下一个生成器
def manager(g,url):
    g.__next__()
    #用lxml解析页面
    soup = BeautifulSoup(get_html(url), 'lxml')
    #获得最后一页的页数
    all_page = soup.find('div',class_="pagelink").find_all('a')[-1].get_text()
    n = 0
    #循环向下一个work1发数据
    while True:
        n = n + 1
        all_pages = url.split('_')[0] + '_' + str(n) + '.html'
        print('send page %s' % all_pages)
        #生成器的send()函数给生成器传输数据
        g.send(all_pages)
        #如果大于最后一页页数停止循环
        if n > int(all_page):
            break
    #关闭生成器
    g.close()

#获取上一个发送的页数，并且获取本页所有小说章节目录地址，发送给下一个生成器
def work1(g):
    g.__next__()
    while True:
        #接收manager的数据
        pages = yield
        #如果没有数据继续接收，不执行下面程序
        if not pages:
            continue
        soup = BeautifulSoup(get_html(pages),'lxml')
        #获取章节地址
        all_tr = soup.find_all('tr',bgcolor="#FFFFFF")
        for each in all_tr:
            href = each.find_all('a')[1].get('href')
            print('send href %s' % href)
            #传输数据
            g.send(href)

#获取小说章节地址，并且获取每一章的地址，发送给下一个生成器
def work2(g):
    g.__next__()
    while True:
        #接收work1数据
        work1_tables = yield
        if not work1_tables:
            continue
        soup = BeautifulSoup(get_html(work1_tables), 'lxml')
        #获得小说名
        titles = soup.title.text
        #创建文件夹
        mkdir(titles)
        #每一章节的地址
        all_td = soup.find_all('td',class_="L")
        for a in all_td:
            #这里有个页面请求错误，直接过滤掉
            try:
                html = a.find('a').get('href')
                htmls = work1_tables + html
                g.send(htmls)
            except:
                print('pass')

#获得每一章的地址，保存小说内容到对应章节的txt文件
def work3():
    while True:
        #接收work2数据
        work2_htmls = yield
        if not work2_htmls:
            continue
        #判断每一章的url是否在数据库，如果在就不继续下面程序
        if item_info2.find_one({'url': work2_htmls}):
            print('爬过了')
        else:
            #将url保存数据库
            item_info2.insert_one({'url': work2_htmls})
            soup = BeautifulSoup(get_html(work2_htmls), 'lxml')
            #获取章节标题
            title = soup.title.text.split('-')[1]
            all_info = soup.find('dd', id="contents")
            # print(all_info)
            #使用正则匹配章节内容
            p = r'<dd id="contents">(.*?)</dd>'
            #处理正则在匹配错误，都是作者牢骚的内容，不影响小说内容抓取，直接过滤
            try:
                info = re.findall(p, str(all_info), re.S)[0]
                #下载到txt文件
                with open(title + '.txt', 'w', encoding='gbk', errors='ignore') as f:
                    f.write(info.replace('<br/>', '\n'))
                    print('save sucessful: %s' % title)
            except:
                print('re faild: %s' % title)




if __name__ == '__main__':
    #这个url是第一个分类的链接，可以获取所有分类的链接，我们以第一个分类的链接为例。
    #所有链接获取方式很简单，不赘述了
    url = 'http://www.23us.com/class/1_1.html'
    #url2 = 'http://www.23us.com/class/2_1.html'
    manager(work1(work2(work3())),url)