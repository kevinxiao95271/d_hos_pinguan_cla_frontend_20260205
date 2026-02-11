#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import codecs
import requests

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

url = 'http://localhost:6031/api/auth/login'
data = {'phone': '13799999112', 'name': '王建国', 'role': 'CONTESTANT'}

print(f'测试账号: {data["name"]} ({data["phone"]})')
print('发送登录请求...\n')

try:
    r = requests.post(url, json=data, timeout=20)
    print(f'Status: {r.status_code}')
    print(f'Response: {r.json()}')
    if r.status_code == 200:
        print('\n✅ 登录成功！')
    else:
        print('\n❌ 登录失败')
except Exception as e:
    print(f'\n❌ 异常: {e}')
