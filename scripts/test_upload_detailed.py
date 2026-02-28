#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE_URL = 'http://localhost:6039/api'

# 1. 登录获取token
print("=" * 80)
print("步骤1: 参赛者登录")
print("=" * 80)
login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
    'phone': '13100009911',
    'password': 'test009911'
})
print(f"登录状态码: {login_res.status_code}")
login_data = login_res.json()

if not login_data.get('success'):
    print(f"❌ 登录失败: {login_data}")
    sys.exit(1)

token = login_data['data']['token']
registration_id = 131
print(f"✅ Token: {token[:20]}...")
print(f"✅ 报名ID: {registration_id}")

headers = {
    'Authorization': f'Bearer {token}'
}

# 2. 测试上传（使用实际文件）
print("\n" + "=" * 80)
print("步骤2: 测试文件上传")
print("=" * 80)

# 尝试用实际的docx文件
import os
test_files = [
    '品管大赛报名表9911.docx',
    '成果报告书9911.docx',
    '佐证材料9911.zip'
]

for file_name in test_files:
    if not os.path.exists(file_name):
        print(f"⚠️  文件不存在: {file_name}")
        continue
    
    print(f"\n--- 测试上传: {file_name} ---")
    
    # 确定materialType
    if '报名表' in file_name:
        material_type = 'REGISTRATION_FORM'
    elif '成果' in file_name or '报告' in file_name:
        material_type = 'REPORT'
    else:
        material_type = 'EVIDENCE'
    
    print(f"materialType: {material_type}")
    
    with open(file_name, 'rb') as f:
        files = {
            'file': (file_name, f, 'application/octet-stream')
        }
        data = {
            'materialType': material_type
        }
        
        res = requests.post(
            f'{BASE_URL}/registrations/{registration_id}/materials',
            headers=headers,
            files=files,
            data=data
        )
        
        print(f"状态码: {res.status_code}")
        print(f"响应头: {dict(res.headers)}")
        print(f"响应体: {res.text}")
        
        # 尝试解析JSON
        try:
            res_json = res.json()
            print(f"JSON格式: {json.dumps(res_json, indent=2, ensure_ascii=False)}")
        except:
            print("响应不是JSON格式")

# 3. 测试只传file不传materialType
print("\n" + "=" * 80)
print("步骤3: 测试只传file不传materialType")
print("=" * 80)

test_content = b'This is a test file.'
files = {
    'file': ('test.docx', test_content, 'application/octet-stream')
}

res = requests.post(
    f'{BASE_URL}/registrations/{registration_id}/materials',
    headers=headers,
    files=files
)

print(f"状态码: {res.status_code}")
print(f"响应: {res.text}")

# 4. 测试materialType作为URL参数
print("\n" + "=" * 80)
print("步骤4: 测试materialType作为URL参数")
print("=" * 80)

files = {
    'file': ('test.docx', test_content, 'application/octet-stream')
}
params = {
    'materialType': 'REGISTRATION_FORM'
}

res = requests.post(
    f'{BASE_URL}/registrations/{registration_id}/materials',
    headers=headers,
    files=files,
    params=params
)

print(f"状态码: {res.status_code}")
print(f"响应: {res.text}")
print(f"实际请求URL: {res.url}")
