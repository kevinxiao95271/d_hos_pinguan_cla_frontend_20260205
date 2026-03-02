#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE_URL = 'http://localhost:6039/api'

# 登录
login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
    'phone': '13800000127',
    'password': 'committee2026'
})
token = login_res.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

print("=" * 80)
print("测试用户查询API的HTTP方法")
print("=" * 80)

# 测试GET方法
print("\n--- GET /admin/users/query ---")
res = requests.get(f'{BASE_URL}/admin/users/query', headers=headers, params={
    'page': 0,
    'size': 20
})
print(f"状态码: {res.status_code}")
print(f"响应: {res.text}")

# 测试POST方法（JSON body）
print("\n--- POST /admin/users/query (JSON body) ---")
res = requests.post(f'{BASE_URL}/admin/users/query', headers=headers, json={
    'page': 0,
    'size': 20
})
print(f"状态码: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    print(f"✅ 成功")
    print(f"success: {data.get('success')}")
    if data.get('success'):
        content = data['data'].get('content', [])
        print(f"返回用户数: {len(content)}")
        if content:
            print(f"第一个用户: {content[0]}")
else:
    print(f"响应: {res.text[:200]}")

# 测试POST方法（form-data）
print("\n--- POST /admin/users/query (form-data) ---")
res = requests.post(f'{BASE_URL}/admin/users/query', headers=headers, data={
    'page': 0,
    'size': 20
})
print(f"状态码: {res.status_code}")
print(f"响应: {res.text[:200]}")

# 测试其他可能的路径
print("\n" + "=" * 80)
print("测试其他可能的用户查询接口")
print("=" * 80)

alternatives = [
    ('GET', '/admin/users', {'page': 0, 'size': 20}),
    ('GET', '/admin/users/list', {'page': 0, 'size': 20}),
    ('POST', '/admin/users/search', {'page': 0, 'size': 20}),
]

for method, path, params in alternatives:
    print(f"\n--- {method} {path} ---")
    if method == 'GET':
        res = requests.get(f'{BASE_URL}{path}', headers=headers, params=params)
    else:
        res = requests.post(f'{BASE_URL}{path}', headers=headers, json=params)
    
    print(f"状态码: {res.status_code}")
    if res.status_code == 200:
        print(f"✅ 接口存在且可用")
        print(f"响应: {res.text[:150]}")
    elif res.status_code == 404:
        print(f"❌ 接口不存在")
    else:
        print(f"响应: {res.text[:150]}")

# 总结
print("\n" + "=" * 80)
print("问题分析结果")
print("=" * 80)

print("""
1️⃣ 用户查询接口 (/admin/users/query):
   ✅ 后端实现: POST方法（JSON body）
   ✅ 前端定义: POST方法（src/api/user.js）
   ❌ 浏览器报错: GET方法400错误
   
   🔍 推测原因:
   a) request工具函数可能在某些情况下错误地使用了GET
   b) 可能有缓存或热更新问题
   c) 检查request.js中params和data的处理逻辑

2️⃣ 系统设置接口 (/admin/settings):
   ✅ 接口存在
   ❌ 数据库中配置不存在（返回"配置不存在"）
   ✅ 前端有容错处理（使用默认值）
   
   💡 解决方案:
   a) 后端需要初始化这些配置项到数据库
   b) 或者前端接受400错误，继续使用默认值（当前已实现）
""")
