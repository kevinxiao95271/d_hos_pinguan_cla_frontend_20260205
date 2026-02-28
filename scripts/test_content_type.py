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
print("测试contentType字段")
print("=" * 80)

test_content = b'This is a test file.'

# 测试1: type + contentType
print("\n--- 测试1: type + contentType ---")
files = {'file': ('test.docx', test_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
data = {
    'type': 'REGISTRATION_FORM',
    'contentType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}
res = requests.post(f'{BASE_URL}/registrations/{registration_id}/materials', headers=headers, files=files, data=data)
print(f"状态码: {res.status_code}")
print(f"响应: {res.text}")

# 测试2: materialType + contentType
print("\n--- 测试2: materialType + contentType ---")
files = {'file': ('test.docx', test_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
data = {
    'materialType': 'REGISTRATION_FORM',
    'contentType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}
res = requests.post(f'{BASE_URL}/registrations/{registration_id}/materials', headers=headers, files=files, data=data)
print(f"状态码: {res.status_code}")
print(f"响应: {res.text}")

# 测试3: type + contentType（简化）
print("\n--- 测试3: type + contentType（简化MIME类型） ---")
files = {'file': ('test.docx', test_content, 'application/octet-stream')}
data = {
    'type': 'REGISTRATION_FORM',
    'contentType': 'application/octet-stream'
}
res = requests.post(f'{BASE_URL}/registrations/{registration_id}/materials', headers=headers, files=files, data=data)
print(f"状态码: {res.status_code}")
print(f"响应: {res.text}")

# 测试4: 使用实际文件
print("\n--- 测试4: 使用实际docx文件 ---")
import os
if os.path.exists('品管大赛报名表9911.docx'):
    with open('品管大赛报名表9911.docx', 'rb') as f:
        files = {'file': ('品管大赛报名表9911.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        data = {
            'type': 'REGISTRATION_FORM',
            'contentType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        res = requests.post(f'{BASE_URL}/registrations/{registration_id}/materials', headers=headers, files=files, data=data)
        print(f"状态码: {res.status_code}")
        print(f"响应: {res.text}")
else:
    print("文件不存在")

# 测试5: 尝试不同的type值（小写）
print("\n--- 测试5: type值为小写 ---")
files = {'file': ('test.docx', test_content, 'application/octet-stream')}
data = {
    'type': 'registration_form',
    'contentType': 'application/octet-stream'
}
res = requests.post(f'{BASE_URL}/registrations/{registration_id}/materials', headers=headers, files=files, data=data)
print(f"状态码: {res.status_code}")
print(f"响应: {res.text}")

# 测试6: 查看Swagger或OpenAPI文档
print("\n--- 测试6: 查看API文档 ---")
swagger_urls = [
    f'http://localhost:6039/swagger-ui.html',
    f'http://localhost:6039/api-docs',
    f'http://localhost:6039/v3/api-docs',
    f'http://localhost:6039/api/v3/api-docs'
]

for url in swagger_urls:
    try:
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            print(f"✅ 找到API文档: {url}")
            print(f"内容长度: {len(res.text)}")
            break
        else:
            print(f"❌ {url} - 状态码: {res.status_code}")
    except Exception as e:
        print(f"❌ {url} - 错误: {e}")
