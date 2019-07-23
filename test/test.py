import json
import requests
import base64
res = requests.get('http://weibo.hnjuchu.com/user/verify_code.html')

with open('test.png','wb') as f:
    f.write(res.content)
bin = base64.b64encode(res.content)
types = 'all'
res = requests.post('http://10.0.0.61:8081/api/ocr',data={'bin':bin,'type':types})
s = res.text
print(s,len(s),len(s[:-1]))

dic = json.loads(s[:-1])
print(dic['data']['Result'])



# with open('json.txt','w',encoding='utf8') as f :
#     f.write(s)
#
# with open('json.txt','r',encoding='utf8') as f2:
#     res_json = ''
#     for line in f2:
#         s = json.loads(line)
#         res_json += s
# print(s)
