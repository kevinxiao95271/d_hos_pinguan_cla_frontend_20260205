#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试"我的报名"API返回数据结构
检查是否返回项目ID (registrationId 或 id)
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

# 测试账号 - 参赛者
TEST_ACCOUNTS = [
    {
        "phone": "13300005566",
        "password": "test005566",
        "role": "参赛者",
        "desc": "参赛者测试账号"
    }
]

def login(phone, password):
    """登录获取token"""
    url = f"{BASE_URL}/auth/login-with-password"
    data = {
        "phone": phone,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('data', {}).get('token')
                return token
            else:
                print(f"  [ERROR] Login failed: {result.get('message')}")
                return None
        else:
            print(f"  [ERROR] HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"  [ERROR] Exception: {str(e)}")
        return None

def test_my_registrations_api(token):
    """测试我的报名API"""
    url = f"{BASE_URL}/registrations/my"
    
    print(f"\n{'='*80}")
    print(f"[API] GET {url}")
    print(f"{'='*80}")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"[OK] HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n[Response] Full Structure:")
            print(json.dumps(result, ensure_ascii=False, indent=2)[:1000])
            print("...")
            
            if result.get('success'):
                data = result.get('data', [])
                print(f"\n[Data] Statistics:")
                print(f"   Record Count: {len(data)}")
                
                if data and len(data) > 0:
                    print(f"\n[Check] First Item Fields:")
                    first_item = data[0]
                    
                    # Check key fields
                    print(f"\n   [Project ID Fields]")
                    print(f"   - id: {first_item.get('id')} {type(first_item.get('id')).__name__}")
                    print(f"   - registrationId: {first_item.get('registrationId')} (exists: {('registrationId' in first_item)})")
                    print(f"   - projectId: {first_item.get('projectId')} (exists: {('projectId' in first_item)})")
                    
                    print(f"\n   [Other Key Fields]")
                    print(f"   - projectName: {first_item.get('projectName')}")
                    print(f"   - competitionId: {first_item.get('competitionId')}")
                    print(f"   - competitionName: {first_item.get('competitionName')}")
                    print(f"   - institutionId: {first_item.get('institutionId')}")
                    print(f"   - institutionName: {first_item.get('institutionName')}")
                    print(f"   - groupType: {first_item.get('groupType')}")
                    print(f"   - status: {first_item.get('status')}")
                    
                    print(f"\n   [All Fields]")
                    all_keys = list(first_item.keys())
                    for i, key in enumerate(all_keys, 1):
                        value = first_item.get(key)
                        value_type = type(value).__name__
                        value_preview = str(value)[:50] if value else 'null'
                        print(f"   {i:2d}. {key:30s} ({value_type:10s}): {value_preview}")
                    
                    # Key analysis
                    print(f"\n{'='*80}")
                    print(f"[Conclusion] Key Findings:")
                    print(f"{'='*80}")
                    
                    has_id = 'id' in first_item
                    has_registration_id = 'registrationId' in first_item
                    has_project_id = 'projectId' in first_item
                    
                    print(f"\n1. Project ID Field Existence:")
                    print(f"   - id: {'[YES]' if has_id else '[NO]'}")
                    if has_id:
                        print(f"     Value: {first_item.get('id')}")
                    
                    print(f"   - registrationId: {'[YES]' if has_registration_id else '[NO]'}")
                    if has_registration_id:
                        print(f"     Value: {first_item.get('registrationId')}")
                    
                    print(f"   - projectId: {'[YES]' if has_project_id else '[NO]'}")
                    if has_project_id:
                        print(f"     Value: {first_item.get('projectId')}")
                    
                    print(f"\n2. Available Fields for Project Identification:")
                    if has_id:
                        print(f"   [OK] Can use 'id' field (value: {first_item.get('id')})")
                    if has_registration_id:
                        print(f"   [OK] Can use 'registrationId' field (value: {first_item.get('registrationId')})")
                    if has_project_id:
                        print(f"   [OK] Can use 'projectId' field (value: {first_item.get('projectId')})")
                    
                    if not (has_id or has_registration_id or has_project_id):
                        print(f"   [WARN] No clear project ID field in outer layer!")
                        print(f"   [ACTION] Backend needs to add 'id' or 'registrationId' field")
                    
                    # Test specific ID
                    print(f"\n3. Search for Project ID 129:")
                    found_129 = False
                    for idx, item in enumerate(data):
                        item_id = item.get('id') or item.get('registrationId')
                        if item_id == 129:
                            found_129 = True
                            print(f"   [FOUND] Project 129 (item #{idx+1})")
                            print(f"      - projectName: {item.get('projectName')}")
                            print(f"      - id: {item.get('id')}")
                            print(f"      - registrationId: {item.get('registrationId')}")
                            print(f"      - status: {item.get('status')}")
                            break
                    
                    if not found_129:
                        print(f"   [NOT FOUND] Project 129 not found in {len(data)} records")
                        print(f"   [List] Existing Project IDs:")
                        for idx, item in enumerate(data[:10]):  # Show first 10
                            item_id = item.get('id') or item.get('registrationId')
                            project_name = item.get('projectName', 'Unknown')
                            print(f"      {idx+1}. ID={item_id}, Name={project_name}")
                        if len(data) > 10:
                            print(f"      ... and {len(data)-10} more")
                    
                else:
                    print(f"\n   [WARN] Empty data array")
            else:
                print(f"\n   [ERROR] API failed: {result.get('message')}")
        else:
            print(f"\n[ERROR] Request failed: {response.text}")
    
    except requests.exceptions.Timeout:
        print(f"[ERROR] Request timeout (30s)")
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")

def main():
    print("="*80)
    print("My Registrations API - Project ID Field Check")
    print("="*80)
    
    # Use contestant account
    account = TEST_ACCOUNTS[0]
    print(f"\n[Account] {account['phone']} ({account['desc']})")
    
    # Login
    token = login(account['phone'], account['password'])
    
    if token:
        print(f"[OK] Login successful")
        # Test my registrations API
        test_my_registrations_api(token)
    else:
        print(f"[ERROR] Login failed, cannot continue")
    
    print(f"\n{'='*80}")
    print(f"[OK] Test completed")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
