#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

BASE_URL = 'http://localhost:6039/api'

# 1. 评委会登录
print("=" * 80)
print("步骤1: 评委会登录获取token")
print("=" * 80)
login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
    'phone': '13800000001',
    'password': 'committee123'
})
print(f"登录响应状态码: {login_res.status_code}")
login_data = login_res.json()
print(f"登录响应: {login_data}")

if login_res.status_code != 200 or not login_data.get('success'):
    print("❌ 登录失败")
    print(f"success字段: {login_data.get('success')}")
    sys.exit(1)

token = login_data['data']['token']
print(f"✅ 获取到token: {token[:20]}...")

headers = {
    'Authorization': f'Bearer {token}'
}

# 2. 查询已提交的报名记录（status=SUBMITTED）
print("\n" + "=" * 80)
print("步骤2: 查询已提交的报名记录")
print("=" * 80)
reg_res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': 1,
    'status': 'SUBMITTED',
    'page': 0,
    'size': 5
})
print(f"状态码: {reg_res.status_code}")
reg_data = reg_res.json()

if reg_res.status_code != 200 or not reg_data.get('success'):
    print("❌ 查询失败")
    sys.exit(1)

registrations = reg_data['data']['content']
print(f"✅ 找到 {len(registrations)} 条已提交的报名记录")

# 3. 查看每条记录的材料详情
print("\n" + "=" * 80)
print("步骤3: 查看报名记录的材料详情")
print("=" * 80)

for reg in registrations[:3]:  # 只看前3条
    reg_id = reg['id']
    project_name = reg.get('projectName', 'N/A')
    print(f"\n{'='*60}")
    print(f"报名ID: {reg_id}, 项目名称: {project_name}")
    print(f"{'='*60}")
    
    # 获取详情
    detail_res = requests.get(f'{BASE_URL}/admin/registrations/{reg_id}', headers=headers)
    if detail_res.status_code == 200:
        detail_data = detail_res.json()
        if detail_data.get('success'):
            detail = detail_data['data']
            materials = detail.get('materials', [])
            print(f"材料数量: {len(materials)}")
            for i, mat in enumerate(materials, 1):
                print(f"  材料{i}:")
                print(f"    - id: {mat.get('id')}")
                print(f"    - materialType: {mat.get('materialType')}")
                print(f"    - fileName: {mat.get('fileName')}")
                print(f"    - fileSize: {mat.get('fileSize')}")
                print(f"    - uploadedAt: {mat.get('uploadedAt')}")
        else:
            print(f"  获取详情失败: {detail_data.get('message')}")
    else:
        print(f"  获取详情失败: {detail_res.status_code}")

# 4. 尝试查看报名ID=131的详细信息
print("\n" + "=" * 80)
print("步骤4: 查看报名ID=131的详细信息")
print("=" * 80)
detail_res = requests.get(f'{BASE_URL}/admin/registrations/131', headers=headers)
print(f"状态码: {detail_res.status_code}")
if detail_res.status_code == 200:
    detail_data = detail_res.json()
    print(f"响应: {detail_data}")
else:
    print(f"响应: {detail_res.text}")
