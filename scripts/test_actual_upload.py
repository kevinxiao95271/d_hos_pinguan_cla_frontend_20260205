#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

BASE_URL = 'http://localhost:6039/api'

# 1. 登录获取token
print("=" * 80)
print("步骤1: 登录获取token")
print("=" * 80)
login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
    'phone': '13100009911',
    'password': 'test009911'
})
print(f"登录响应状态码: {login_res.status_code}")
login_data = login_res.json()
print(f"登录响应: {login_data}")

if login_res.status_code != 200 or not login_data.get('success'):
    print("❌ 登录失败")
    sys.exit(1)

token = login_data['data']['token']
print(f"✅ 获取到token: {token[:20]}...")

headers = {
    'Authorization': f'Bearer {token}'
}

# 2. 获取报名信息
print("\n" + "=" * 80)
print("步骤2: 获取报名信息")
print("=" * 80)
reg_res = requests.get(f'{BASE_URL}/registrations/my', headers=headers)
print(f"获取报名信息状态码: {reg_res.status_code}")
reg_data = reg_res.json()
print(f"报名信息: {reg_data}")

if not reg_data.get('success'):
    print("❌ 获取报名信息失败")
    sys.exit(1)

if not reg_data['data'] or len(reg_data['data']) == 0:
    print("❌ 没有找到报名记录")
    sys.exit(1)

registration_id = reg_data['data'][0]['id']
print(f"✅ 报名ID: {registration_id}")

# 3. 测试上传报名表
print("\n" + "=" * 80)
print("步骤3: 测试上传报名表")
print("=" * 80)

# 创建一个测试文件
test_file_content = b'This is a test registration form file.'

# 测试1: 只有file字段
print("\n--- 测试1: 只有file字段 ---")
files = {'file': ('test_registration_form.docx', test_file_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
res1 = requests.post(f'{BASE_URL}/registrations/{registration_id}/materials', headers=headers, files=files)
print(f"状态码: {res1.status_code}")
print(f"响应: {res1.text}")

# 测试2: file + materialType字段（作为formData字段）
print("\n--- 测试2: file + materialType作为formData字段 ---")
files = {'file': ('test_registration_form.docx', test_file_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
data = {'materialType': 'REGISTRATION_FORM'}
res2 = requests.post(f'{BASE_URL}/registrations/{registration_id}/materials', headers=headers, files=files, data=data)
print(f"状态码: {res2.status_code}")
print(f"响应: {res2.text}")

# 测试3: materialType作为查询参数
print("\n--- 测试3: materialType作为查询参数 ---")
files = {'file': ('test_registration_form.docx', test_file_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
params = {'materialType': 'REGISTRATION_FORM'}
res3 = requests.post(f'{BASE_URL}/registrations/{registration_id}/materials', headers=headers, files=files, params=params)
print(f"状态码: {res3.status_code}")
print(f"响应: {res3.text}")

# 测试4: 尝试其他materialType值
print("\n--- 测试4: 尝试其他materialType值 ---")
for material_type in ['REPORT', 'EVIDENCE', 'registration_form', 'report', 'evidence']:
    files = {'file': ('test_file.docx', test_file_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    data = {'materialType': material_type}
    res = requests.post(f'{BASE_URL}/registrations/{registration_id}/materials', headers=headers, files=files, data=data)
    print(f"materialType='{material_type}': 状态码={res.status_code}, 响应={res.text[:100]}")
