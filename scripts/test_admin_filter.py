#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新测试 /api/admin/registrations/filter 接口
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

def test():
    print("="*70)
    print("测试 Admin Filter 接口")
    print("="*70)
    
    # 1. 登录
    print("\n[Step 1] 登录...")
    payload = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Committee Member",
        "role": "COMMITTEE_ADMIN",
        "institutionId": None,
        "reviewerGroupCode": None,
        "interviewGroupCode": None,
        "expertBackground": None
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
    if response.status_code != 200:
        print(f"[FAIL] Login failed: {response.status_code}")
        return
    
    data = response.json()
    token = data["data"]["token"]
    print(f"[OK] Login successful! Token: {token[:30]}...")
    
    # 2. 测试 Admin Filter 接口
    print("\n" + "="*70)
    print("[Step 2] 测试 /api/admin/registrations/filter")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"competitionId": 21}
    
    url = f"{BASE_URL}/admin/registrations/filter"
    print(f"[URL] {url}")
    print(f"[Params] {params}")
    print(f"[Headers] Authorization: Bearer {token[:30]}...")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"\n[Status] {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[Response] success={data.get('success')}")
            
            if data.get("success"):
                registrations = data.get("data", [])
                count = len(registrations)
                print(f"[Data] {count} registrations")
                
                if count > 0:
                    first = registrations[0]
                    
                    print("\n" + "="*70)
                    print("第一条数据的所有字段：")
                    print("="*70)
                    for key in sorted(first.keys()):
                        value = first[key]
                        str_value = str(value)
                        if len(str_value) > 50:
                            str_value = str_value[:50] + "..."
                        print(f"  {key:30} = {str_value}")
                    
                    print("\n" + "="*70)
                    print("检查关键字段：")
                    print("="*70)
                    
                    needed = {
                        'registrationId': '项目编号',
                        'institutionName': '医疗机构名称',
                        'methodLabel': '品管工具',
                        'applicantName': '报名人'
                    }
                    
                    all_found = True
                    for field, name in needed.items():
                        if field in first:
                            print(f"  [OK] {field:30} = {first[field]} ({name})")
                        else:
                            print(f"  [MISSING] {field:30} ({name})")
                            all_found = False
                    
                    if all_found:
                        print("\n[SUCCESS] 所有关键字段都存在！")
                        print("[INFO] 前端应该使用这个接口：/api/admin/registrations/filter")
                    else:
                        print("\n[WARNING] 有字段缺失")
                    
                    print("\n" + "="*70)
                    print("完整 JSON：")
                    print("="*70)
                    print(json.dumps(first, ensure_ascii=False, indent=2))
                else:
                    print("[INFO] 返回空数组")
            else:
                print(f"[FAIL] success=false, message={data.get('message')}")
        elif response.status_code == 401:
            print("[FAIL] 401 Unauthorized")
            print(f"[Response] {response.text}")
            print("\n[建议] 可能需要重启后端服务")
        else:
            print(f"[FAIL] HTTP {response.status_code}")
            print(f"[Response] {response.text[:300]}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    test()
