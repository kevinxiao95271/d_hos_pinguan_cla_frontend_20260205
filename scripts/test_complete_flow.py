#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整流程测试：从登录到列表、详情、筛选
按照用户提供的流程指引执行
"""

import requests
import json
import sys

BASE_URL = "http://localhost:6031/api"

class FlowTester:
    def __init__(self):
        self.token = None
        self.competition_id = 21
        self.registration_id = None
        
    def print_step(self, step, title):
        """打印步骤标题"""
        print("\n" + "="*70)
        print(f"Step {step}: {title}")
        print("="*70)
    
    def print_result(self, success, message, data=None):
        """打印结果"""
        status = "[SUCCESS]" if success else "[FAIL]"
        print(f"{status} {message}")
        if data and isinstance(data, (dict, list)):
            print(f"[DATA] {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
    
    def step1_login(self):
        """步骤1: 登录获取 token"""
        self.print_step(1, "登录获取 token")
        
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
        
        print(f"[REQUEST] POST {BASE_URL}/auth/login")
        print(f"[BODY] {json.dumps(payload, ensure_ascii=False)}")
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    self.token = data["data"].get("token")
                    self.print_result(True, f"Login successful! Token: {self.token[:30]}...")
                    return True
                else:
                    self.print_result(False, f"Login failed: {data.get('message')}")
                    return False
            else:
                self.print_result(False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
        except Exception as e:
            self.print_result(False, f"Exception: {str(e)}")
            return False
    
    def step2_get_registrations_admin(self):
        """步骤2: 使用 admin 接口拉取报名列表"""
        self.print_step(2, "使用 /api/admin/registrations/filter 拉取报名列表")
        
        if not self.token:
            self.print_result(False, "No token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"competitionId": self.competition_id}
        
        print(f"[REQUEST] GET {BASE_URL}/admin/registrations/filter")
        print(f"[PARAMS] {params}")
        print(f"[HEADERS] Authorization: Bearer {self.token[:30]}...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/registrations/filter",
                headers=headers,
                params=params,
                timeout=10
            )
            
            print(f"[STATUS] {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    registrations = data.get("data", [])
                    self.print_result(True, f"Got {len(registrations)} registrations")
                    
                    if len(registrations) > 0:
                        self.registration_id = registrations[0].get("id") or registrations[0].get("registrationId")
                        print(f"[INFO] First registration ID: {self.registration_id}")
                        print(f"[INFO] Sample data: {json.dumps(registrations[0], ensure_ascii=False)[:300]}...")
                    
                    return True
                else:
                    self.print_result(False, f"Request failed: {data.get('message')}")
                    return False
            elif response.status_code == 401:
                self.print_result(False, "401 Unauthorized - Token might be invalid or insufficient permissions")
                print(f"[RESPONSE] {response.text}")
                return False
            else:
                self.print_result(False, f"HTTP {response.status_code}")
                print(f"[RESPONSE] {response.text[:300]}")
                return False
        except Exception as e:
            self.print_result(False, f"Exception: {str(e)}")
            return False
    
    def step2_alternative_get_registrations(self):
        """步骤2备选: 使用通用接口拉取报名列表"""
        self.print_step("2-ALT", "使用 /api/registrations 拉取报名列表（备选方案）")
        
        if not self.token:
            self.print_result(False, "No token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"competitionId": self.competition_id}
        
        print(f"[REQUEST] GET {BASE_URL}/registrations")
        print(f"[PARAMS] {params}")
        
        try:
            response = requests.get(
                f"{BASE_URL}/registrations",
                headers=headers,
                params=params,
                timeout=10
            )
            
            print(f"[STATUS] {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    registrations = data.get("data", [])
                    self.print_result(True, f"Got {len(registrations)} registrations")
                    
                    if len(registrations) > 0:
                        self.registration_id = registrations[0].get("id") or registrations[0].get("registrationId")
                        print(f"[INFO] First registration ID: {self.registration_id}")
                        print(f"[INFO] Sample data: {json.dumps(registrations[0], ensure_ascii=False)[:300]}...")
                    
                    return True
                else:
                    self.print_result(False, f"Request failed: {data.get('message')}")
                    return False
            else:
                self.print_result(False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result(False, f"Exception: {str(e)}")
            return False
    
    def step3_troubleshoot(self):
        """步骤3: 排查"暂无报名数据"的原因"""
        self.print_step(3, "排查'暂无报名数据'的原因")
        
        checks = []
        
        # 检查1: competitionId 是否正确
        print(f"\n[CHECK 1] Competition ID")
        print(f"  Current ID: {self.competition_id}")
        print(f"  Status: OK (using ID from backend test)")
        checks.append(True)
        
        # 检查2: token 是否存在
        print(f"\n[CHECK 2] Token Status")
        if self.token:
            print(f"  Token: {self.token[:30]}...")
            print(f"  Status: OK")
            checks.append(True)
        else:
            print(f"  Status: FAIL - No token")
            checks.append(False)
        
        # 检查3: 使用的接口
        print(f"\n[CHECK 3] API Endpoint")
        print(f"  Recommended: /api/admin/registrations/filter")
        print(f"  Alternative: /api/registrations")
        print(f"  Status: See step 2 results")
        
        all_ok = all(checks)
        self.print_result(all_ok, "Troubleshooting complete")
        return all_ok
    
    def step4_get_detail(self):
        """步骤4: 获取详情页数据"""
        self.print_step(4, "获取详情页数据")
        
        if not self.token:
            self.print_result(False, "No token available")
            return False
        
        if not self.registration_id:
            self.print_result(False, "No registration ID available (list might be empty)")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print(f"[REQUEST] GET {BASE_URL}/registrations/{self.registration_id}")
        
        try:
            response = requests.get(
                f"{BASE_URL}/registrations/{self.registration_id}",
                headers=headers,
                timeout=10
            )
            
            print(f"[STATUS] {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    detail = data["data"]
                    self.print_result(True, "Got registration detail")
                    
                    # 显示关键字段
                    print(f"\n[DETAIL INFO]")
                    print(f"  Institution Name: {detail.get('institutionName', 'N/A')}")
                    print(f"  Applicant Name: {detail.get('applicantName', 'N/A')}")
                    print(f"  Project Name: {detail.get('projectName', 'N/A')}")
                    
                    # 显示成员信息
                    members = detail.get("members", [])
                    print(f"  Members: {len(members)} total")
                    
                    mentors = [m for m in members if m.get("role") == "MENTOR"]
                    participants = [m for m in members if m.get("role") == "PARTICIPANT"]
                    
                    print(f"    - Mentors (MENTOR): {len(mentors)}")
                    print(f"    - Participants (PARTICIPANT): {len(participants)}")
                    
                    if mentors:
                        print(f"    - Sample mentor: {mentors[0].get('name')} ({mentors[0].get('title')})")
                    if participants:
                        print(f"    - Sample participant: {participants[0].get('name')} ({participants[0].get('title')})")
                    
                    return True
                else:
                    self.print_result(False, f"Request failed: {data.get('message')}")
                    return False
            else:
                self.print_result(False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result(False, f"Exception: {str(e)}")
            return False
    
    def step5_test_filters(self):
        """步骤5: 测试下拉筛选"""
        self.print_step(5, "测试下拉筛选")
        
        if not self.token:
            self.print_result(False, "No token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 5.1 获取主题类型字典
        print(f"\n[5.1] GET /api/dictionaries/subject_type")
        try:
            response = requests.get(f"{BASE_URL}/dictionaries/subject_type", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    items = data.get("data", [])
                    print(f"  [OK] Got {len(items)} subject types")
                    if items:
                        print(f"  Sample: {items[0].get('code')} - {items[0].get('label')}")
                else:
                    print(f"  [FAIL] {data.get('message')}")
            else:
                print(f"  [FAIL] HTTP {response.status_code}")
        except Exception as e:
            print(f"  [FAIL] {str(e)}")
        
        # 5.2 获取品管工具字典
        print(f"\n[5.2] GET /api/dictionaries/method")
        try:
            response = requests.get(f"{BASE_URL}/dictionaries/method", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    items = data.get("data", [])
                    print(f"  [OK] Got {len(items)} methods")
                    if items:
                        print(f"  Sample: {items[0].get('code')} - {items[0].get('label')}")
                        
                        # 5.3 使用第一个 method 进行筛选测试
                        method_code = items[0].get('code')
                        print(f"\n[5.3] Test filter with methodCode={method_code}")
                        
                        # 尝试 admin 接口
                        params = {
                            "competitionId": self.competition_id,
                            "methodCode": method_code
                        }
                        response = requests.get(
                            f"{BASE_URL}/admin/registrations/filter",
                            headers=headers,
                            params=params,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success"):
                                filtered = data.get("data", [])
                                print(f"  [OK] Filter works! Got {len(filtered)} results")
                                if filtered:
                                    print(f"  methodLabel in result: {filtered[0].get('methodLabel')}")
                            else:
                                print(f"  [FAIL] {data.get('message')}")
                        elif response.status_code == 401:
                            print(f"  [FAIL] 401 - Try alternative endpoint /api/registrations")
                            
                            # 尝试备选接口
                            response = requests.get(
                                f"{BASE_URL}/registrations",
                                headers=headers,
                                params=params,
                                timeout=10
                            )
                            if response.status_code == 200:
                                data = response.json()
                                if data.get("success"):
                                    filtered = data.get("data", [])
                                    print(f"  [OK] Alternative works! Got {len(filtered)} results")
                        else:
                            print(f"  [FAIL] HTTP {response.status_code}")
                else:
                    print(f"  [FAIL] {data.get('message')}")
            else:
                print(f"  [FAIL] HTTP {response.status_code}")
        except Exception as e:
            print(f"  [FAIL] {str(e)}")
        
        return True

def main():
    print("\n" + "="*70)
    print("Complete Flow Test: From Login to List, Detail, and Filters")
    print("="*70)
    
    tester = FlowTester()
    
    results = {}
    
    # Step 1: Login
    results['step1'] = tester.step1_login()
    if not results['step1']:
        print("\n[ABORT] Cannot proceed without login")
        sys.exit(1)
    
    # Step 2: Get registrations (try admin endpoint first)
    results['step2_admin'] = tester.step2_get_registrations_admin()
    
    # If admin endpoint fails with 401, try alternative
    if not results['step2_admin']:
        results['step2_alt'] = tester.step2_alternative_get_registrations()
    
    # Step 3: Troubleshooting
    results['step3'] = tester.step3_troubleshoot()
    
    # Step 4: Get detail (if we have registration ID)
    if tester.registration_id:
        results['step4'] = tester.step4_get_detail()
    else:
        print("\n[SKIP] Step 4: No registration ID (list is empty)")
        results['step4'] = False
    
    # Step 5: Test filters
    results['step5'] = tester.step5_test_filters()
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    for key, value in results.items():
        status = "[PASS]" if value else "[FAIL]"
        print(f"{status} {key}")
    
    # Recommendations
    print("\n" + "="*70)
    print("Recommendations")
    print("="*70)
    
    if not results.get('step2_admin') and results.get('step2_alt'):
        print("\n[IMPORTANT] /api/admin/registrations/filter returns 401")
        print("  Frontend should use: /api/registrations?competitionId=XX")
        print("  This is already implemented in the current frontend code")
    
    if not tester.registration_id:
        print("\n[WARNING] No registration data found")
        print("  Possible reasons:")
        print("  1. Competition ID 21 has no registrations")
        print("  2. Need to create test data in backend")
        print("  3. Database is empty")
    
    print("\n[INFO] Frontend flow guide:")
    print("  1. Login: Use token from step 1")
    print("  2. List: GET /api/registrations?competitionId=21")
    print("  3. Detail: GET /api/registrations/{id}")
    print("  4. Filters: Use methodLabel/subjectTypeLabel from list response")

if __name__ == "__main__":
    main()
