#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试详情接口的字段
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

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
    
    # 获取详情
    registration_id = 106
    url = f"{BASE_URL}/registrations/{registration_id}"
    
    print("="*70)
    print(f"Testing: GET /api/registrations/{registration_id}")
    print("="*70)
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("data"):
            detail = data["data"]
            
            print("\nAll fields in detail:")
            print("-"*70)
            for key in sorted(detail.keys()):
                value = detail[key]
                if isinstance(value, (list, dict)):
                    print(f"  {key:30} = {type(value).__name__} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                else:
                    str_value = str(value)
                    if len(str_value) > 50:
                        str_value = str_value[:50] + "..."
                    print(f"  {key:30} = {str_value}")
            
            print("\n" + "="*70)
            print("Check for needed fields:")
            print("="*70)
            
            needed = {
                'registrationId': '项目编号',
                'institutionId': '机构ID',
                'institutionName': '医疗机构名称',
                'methodCode': '品管工具代码',
                'methodLabel': '品管工具',
                'subjectTypeCode': '主题类型代码',
                'subjectTypeLabel': '主题类型',
                'applicantId': '报名人ID',
                'applicantName': '报名人'
            }
            
            for field, name in needed.items():
                if field in detail:
                    print(f"  [OK] {field:30} ({name})")
                else:
                    print(f"  [MISSING] {field:30} ({name})")
            
            print("\n" + "="*70)
            print("Full JSON:")
            print("="*70)
            print(json.dumps(detail, ensure_ascii=False, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text[:200])

if __name__ == "__main__":
    test()
