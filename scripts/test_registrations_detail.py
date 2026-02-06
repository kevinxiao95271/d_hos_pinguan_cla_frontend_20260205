#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试报名列表接口
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

def test():
    print("="*70)
    print("详细测试报名列表接口")
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
    if not data.get("success"):
        print(f"[FAIL] Login failed: {data.get('message')}")
        return
    
    token = data["data"]["token"]
    print(f"[OK] Login successful! Token: {token[:30]}...")
    
    # 2. 测试不同的 competitionId
    print("\n" + "="*70)
    print("[Step 2] 测试不同的 competitionId")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for comp_id in [1, 21]:
        print(f"\n--- Testing competitionId={comp_id} ---")
        
        url = f"{BASE_URL}/registrations?competitionId={comp_id}"
        print(f"[URL] {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"[Status] {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"[Response] success={data.get('success')}")
                
                if data.get("success"):
                    registrations = data.get("data", [])
                    count = len(registrations)
                    print(f"[Data] {count} registrations")
                    
                    if count > 0:
                        print(f"\n[Sample] First registration:")
                        first = registrations[0]
                        print(f"  - id: {first.get('id')}")
                        print(f"  - projectName: {first.get('projectName')}")
                        print(f"  - groupType: {first.get('groupType')}")
                        print(f"  - status: {first.get('status')}")
                        print(f"\n[Full] {json.dumps(first, ensure_ascii=False, indent=2)}")
                    else:
                        print(f"[INFO] Empty array returned")
                else:
                    print(f"[FAIL] success=false, message={data.get('message')}")
            else:
                print(f"[FAIL] HTTP {response.status_code}")
                print(f"[Response] {response.text[:200]}")
        except Exception as e:
            print(f"[ERROR] {str(e)}")
    
    # 3. 测试带参数的请求
    print("\n" + "="*70)
    print("[Step 3] 测试带筛选参数的请求")
    print("="*70)
    
    params = {
        "competitionId": 21,
        "groupType": "BASIC"
    }
    
    url = f"{BASE_URL}/registrations"
    print(f"[URL] {url}")
    print(f"[Params] {json.dumps(params)}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"[Status] {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                count = len(data.get("data", []))
                print(f"[Result] {count} registrations with groupType=BASIC")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
    
    # 4. 总结
    print("\n" + "="*70)
    print("总结")
    print("="*70)
    print("\n如果 competitionId=21 返回数据，而前端显示'暂无数据'，")
    print("请检查前端发送的实际请求参数（Network 标签）")

if __name__ == "__main__":
    test()
