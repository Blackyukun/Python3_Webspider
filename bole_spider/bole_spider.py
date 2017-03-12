import asyncio
import aiohttp
import time
import re
import os
from bs4 import BeautifulSoup


#转移工作路径
os.mkdir("D:/bole")
os.chdir("D:/bole")
#协程对象
async def get_page(url,res_list,callback=None):
    print(url)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    #限制同时运行的协程数量
    sem = asyncio.Semaphore(5)
    with (await sem):
        async with aiohttp.ClientSession() as session:
            #由于aiohttp使用时会有ConnectionResetError错误，我们处理一下
            try:
                async with session.get(url,headers=headers) as resp:
                    #断言，判断网站状态
                    assert resp.status == 200
                    #判断不同回调函数做处理
                    if callback == get_url:
                        body = await resp.text()
                        callback(res_list, body)
                    elif callback == save_html:
                        body = await resp.text()
                        callback(body)
                    else:
                        return await resp.text()
            except ConnectionResetError as e:
                print('Error: %s, Error_url: %s' % (e,url))
            finally:
                # 关闭请求
                session.close()


#解析页面拿到文章url
def get_url(res_list,body):
    soup = BeautifulSoup(body, 'lxml')
    all_a = soup.select('div.post-meta p a.archive-title')
    for a in all_a:
        hrefs = a.get('href')
        res_list.add(hrefs)
        #print(res_list)
    # print(all_a)


#保存html文件
def save_html(body):
    '''
    正则匹配属于计算密集型任务， HTTP 请求属于 I/O 密集型任务,如果能把两者分开，效率会更高。
    '''
    soup = BeautifulSoup(body, 'lxml')
    titles = soup.title.text
    #在windows环境下有这些字符的文件名不能保存，所有去掉
    title = re.sub('？|：|"','_',titles)
    try:
        with open(title+'.html','w', encoding='utf-8') as f:
            f.write(body)
            print(u'保存成功：%s' % title)
    except:
        print(u'保存失败文章：%s' % title)


start = time.time()

#文章列表页面总页数
page_num = 11
#起始页面
page_url_base = 'http://python.jobbole.com/category/tools/'
#列表页面的列表
page_urls = [page_url_base + 'page/'+ str(i+1) for i in range(page_num)]

#创建事件循环
loop = asyncio.get_event_loop()
#用来存储所有文章详细页url
res_list = set()
#协程任务，获得所有文章详细页面到set中
tasks = [get_page(host,res_list,callback=get_url) for host in page_urls]
#在事件循环中执行协程程序
loop.run_until_complete(asyncio.gather(*tasks))

#协程任务，获得文章详细页面的标题
tasks = [get_page(url,res_list,callback=save_html) for url in res_list]
loop.run_until_complete(asyncio.gather(*tasks))

#关闭事件循环
loop.close()
#用时
print('Elapsed Time: %s' % (time.time()-start))
