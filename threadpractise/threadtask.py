#coding:utf-8

import requests
from threading import Thread

ips = 
'''
192.168.1.100
192.168.1.101
'''

urls = []
for ip in ips.split('\n'):
	if ip != '':
		url = 'http://'+ip
		urls.append(url)
		
def req(url):
	try:
		response = requests.get(url,timeout=6)
		print(url,str(response.status_code),str(len(response.content)))
	except requests.RequestException as e:
		print(url,e)

t_task = []
for url in urls:
	t = Thread(target=req,args=(url,))
	t_task.append(t)

for t in t_task:
	t.setDaemon(True)
	t.start()

t.join()



