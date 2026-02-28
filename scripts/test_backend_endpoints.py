#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

BASE_URL = 'http://localhost:6039/api'

# 登录
login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
    'phone': '13100009911',
    'password': 'test009911'
})
token = login_res.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

# 测试不同的HTTP方法
registration_id = 131
test_url = f'{BASE_URL}/registrations/{registration_id}/materials'

print("=" * 80)
print(f"测试端点: {test_url}")
print("=" * 80)

methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']

for method in methods:
    try:
        res = requests.request(method, test_url, headers=headers, timeout=5)
        print(f"{method:8} -> 状态码: {res.status_code:3}, 响应: {res.text[:100]}")
    except Exception as e:
        print(f"{method:8} -> 错误: {e}")

# 尝试查看已有材料
print("\n" + "=" * 80)
print("查看报名131的现有材料")
print("=" * 80)

# 根据之前的API定义，查看材料应该用 GET /materials/registration/{id}
get_materials_url = f'{BASE_URL}/materials/registration/{registration_id}'
res = requests.get(get_materials_url, headers=headers)
print(f"GET {get_materials_url}")
print(f"状态码: {res.status_code}")
print(f"响应: {res.text}")

# 尝试另一个可能的路径
print("\n" + "=" * 80)
print("尝试GET查看材料（路径2）")
print("=" * 80)
get_materials_url2 = f'{BASE_URL}/registrations/{registration_id}/materials'
res2 = requests.get(get_materials_url2, headers=headers)
print(f"GET {get_materials_url2}")
print(f"状态码: {res2.status_code}")
print(f"响应: {res2.text}")
