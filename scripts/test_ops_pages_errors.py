#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE_URL = 'http://localhost:6039/api'

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

# 登录OPS账号
print_section("步骤1: 尝试登录OPS账号")

ops_accounts = [
    ('13900000001', 'ops123456'),
    ('13900000002', 'ops123456'),
    ('13800000127', 'committee2026'),  # 用评委会账号测试
]

token = None
headers = None

for phone, password in ops_accounts:
    print(f"\n尝试账号: {phone}")
    login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
        'phone': phone,
        'password': password
    })
    
    if login_res.status_code == 200:
        login_data = login_res.json()
        if login_data.get('success'):
            token = login_data['data']['token']
            role = login_data['data']['role']
            print(f"✅ 登录成功: {login_data['data']['name']} ({role})")
            headers = {'Authorization': f'Bearer {token}'}
            break
        else:
            print(f"❌ 登录失败: {login_data.get('message')}")
    else:
        print(f"❌ 登录失败: {login_res.status_code}")

if not token:
    print("\n❌ 所有账号登录失败")
    sys.exit(1)

# 测试1: 查询用户列表
print_section("测试1: 查询用户列表 (/admin/users/query)")

# 测试不同的参数组合
test_cases = [
    ('无参数', {}),
    ('只有page和size', {'page': 0, 'size': 20}),
    ('带competitionId', {'competitionId': 1, 'page': 0, 'size': 20}),
    ('带role', {'role': 'CONTESTANT', 'page': 0, 'size': 20}),
    ('带enabled', {'enabled': True, 'page': 0, 'size': 20}),
    ('完整参数', {'competitionId': 1, 'page': 0, 'size': 20, 'role': 'CONTESTANT'}),
]

for test_name, params in test_cases:
    print(f"\n--- {test_name} ---")
    print(f"参数: {json.dumps(params, ensure_ascii=False)}")
    
    res = requests.get(f'{BASE_URL}/admin/users/query', headers=headers, params=params)
    print(f"状态码: {res.status_code}")
    
    if res.status_code == 200:
        data = res.json()
        if data.get('success'):
            users = data['data'] if isinstance(data['data'], list) else data['data'].get('content', [])
            print(f"✅ 成功，返回 {len(users)} 个用户")
        else:
            print(f"❌ 失败: {data.get('message')}")
    else:
        print(f"❌ 响应: {res.text[:200]}")

# 测试2: 查询设置
print_section("测试2: 查询系统设置 (/admin/settings)")

setting_keys = [
    'maxRegistrationsPerInstitution',
    'reviewerMaxLoad',
    'basicGroupCount',
    'comprehensiveGroupCount',
    'advancedGroupCount',
    'shortlistRatio'
]

for key in setting_keys:
    print(f"\n--- 查询: {key} ---")
    
    # 测试1: 作为查询参数
    res = requests.get(f'{BASE_URL}/admin/settings', headers=headers, params={'key': key})
    print(f"GET /admin/settings?key={key}")
    print(f"  状态码: {res.status_code}")
    
    if res.status_code == 200:
        data = res.json()
        print(f"  success: {data.get('success')}")
        print(f"  data: {data.get('data')}")
        print(f"  message: {data.get('message')}")
    else:
        print(f"  响应: {res.text[:150]}")

# 测试3: 查看是否有其他的设置查询接口
print_section("测试3: 尝试其他可能的设置查询接口")

alternative_endpoints = [
    f'/admin/settings/{setting_keys[0]}',
    f'/admin/settings/all',
    f'/settings',
    f'/admin/config',
]

for endpoint in alternative_endpoints:
    print(f"\n--- GET {endpoint} ---")
    res = requests.get(f'{BASE_URL}{endpoint}', headers=headers)
    print(f"状态码: {res.status_code}")
    if res.status_code == 200:
        print(f"✅ 端点存在")
        print(f"响应: {res.text[:200]}")
    elif res.status_code == 404:
        print(f"❌ 端点不存在")
    else:
        print(f"响应: {res.text[:150]}")

# 测试4: 查看用户查询接口是否要求特定参数
print_section("测试4: 分析用户查询接口要求")

# 尝试不同的HTTP方法
print("\n尝试POST方法:")
res = requests.post(f'{BASE_URL}/admin/users/query', headers=headers, json={'page': 0, 'size': 20})
print(f"状态码: {res.status_code}")
print(f"响应: {res.text[:200]}")

# 查看OPTIONS
print("\n查看OPTIONS:")
res = requests.options(f'{BASE_URL}/admin/users/query', headers=headers)
print(f"状态码: {res.status_code}")
if 'Allow' in res.headers:
    print(f"允许的方法: {res.headers['Allow']}")

# 总结
print_section("问题总结")

print("""
根据测试结果，需要确认：

1️⃣ /admin/users/query 接口：
   - 是否必须传递某些参数？
   - 是否需要特定的参数格式？
   - 后端期望的参数类型是什么？

2️⃣ /admin/settings 接口：
   - 是否存在这个接口？
   - 查询单个配置的正确方式是什么？
   - 是否需要先创建这些配置？

建议检查后端日志，查看具体的400错误原因。
""")
