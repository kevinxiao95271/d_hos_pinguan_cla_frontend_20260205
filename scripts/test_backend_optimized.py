#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试后端优化后的接口"""

import requests
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:6031/api"

try:
    # 1. 登录
    print("1️⃣  登录...")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Title",
        "role": "COMMITTEE_ADMIN"
    }, timeout=10)
    
    token = r.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功\n")
    
    # 2. 测试 admin filter 接口（应该不再返回 401）
    print("2️⃣  测试 /api/admin/registrations/filter")
    r = requests.get(
        f"{BASE_URL}/admin/registrations/filter",
        headers=headers,
        params={"competitionId": 21},
        timeout=10
    )
    
    print(f"   状态码: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()['data']
        print(f"   ✅ 请求成功，共 {len(data)} 条\n")
        
        if len(data) > 0:
            first = data[0]
            print("   第一条数据的关键字段:")
            print(f"      - id: {first.get('id')}")
            print(f"      - projectName: {first.get('projectName')}")
            print(f"      - registrationId: {first.get('registrationId')}")
            print(f"      - institutionName: {first.get('institutionName')}")
            print(f"      - methodCode: {first.get('methodCode')}")
            print(f"      - methodLabel: {first.get('methodLabel')}")
            print(f"      - subjectTypeCode: {first.get('subjectTypeCode')}")
            print(f"      - subjectTypeLabel: {first.get('subjectTypeLabel')}")
            print(f"      - applicantName: {first.get('applicantName')}")
            
            # 3. 测试按 methodCode 筛选
            if first.get('methodCode'):
                method_code = first['methodCode']
                print(f"\n3️⃣  测试按品管工具筛选 (methodCode={method_code})")
                r = requests.get(
                    f"{BASE_URL}/admin/registrations/filter",
                    headers=headers,
                    params={"competitionId": 21, "methodCode": method_code},
                    timeout=10
                )
                if r.status_code == 200:
                    filtered = r.json()['data']
                    print(f"   ✅ 筛选成功，共 {len(filtered)} 条")
                    if len(filtered) > 0:
                        print(f"   第一条的 methodLabel: {filtered[0].get('methodLabel')}")
                else:
                    print(f"   ❌ 筛选失败: {r.status_code}")
            
            # 4. 测试详情接口
            first_id = first['id']
            print(f"\n4️⃣  测试详情接口 /api/registrations/{first_id}")
            r = requests.get(f"{BASE_URL}/registrations/{first_id}", headers=headers, timeout=10)
            
            if r.status_code == 200:
                detail = r.json()['data']
                activity = detail.get('activityInfo', {})
                print(f"   ✅ 详情请求成功")
                print(f"      - methodCode: {activity.get('methodCode')}")
                print(f"      - methodLabel: {activity.get('methodLabel')}")
                print(f"      - subjectTypeCode: {activity.get('subjectTypeCode')}")
                print(f"      - subjectTypeLabel: {activity.get('subjectTypeLabel')}")
            else:
                print(f"   ❌ 详情请求失败: {r.status_code}")
    else:
        print(f"   ❌ 请求失败: {r.status_code}")
        if r.status_code == 401:
            print("   ⚠️  仍然返回 401，权限问题未修复")
        print(f"   响应: {r.text[:200]}")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
