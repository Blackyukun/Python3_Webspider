import re
import os
import json
import pymongo
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from urllib.parse import urlencode
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException


#爬虫类
class Jpspider(object):

    def __init__(self,offset):
        #参数构造成字典，offset是js渲染的页数
        self.data = {
            'offset': offset,
            'format': 'json',
            'keyword': '街拍',
            'autoload': 'true',
            'count': 20,
            'cur_tab': 3
        }
        #连接数据库
        client = pymongo.MongoClient('localhost', 27017)
        jiepai = client['jiepai']
        self.url_list = jiepai['url_list']

    def save_mongodb(self,dict):
        # 将url保存数据库
        self.url_list.insert_one(dict)
        print(dict)

    #获取页面信息
    def get_html(self,url):
        #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        #处理requests错误
        try:
            html = requests.get(url)
            #判断返回的状态码
            if html.status_code == 200:
                return html
            return None
        except RequestException as e:
            print('Error: %s,%s' % (e,url))
            return None

    #抓取索引页请求，调用parse_index()
    def get_index_html(self,url):
        html = self.get_html(url).text
        self.parse_index(html)

    #解析json
    def parse_index(self,html):
        # url本身可能是空，json.loads会报错
        try:
            # 把json字符串转化成对象
            index_data = json.loads(html)
            # 判断json含有data，data.kays换回所有键名
            if index_data and 'data' in index_data.keys():
                for page in index_data.get('data'):
                    #分析找到所有图集url
                    imgs_url = page.get('article_url')
                    self.get_images_html(imgs_url)
        except JSONDecodeError:
            pass

    #获得所有图片的url
    def get_images_html(self,imgs_url):
        try:
            resp = self.get_html(imgs_url).text
            soup = BeautifulSoup(resp, 'lxml')
            #得到组图名称
            title = soup.title.text
            # 正则匹配url
            images_pattern = re.compile('var gallery = (.*?);', re.S)
            result = re.search(images_pattern, resp)
            # 判断匹配是否成功，如果成功拿到group1
            if result:
                url_data = json.loads(result.group(1))
                # 判断data是否有想要数据
                if url_data and 'sub_images' in url_data.keys():
                    #提取信息
                    sub_images = url_data.get('sub_images')
                    images = [item.get('url') for item in sub_images]
                    #名称和图片url组成字典
                    dict = {
                        title: images
                    }

                    self.download_images(dict)
                    self.save_mongodb(dict)
        except AttributeError:
            pass

    #下载图片
    def download_images(self,dict):
        #提取字典数据
        for k, v in dict.items():
            #以组图名称创建文件夹
            path = k.replace('：', '').strip()
            isExists = os.path.exists(os.path.join("D:\jiepai", path))
            if not isExists:
                print(u'建了一个名字叫做', path, u'的文件夹！')
                os.makedirs(os.path.join("D:\jiepai", path))
                os.chdir(os.path.join("D:\jiepai", path))
            else:
                print(u'名字叫做', path, u'的文件夹已经存在了！')
            for each in v:
                #下载图片时是.content而不是.text
                img = self.get_html(each).content
                filename = each.split('/')[-1] + '.jpg'
                with open(filename, 'wb') as f:
                    print('正在下载; %s.' % filename)
                    f.write(img)


if __name__ == '__main__':
    #0到120间隔20
    pages = [x*20 for x in range(7)]
    for i in pages:
        #实例爬虫对象
        jiepai = Jpspider(i)
        #对data编码，使用urlencode模块
        params = urlencode(jiepai.data)
        base = 'http://www.toutiao.com/search_content/'
        #构造完整的url
        url = base + '?' + params
        #开启进程池
        p = Pool(4)
        try:
            p.apply_async(jiepai.get_index_html(url),url)
        except:
            pass
        p.close()
        p.join()