#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试不同的接口端点，寻找完整的字段
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

def print_fields(data, title):
    """打印字段"""
    print(f"\n{'='*70}")
    print(title)
    print('='*70)
    if isinstance(data, dict):
        for key, value in data.items():
            # 截断长值
            str_value = str(value)
            if len(str_value) > 50:
                str_value = str_value[:50] + "..."
            print(f"  {key:30} = {str_value}")
    else:
        print("Not a dict:", type(data))

def test():
    # 登录
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
    token = response.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试不同的接口
    endpoints = [
        ("GET /api/registrations (no params)", f"{BASE_URL}/registrations", {}),
        ("GET /api/registrations?competitionId=21", f"{BASE_URL}/registrations", {"competitionId": 21}),
        ("GET /api/admin/registrations/filter", f"{BASE_URL}/admin/registrations/filter", {"competitionId": 21}),
    ]
    
    for title, url, params in endpoints:
        print(f"\n\n{'#'*70}")
        print(f"Testing: {title}")
        print(f"URL: {url}")
        print(f"Params: {params}")
        print('#'*70)
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    items = data["data"]
                    if isinstance(items, list) and len(items) > 0:
                        print(f"Count: {len(items)}")
                        print_fields(items[0], "First item fields:")
                        
                        # 检查是否有我们需要的字段
                        first = items[0]
                        needed_fields = {
                            'registrationId': 'Registration ID',
                            'institutionName': 'Institution Name',
                            'methodLabel': 'Method Label',
                            'applicantName': 'Applicant Name'
                        }
                        
                        print(f"\n[Check] Needed fields:")
                        for field, desc in needed_fields.items():
                            if field in first:
                                print(f"  [OK] {field:30} = {first[field]}")
                            else:
                                print(f"  [MISSING] {field:30}")
                    else:
                        print("Empty list or not a list")
                else:
                    print(f"success=false or no data: {data}")
            elif response.status_code == 401:
                print("401 Unauthorized - Need different role or token")
            else:
                print(f"Error: {response.text[:200]}")
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test()
