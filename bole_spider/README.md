��������aiohttp������
----
ʹ��aiohttpģ���һ������������Ŀ��
<br>
������Ҫ��<br>
    1.  python3.5����
    2.  lxml
    3.  bs4
```
async, await �൱�� python3.4�е� @asyncio.coroutine, yield from
```
����ץȡ�������ߣ�<http://python.jobbole.com/all-posts/>����python�������£���ʱ�ȶ��߳̿��˲���2�롣
aiohttpҲ֧��ʹ�ô���ʾ����
```
async with aiohttp.ClientSession() as session:
	async with session.get("http://python.org",proxy="http://some.proxy.com") as resp:
		print(resp.status)
```