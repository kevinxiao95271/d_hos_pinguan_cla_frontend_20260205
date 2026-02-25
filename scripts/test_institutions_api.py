# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json

BASE_URL = 'http://localhost:6031/api'

print('='*80)
print('测试机构列表API')
print('='*80)

# 测试1: 不带Token
print('\n测试1: GET /institutions (无Token)')
try:
    response = requests.get(f'{BASE_URL}/institutions', timeout=10)
    print(f'状态码: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print(f'成功: {result.get("success")}')
        if result.get('success'):
            data = result.get('data', [])
            print(f'返回机构数量: {len(data)}')
            if data:
                print(f'第一个机构: {data[0]}')
    else:
        print(f'失败: {response.text[:200]}')
except Exception as e:
    print(f'异常: {e}')

# 测试2: 带参数
print('\n测试2: GET /institutions?page=0&size=10')
try:
    response = requests.get(f'{BASE_URL}/institutions', params={'page': 0, 'size': 10}, timeout=10)
    print(f'状态码: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print(f'成功: {result.get("success")}')
        print(f'响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}')
    else:
        print(f'失败: {response.text[:200]}')
except Exception as e:
    print(f'异常: {e}')
