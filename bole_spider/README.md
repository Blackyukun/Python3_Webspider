��������aiohttp������
----
ʹ��aiohttpģ���һ������������Ŀ��
<br>
������Ҫ��<br>
	<ul>
		<li>python3.5����;</li>
		<li>lxml;</li>
		<li>bs4;</li>
	</ul>
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