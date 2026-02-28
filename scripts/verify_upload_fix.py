#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import os

BASE_URL = 'http://localhost:6039/api'

# 登录
print("=" * 80)
print("验证材料上传修复")
print("=" * 80)

login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
    'phone': '13100009911',
    'password': 'test009911'
})
token = login_res.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}
registration_id = 131

print(f"✅ 登录成功，报名ID: {registration_id}")

# 上传三类文件
test_files = [
    ('品管大赛报名表9911.docx', 'REGISTRATION_FORM'),
    ('成果报告书9911.docx', 'REPORT'),
    ('佐证材料9911.zip', 'EVIDENCE')
]

print("\n" + "=" * 80)
print("测试上传三类材料文件")
print("=" * 80)

success_count = 0

for file_name, material_type in test_files:
    if not os.path.exists(file_name):
        print(f"\n❌ 文件不存在: {file_name}")
        continue
    
    print(f"\n--- 上传: {file_name} (type={material_type}) ---")
    
    with open(file_name, 'rb') as f:
        # 获取文件MIME类型
        if file_name.endswith('.docx'):
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_name.endswith('.zip'):
            content_type = 'application/zip'
        else:
            content_type = 'application/octet-stream'
        
        files = {'file': (file_name, f, content_type)}
        data = {
            'type': material_type,
            'contentType': content_type
        }
        
        res = requests.post(
            f'{BASE_URL}/registrations/{registration_id}/materials',
            headers=headers,
            files=files,
            data=data
        )
        
        print(f"状态码: {res.status_code}")
        
        if res.status_code == 200:
            res_data = res.json()
            if res_data.get('success'):
                print(f"✅ 上传成功!")
                print(f"   材料ID: {res_data['data']['id']}")
                print(f"   文件名: {res_data['data']['fileName']}")
                print(f"   文件URL: {res_data['data']['fileUrl']}")
                success_count += 1
            else:
                print(f"❌ 上传失败: {res_data.get('message')}")
        else:
            print(f"❌ 上传失败: {res.text}")

print("\n" + "=" * 80)
print(f"测试完成: {success_count}/{len(test_files)} 成功")
print("=" * 80)

# 查看上传后的材料列表
print("\n" + "=" * 80)
print("查看报名131的材料列表")
print("=" * 80)

res = requests.get(f'{BASE_URL}/registrations/{registration_id}/materials', headers=headers)
print(f"状态码: {res.status_code}")

if res.status_code == 200:
    materials = res.json()['data']
    print(f"✅ 材料数量: {len(materials)}")
    for i, mat in enumerate(materials, 1):
        print(f"  {i}. {mat.get('fileName')} (type={mat.get('type')}, id={mat.get('id')})")
else:
    print(f"❌ 查询失败: {res.text}")
