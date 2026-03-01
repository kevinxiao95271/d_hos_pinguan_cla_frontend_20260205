#!/usr/bin/env python3
"""步骤1: 测试登录"""
import requests
import json

BASE_URL = "http://localhost:6031/api"
TIMEOUT = 30

print("=" * 60)
print("步骤1: 测试登录")
print("=" * 60)

# 测试OPS账号登录
url = f"{BASE_URL}/auth/login-with-password"
data = {
    "phone": "13800000005",
    "password": "ops2026"
}

print(f"\n请求URL: {url}")
print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")

try:
    response = requests.post(url, json=data, timeout=TIMEOUT)
    print(f"\n状态码: {response.status_code}")
    
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('success') and result.get('data'):
        token = result['data'].get('token', '')
        print(f"\n✅ 登录成功!")
        print(f"Token (前50字符): {token[:50]}...")
        print(f"\n完整Token:")
        print(token)
    else:
        print(f"\n❌ 登录失败: {result.get('message')}")
        
except Exception as e:
    print(f"\n❌ 异常: {str(e)}")
