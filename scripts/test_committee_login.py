#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

BASE_URL = 'http://localhost:6039/api'

# 测试不同的评委会账号
test_accounts = [
    ('13800000127', 'committee2026'),
    ('13800000001', 'committee123'),
    ('13800000002', 'committee456'),
]

print("=" * 80)
print("测试评委会账号登录")
print("=" * 80)

for phone, password in test_accounts:
    print(f"\n--- 测试账号: {phone} ---")
    
    res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
        'phone': phone,
        'password': password
    })
    
    print(f"状态码: {res.status_code}")
    
    if res.status_code == 200:
        data = res.json()
        print(f"success: {data.get('success')}")
        if data.get('success'):
            print(f"✅ 登录成功")
            print(f"   姓名: {data['data'].get('name')}")
            print(f"   角色: {data['data'].get('role')}")
            print(f"   当前赛事ID: {data['data'].get('currentCompetitionId')}")
            break
        else:
            print(f"❌ 登录失败: {data.get('message')}")
    else:
        print(f"❌ 请求失败: {res.text[:100]}")
