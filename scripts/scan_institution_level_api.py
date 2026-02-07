#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描所有涉及机构名称的API，检查是否返回机构等级（level）字段
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def print_safe(text):
    """安全打印"""
    try:
        print(text, flush=True)
    except:
        print(text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'), flush=True)

def login(role, phone, name):
    """登录获取token"""
    login_url = f"{BASE_URL}/api/auth/login"
    payload = {
        "phone": phone,
        "name": name,
        "title": "Title",
        "role": role
    }
    
    try:
        response = requests.post(login_url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data', {}).get('token'):
                token = data['data']['token']
                institution_level = data['data'].get('institutionLevel')
                institution_region = data['data'].get('institutionRegion')
                print_safe(f"  Login successful - institutionLevel: {institution_level}, region: {institution_region}")
                return token, institution_level is not None
            else:
                print_safe(f"  Login failed: {data.get('message', 'Unknown error')}")
                return None, False
        else:
            print_safe(f"  Login failed: {response.status_code}")
            return None, False
    except Exception as e:
        print_safe(f"  Login exception: {str(e)}")
        return None, False

def check_api(name, url, headers, expected_path, role):
    """检查API是否返回机构等级"""
    print_safe(f"\n  API: {url}")
    print_safe(f"  Expected level path: {expected_path}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            # 导航到期望的路径
            current = data
            has_level = False
            level_value = None
            
            try:
                for key in expected_path.split('.'):
                    if '[' in key:  # 处理数组
                        base_key = key.split('[')[0]
                        current = current.get(base_key, [])
                        if current and len(current) > 0:
                            current = current[0]
                    else:
                        current = current.get(key, {})
                
                # 检查是否有level字段
                if isinstance(current, dict):
                    level_value = current.get('level')
                    has_level = level_value is not None
                elif isinstance(current, list) and len(current) > 0:
                    level_value = current[0].get('level')
                    has_level = level_value is not None
                
            except Exception as e:
                print_safe(f"  Path navigation error: {str(e)}")
            
            if has_level:
                print_safe(f"  [OK] Has 'level' field: {level_value}")
                return True
            else:
                print_safe(f"  [MISSING] No 'level' field found")
                print_safe(f"  Response sample: {json.dumps(data, ensure_ascii=False)[:500]}...")
                return False
        else:
            print_safe(f"  API failed: {response.status_code}")
            return False
    except Exception as e:
        print_safe(f"  API exception: {str(e)}")
        return False

def main():
    """主函数"""
    print_safe("\n" + "=" * 80)
    print_safe("Institution Level Field Scan Report")
    print_safe("=" * 80)
    
    results = {
        'login': {},
        'apis': {}
    }
    
    # ==================== 1. 登录接口检查 ====================
    print_safe("\n" + "=" * 80)
    print_safe("1. LOGIN API CHECK")
    print_safe("=" * 80)
    
    test_accounts = [
        ("CONTESTANT", "13966000011", "Contestant 11"),
        ("REVIEWER", "13800000021", "Li Minghua"),
        ("COMMITTEE_ADMIN", "13800000041", "Committee A"),
        ("OPS", "13800000051", "Ops A")
    ]
    
    tokens = {}
    for role, phone, name in test_accounts:
        print_safe(f"\n[{role}] {name} ({phone})")
        token, has_level = login(role, phone, name)
        tokens[role] = token
        results['login'][role] = has_level
    
    # ==================== 2. 参赛者相关API ====================
    print_safe("\n" + "=" * 80)
    print_safe("2. CONTESTANT APIS")
    print_safe("=" * 80)
    
    if tokens.get('CONTESTANT'):
        headers = {"Authorization": f"Bearer {tokens['CONTESTANT']}"}
        
        # 2.1 报名详情
        print_safe("\n[CONTESTANT] Registration Detail")
        results['apis']['registration_detail'] = check_api(
            "Registration Detail",
            f"{BASE_URL}/api/registrations/116",
            headers,
            "data.institution",
            "CONTESTANT"
        )
        
        # 2.2 我的报名列表
        print_safe("\n[CONTESTANT] My Registrations")
        results['apis']['my_registrations'] = check_api(
            "My Registrations",
            f"{BASE_URL}/api/registrations/my",
            headers,
            "data[0]",
            "CONTESTANT"
        )
    
    # ==================== 3. 评审专家相关API ====================
    print_safe("\n" + "=" * 80)
    print_safe("3. REVIEWER APIS")
    print_safe("=" * 80)
    
    if tokens.get('REVIEWER'):
        headers = {"Authorization": f"Bearer {tokens['REVIEWER']}"}
        
        # 3.1 我的评审任务
        print_safe("\n[REVIEWER] My Tasks")
        results['apis']['reviewer_tasks'] = check_api(
            "Reviewer Tasks",
            f"{BASE_URL}/api/reviews/my-tasks",
            headers,
            "data[0]",
            "REVIEWER"
        )
        
        # 3.2 报名详情（评审查看）
        print_safe("\n[REVIEWER] Registration Detail (for review)")
        results['apis']['reviewer_registration_detail'] = check_api(
            "Registration Detail",
            f"{BASE_URL}/api/registrations/106",
            headers,
            "data.institution",
            "REVIEWER"
        )
    
    # ==================== 4. 组委会相关API ====================
    print_safe("\n" + "=" * 80)
    print_safe("4. COMMITTEE APIS")
    print_safe("=" * 80)
    
    if tokens.get('COMMITTEE_ADMIN'):
        headers = {"Authorization": f"Bearer {tokens['COMMITTEE_ADMIN']}"}
        
        # 4.1 报名筛选列表
        print_safe("\n[COMMITTEE] Registration Filter")
        results['apis']['registration_filter'] = check_api(
            "Registration Filter",
            f"{BASE_URL}/api/admin/registrations/filter?competitionId=21",
            headers,
            "data[0]",
            "COMMITTEE_ADMIN"
        )
        
        # 4.2 评审排名列表
        print_safe("\n[COMMITTEE] Review Rankings")
        results['apis']['review_rankings'] = check_api(
            "Review Rankings",
            f"{BASE_URL}/api/admin/reviews/rankings?competitionId=21&stage=BOOK",
            headers,
            "data[0]",
            "COMMITTEE_ADMIN"
        )
        
        # 4.3 评审任务列表（按阶段）
        print_safe("\n[COMMITTEE] Review Tasks by Stage")
        results['apis']['review_tasks_by_stage'] = check_api(
            "Review Tasks by Stage",
            f"{BASE_URL}/api/reviews/tasks/stage?competitionId=21&stage=BOOK",
            headers,
            "data[0]",
            "COMMITTEE_ADMIN"
        )
        
        # 4.4 评审人列表
        print_safe("\n[COMMITTEE] Reviewers List")
        results['apis']['reviewers_list'] = check_api(
            "Reviewers List",
            f"{BASE_URL}/api/admin/reviewers",
            headers,
            "data[0]",
            "COMMITTEE_ADMIN"
        )
    
    # ==================== 5. 系统运维相关API ====================
    print_safe("\n" + "=" * 80)
    print_safe("5. OPS APIS")
    print_safe("=" * 80)
    
    if tokens.get('OPS'):
        headers = {"Authorization": f"Bearer {tokens['OPS']}"}
        
        # 5.1 机构列表
        print_safe("\n[OPS] Institutions List")
        results['apis']['institutions_list'] = check_api(
            "Institutions List",
            f"{BASE_URL}/api/institutions",
            headers,
            "data[0]",
            "OPS"
        )
    
    # ==================== 总结 ====================
    print_safe("\n" + "=" * 80)
    print_safe("SUMMARY")
    print_safe("=" * 80)
    
    print_safe("\n[LOGIN API]")
    for role, has_level in results['login'].items():
        status = "[OK]" if has_level else "[MISSING]"
        print_safe(f"  {status} {role}")
    
    print_safe("\n[DATA APIS]")
    missing_apis = []
    for api_name, has_level in results['apis'].items():
        status = "[OK]" if has_level else "[MISSING]"
        print_safe(f"  {status} {api_name}")
        if not has_level:
            missing_apis.append(api_name)
    
    if missing_apis:
        print_safe("\n" + "!" * 80)
        print_safe("APIS MISSING 'level' FIELD:")
        for api in missing_apis:
            print_safe(f"  - {api}")
        print_safe("!" * 80)
    else:
        print_safe("\n" + "=" * 80)
        print_safe("All APIs have 'level' field!")
        print_safe("=" * 80)

if __name__ == "__main__":
    main()
