import requests
res = requests.get('http://weibo.hnjuchu.com/index/index/p/1.html')

with open('index.html','w',encoding='utf8') as f :
    f.write(res.text)