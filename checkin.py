# -*- coding: utf-8 -*-

import os
import re
import json
import datetime
import time
import requests


def generate_cookies_dict() -> dict:
    try:
        cookies_dict = {
            'eai-sess': os.environ['EAI_SESS'],
            'UUkey': os.environ['UUKEY']
        }
        return cookies_dict
    except Exception as ept:
        raise Exception(f'[ERROR] {ept}')


def modify_json(res_json: dict) -> dict:
    # load default geo_api_info
    with open(os.path.join('resource', f'{os.environ["CAMPUS"]}.json'), 'r') as ifile:
        res_json['geo_api_info'] = json.load(ifile)

    res_json['province'] = res_json['geo_api_info']['addressComponent']['province']
    res_json['city'] = res_json['geo_api_info']['addressComponent']['city']
    res_json['address'] = res_json['geo_api_info']['formattedAddress']
    res_json['area'] = ' '.join([
        res_json['province'],
        res_json['city'],
        res_json['geo_api_info']['addressComponent']['district']
    ])
    res_json['date'] = datetime.datetime.now().strftime("%Y%m%d")
    res_json['created'] = int(time.time())
    res_json['ismoved'] = 0
    return res_json


def checkin(cookies_dict: dict):
    # base data
    session = requests.session()
    url = 'https://wfw.scu.edu.cn/ncov/wap/default/index'
    cookiesJar = requests.utils.cookiejar_from_dict(
        cookies_dict, cookiejar=None, overwrite=True)
    session.cookies = cookiesJar
    resp = session.get(url=url)
    if resp.status_code != 200:
        raise Exception(f'[ERROR] response status: {resp.status_code}')

    html = resp.content.decode('utf-8')
    pattern = re.compile('var def =(.*);!?')
    res = re.findall(pattern, html)
    if len(res) == 0:
        raise Exception('[ERROR] user templates not found')
    res_json = json.loads(res[0])
    
    # load geo info & modify data
    modify_json(res_json)

    # post checkin data
    url = 'https://wfw.scu.edu.cn/ncov/wap/default/save'
    resp = session.post(url=url, data=res_json)
    if resp.status_code == 200:
        resp_json = json.loads(resp.content.decode('utf-8'))
        print(f'[INFO] 签到结果：{resp_json["m"]}')
    else:
        print(f'[ERROR] 签到失败：{resp.status_code} {resp.content.decode("utf-8")}')


if __name__ == '__main__':
    checkin(generate_cookies_dict())
