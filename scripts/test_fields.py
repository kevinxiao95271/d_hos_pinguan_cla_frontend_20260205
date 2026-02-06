#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查接口返回的字段名
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

def test():
    # 1. 登录
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
    
    # 2. 获取报名列表
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/registrations?competitionId=21", headers=headers, timeout=10)
    
    data = response.json()
    
    if data.get("success") and data.get("data"):
        registrations = data["data"]
        
        print("="*70)
        print("接口返回的第一条数据的所有字段：")
        print("="*70)
        
        first = registrations[0]
        
        # 打印所有字段
        for key, value in first.items():
            print(f"{key:30} = {value}")
        
        print("\n" + "="*70)
        print("关键字段检查：")
        print("="*70)
        
        # 检查关键字段
        fields_to_check = [
            ('项目编号', ['registrationId', 'id', 'projectId', 'code', 'registrationCode']),
            ('医疗机构名称', ['institutionName', 'institution', 'hospitalName']),
            ('品管工具', ['methodLabel', 'method', 'methodName', 'tool']),
            ('报名人', ['applicantName', 'applicant', 'submitter', 'createdBy'])
        ]
        
        for field_cn, possible_keys in fields_to_check:
            print(f"\n【{field_cn}】可能的字段名：")
            found = False
            for key in possible_keys:
                if key in first:
                    print(f"  ✓ {key:30} = {first[key]}")
                    found = True
            if not found:
                print(f"  ✗ 未找到匹配的字段")
        
        print("\n" + "="*70)
        print("完整数据（JSON格式）：")
        print("="*70)
        print(json.dumps(first, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test()
