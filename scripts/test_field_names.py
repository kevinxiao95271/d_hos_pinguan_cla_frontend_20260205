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
registration_id = 131

print("=" * 80)
print("测试不同的字段名称组合")
print("=" * 80)

test_content = b'This is a test file.'

# 测试不同的file字段名
test_cases = [
    {'file': ('test.docx', test_content), 'materialType': 'REGISTRATION_FORM'},
    {'material': ('test.docx', test_content), 'materialType': 'REGISTRATION_FORM'},
    {'attachment': ('test.docx', test_content), 'materialType': 'REGISTRATION_FORM'},
    {'document': ('test.docx', test_content), 'materialType': 'REGISTRATION_FORM'},
]

for i, case in enumerate(test_cases, 1):
    print(f"\n--- 测试{i}: {list(case.keys())} ---")
    
    # 分离文件和数据
    files = {}
    data = {}
    
    for key, value in case.items():
        if isinstance(value, tuple):
            files[key] = value
        else:
            data[key] = value
    
    print(f"files: {list(files.keys())}")
    print(f"data: {data}")
    
    res = requests.post(
        f'{BASE_URL}/registrations/{registration_id}/materials',
        headers=headers,
        files=files,
        data=data
    )
    
    print(f"状态码: {res.status_code}")
    print(f"响应: {res.text[:150]}")

# 测试不同的materialType字段名
print("\n" + "=" * 80)
print("测试不同的materialType字段名")
print("=" * 80)

type_field_cases = [
    {'file': ('test.docx', test_content), 'materialType': 'REGISTRATION_FORM'},
    {'file': ('test.docx', test_content), 'type': 'REGISTRATION_FORM'},
    {'file': ('test.docx', test_content), 'material_type': 'REGISTRATION_FORM'},
    {'file': ('test.docx', test_content), 'fileType': 'REGISTRATION_FORM'},
]

for i, case in enumerate(type_field_cases, 1):
    print(f"\n--- 测试{i}: {list(case.keys())} ---")
    
    files = {}
    data = {}
    
    for key, value in case.items():
        if isinstance(value, tuple):
            files[key] = value
        else:
            data[key] = value
    
    print(f"data字段: {data}")
    
    res = requests.post(
        f'{BASE_URL}/registrations/{registration_id}/materials',
        headers=headers,
        files=files,
        data=data
    )
    
    print(f"状态码: {res.status_code}")
    print(f"响应: {res.text[:150]}")

# 尝试纯JSON格式（虽然不太可能）
print("\n" + "=" * 80)
print("测试纯JSON格式（非multipart）")
print("=" * 80)

json_data = {
    'materialType': 'REGISTRATION_FORM',
    'fileName': 'test.docx'
}

res = requests.post(
    f'{BASE_URL}/registrations/{registration_id}/materials',
    headers={**headers, 'Content-Type': 'application/json'},
    json=json_data
)

print(f"状态码: {res.status_code}")
print(f"响应: {res.text[:150]}")
