# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests

BASE_URL = 'http://localhost:6031/api'

print('搜索第一个机构...')
try:
    response = requests.post(
        f'{BASE_URL}/institutions/search',
        json={'page': 0, 'size': 1},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data', {}).get('content'):
            inst = result['data']['content'][0]
            print(f'ID: {inst["id"]}')
            print(f'名称: {inst["name"]}')
            print(f'地区: {inst.get("region", "N/A")}')
            print(f'等级: {inst.get("level", "N/A")}')
        else:
            print('未找到机构')
    else:
        print(f'失败: {response.text}')
except Exception as e:
    print(f'异常: {e}')
