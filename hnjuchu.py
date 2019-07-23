import time

import requests
import json
import base64
import re
from lxml import etree

decode_url = 'http://10.0.0.61:8081/api/ocr'                        # 验证码解码
verify_img_url = 'http://weibo.hnjuchu.com/user/verify_code.html'  # 验证码图片
login_url = 'http://weibo.hnjuchu.com/user/login.html'              # 登录网址
index_url = 'http://weibo.hnjuchu.com/index/fans/type/4.html'       # 网站主页
tuikuan_url = 'http://weibo.hnjuchu.com/index/refund.html?'          # 退款网站

username = '453453453'
password = '453453453'
login_flag = False

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'Referer': 'http://weibo.hnjuchu.com/user/login.html',
    'Host': 'weibo.hnjuchu.com'
}


# 登录
def login():
    res = requests.get(url=verify_img_url)
    cookie = res.headers['Set-Cookie']  # 设置cookie
    headers['Cookie'] = cookie  #

    verify_json = requests.post(url=decode_url, data={'type': 'all', 'bin': base64.b64encode(res.content)}).text
    verify_json = verify_json[:-1]  # 去空白
    verify_dic = json.loads(verify_json)
    verify_code = verify_dic['data']['Result']  # 验证码

    data = {'username': username, 'password': password, 'verify_code': verify_code}
    res = requests.post(url=login_url, data=data, headers=headers)

    # print(r'<p class="success">(.*)</p>',res.text,re.S)
    if re.findall(r'<p class="success">(.*)</p>', res.text, re.S):
        global login_flag
        login_flag = True


def caiji(id, orders=None):
    words = id
    res = requests.get(url=index_url, headers=headers)
    webo_list = re.findall(r'name="__webo__" value="(.*?)" /></form>', res.text, re.S)
    webo = webo_list[0]
    res = requests.get(url=index_url, headers=headers, params={'words': words, 'type': 4, '__webo__': webo})

    tree = etree.HTML(res.text)
    tr_list = tree.xpath('/html/body/div/div[2]/div/div[3]/div/form/table/tbody/tr')

    for tr in tr_list:
        oid = tr.xpath('.//td[1]/text()')[0]
        uid = tr.xpath('.//td[3]/a/text()')[0]
        if orders != None:
            if oid == orders:
                jindu = tr.xpath('.//td[4]/text()')[0].split('/')[0]
                chushiliang = tr.xpath('.//td[5]/text()')[0].split('/')[0]
                status = tr.xpath('.//td[6]/text()')[0]
                data_taskid = tr.xpath('.//td[7]/div/div/button[2]/@data-taskid')
                if data_taskid:
                    data_taskid = data_taskid[0]
                else:
                    data_taskid = '已退款'
                data = {'oid': orders, 'uid': id, 'jindu': jindu, 'chushiliang': chushiliang, 'status': status,
                        'data_taskid': data_taskid}
                return data
        elif uid == id:
            shijian = tr.xpath('.//td[8]/text()')[0]
            data = {'oid': oid, 'shijian': shijian}
            return data
    else:
        return


def xiadan(id, number):
    res = requests.get('http://weibo.hnjuchu.com/index/task.html', headers=headers)
    webo_list = re.findall(r'name="__webo__" value="(.*?)" /></form>', res.text, re.S)
    webo = webo_list[0]

    res = requests.post(url='http://weibo.hnjuchu.com/index/task.html',
                        data={'ftype': 4, 'wid': id, 'number': number, '__webo__': webo}, headers=headers)
    # print(res.text)
    err = re.findall(r'class="error">(.*?)</p>', res.text, re.S)
    success = re.findall(r'class="success">(.*?)</p>', res.text, re.S)

    if err:
        # print(err[0])
        return err
    elif success:
        # time.sleep(2)
        print(success[0])
        data = caiji(id)
        # print(data)
        return data


def tuikuan(data):
    taskid = data['data_taskid']
    if taskid != '已退款':
        tuikuan_headers = headers
        tuikuan_headers['X-Requested-With'] = 'XMLHttpRequest'
        res = requests.get(url=tuikuan_url,params={'taskId':taskid},headers=tuikuan_headers).text
        # print(res)
        res = json.loads(res)
        success = res['info']  # info : 退款成功
        return success
    else:
        return taskid


if __name__ == '__main__':
    while login_flag != True:
        login()
        time.sleep(1)
        print('登录失败,重试+1')
    print('登录成功')

    xiadan_id = '1826792436'
    number = '100'
    data = xiadan(xiadan_id, number)
    print(data)

    tuikuan_uid = '1826792436'
    tuikuan_orders = data['oid']
    caiji_data = caiji(tuikuan_uid, tuikuan_orders)
    print(caiji_data)
    if caiji_data != None:
        info = tuikuan(caiji_data)
        print(info)
    else:
        print('退款失败, 重新输入订单id,Uid')
