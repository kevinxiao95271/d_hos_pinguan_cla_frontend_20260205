#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MinIO相关API接口
对比实际返回与文档预期的差异
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:6031/api"

# 测试账号
TEST_ACCOUNTS = {
    "contestant": {
        "phone": "13300005566",
        "password": "test005566",
        "role": "参赛者"
    },
    "ops": {
        "phone": "admin",
        "password": "admin123",
        "role": "OPS运维"
    }
}

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

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
                token = result['data'].get('token')
                print(f"[OK] Login successful - Role: {result['data'].get('role')}")
                return token
            else:
                print(f"[ERROR] Login failed: {result.get('message')}")
                return None
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Login exception: {e}")
        return None

def test_get_active_templates():
    """测试1: 获取有效模版列表（公开接口）"""
    print_section("Test 1: GET /api/system-templates/active (Public API)")
    
    url = f"{BASE_URL}/system-templates/active"
    
    print(f"\n[Request] GET {url}")
    print("[Expected] Public API - No token required")
    print("[Expected] Response format:")
    print("""
    {
      "code": 200,
      "message": "success",
      "data": [
        {
          "id": 1,
          "templateType": "registration_form",
          "fileName": "xxx.docx",
          "fileSize": 16967,
          "version": 1,
          "isActive": true,
          "uploadedBy": null,
          "uploadedAt": "2026-02-27T16:00:00",
          "description": null
        }
      ]
    }
    """)
    
    try:
        # 不带token测试（公开接口）
        response = requests.get(url, timeout=30)
        print(f"\n[Actual] HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[Actual] Response structure:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 检查响应格式
            print("\n[Validation]")
            if 'success' in result:
                print("  [OK] Has 'success' field")
            else:
                print("  [DIFF] Missing 'success' field - Document expects 'code' field")
            
            if 'data' in result:
                print("  [OK] Has 'data' field")
                if isinstance(result['data'], list):
                    print(f"  [OK] data is array with {len(result['data'])} items")
                    
                    if len(result['data']) > 0:
                        first_item = result['data'][0]
                        required_fields = ['id', 'templateType', 'fileName', 'version', 'isActive']
                        for field in required_fields:
                            if field in first_item:
                                print(f"  [OK] Has '{field}': {first_item[field]}")
                            else:
                                print(f"  [DIFF] Missing '{field}'")
                else:
                    print("  [DIFF] data is not an array")
            else:
                print("  [DIFF] Missing 'data' field")
        
        elif response.status_code == 401:
            print("[DIFF] HTTP 401 - Document says this is a PUBLIC API (no token required)")
            print("[ERROR] API requires authentication but document says it's public")
        else:
            print(f"[ERROR] Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")

def test_download_template():
    """测试2: 下载模版文件（公开接口）"""
    print_section("Test 2: GET /api/system-templates/{id}/download (Public API)")
    
    template_id = 1
    url = f"{BASE_URL}/system-templates/{template_id}/download"
    
    print(f"\n[Request] GET {url}")
    print("[Expected] Public API - No token required")
    print("[Expected] Response: File blob with Content-Disposition header")
    
    try:
        response = requests.get(url, timeout=30, stream=True)
        print(f"\n[Actual] HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            content_disposition = response.headers.get('Content-Disposition', '')
            content_length = response.headers.get('Content-Length', '0')
            
            print(f"[OK] Content-Type: {content_type}")
            print(f"[OK] Content-Disposition: {content_disposition}")
            print(f"[OK] Content-Length: {content_length} bytes")
            
            if 'application/octet-stream' in content_type or 'application' in content_type:
                print("[OK] Response is file blob")
            else:
                print(f"[DIFF] Content-Type not as expected: {content_type}")
        
        elif response.status_code == 401:
            print("[DIFF] HTTP 401 - Document says this is a PUBLIC API")
            print("[ERROR] API requires authentication but document says it's public")
        
        elif response.status_code == 404:
            print("[WARNING] Template ID 1 not found - May need to create templates first")
        
        else:
            print(f"[ERROR] Unexpected status code: {response.status_code}")
    
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")

def test_registration_filter_with_materials(token):
    """测试3: 列表查询是否包含materials字段"""
    print_section("Test 3: GET /api/admin/registrations/filter (with materials)")
    
    url = f"{BASE_URL}/admin/registrations/filter"
    params = {
        "competitionId": 1,
        "status": "SUBMITTED"
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"\n[Request] GET {url}")
    print(f"[Params] {params}")
    print("[Expected] Response should include 'materials' field in each item:")
    print("""
    {
      "success": true,
      "data": [
        {
          "registrationId": 123,
          "projectName": "xxx",
          "materials": [
            {
              "id": 456,
              "type": "registration_form",
              "fileName": "xxx.docx",
              "downloadUrl": "/api/materials/456/download"
            }
          ]
        }
      ]
    }
    """)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(f"\n[Actual] HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success') and result.get('data'):
                items = result['data']
                print(f"[OK] Got {len(items)} items")
                
                if len(items) > 0:
                    first_item = items[0]
                    print(f"\n[Check] First item fields:")
                    print(f"  - registrationId: {first_item.get('registrationId', 'N/A')}")
                    print(f"  - projectName: {first_item.get('projectName', 'N/A')}")
                    
                    if 'materials' in first_item:
                        materials = first_item['materials']
                        print(f"  [OK] Has 'materials' field: {len(materials)} files")
                        
                        if len(materials) > 0:
                            print(f"\n[First Material]:")
                            print(json.dumps(materials[0], indent=4, ensure_ascii=False))
                    else:
                        print("  [DIFF] Missing 'materials' field")
                        print("  [ERROR] Backend has NOT implemented materials field in filter API")
                        print("\n[All Fields in first item]:")
                        for key in first_item.keys():
                            print(f"    - {key}")
                else:
                    print("[WARNING] No data in result")
            else:
                print(f"[ERROR] Unexpected response format: {result}")
        
        elif response.status_code == 401:
            print("[ERROR] Unauthorized - Token may be invalid")
        
        else:
            print(f"[ERROR] Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")

def test_material_download_api(token):
    """测试4: 材料下载API"""
    print_section("Test 4: GET /api/materials/{id}/download")
    
    material_id = 1
    url = f"{BASE_URL}/materials/{material_id}/download"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"\n[Request] GET {url}")
    print("[Expected] Requires JWT token")
    print("[Expected] Response: File blob")
    
    try:
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        print(f"\n[Actual] HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            content_disposition = response.headers.get('Content-Disposition', '')
            
            print(f"[OK] Content-Type: {content_type}")
            print(f"[OK] Content-Disposition: {content_disposition}")
            print("[OK] Material download API works")
        
        elif response.status_code == 404:
            print("[WARNING] Material ID 1 not found - May need to upload materials first")
        
        elif response.status_code == 403:
            print("[INFO] Forbidden - Permission check works (user cannot download this material)")
        
        else:
            print(f"[ERROR] Unexpected status code: {response.status_code}")
    
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")

def main():
    print_section("MinIO API Test Suite")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: 公开接口 - 获取有效模版列表
    test_get_active_templates()
    
    # Test 2: 公开接口 - 下载模版文件
    test_download_template()
    
    # Login as contestant to test authenticated APIs
    print_section("Login as Contestant for Authenticated Tests")
    account = TEST_ACCOUNTS['contestant']
    print(f"[Account] {account['phone']} ({account['role']})")
    token = login(account['phone'], account['password'])
    
    if token:
        # Test 3: 列表查询包含materials字段
        test_registration_filter_with_materials(token)
        
        # Test 4: 材料下载API
        test_material_download_api(token)
    else:
        print("\n[SKIP] Tests 3-4 skipped due to login failure")
    
    # Summary
    print_section("Test Summary")
    print("""
[Key Findings]
1. Check if /api/system-templates/active is truly PUBLIC (no token required)
2. Check if response format matches document (code vs success field)
3. Check if /api/admin/registrations/filter includes 'materials' field
4. Check if /api/materials/{id}/download API exists
    """)
    
    print("\n[OK] Test completed")

if __name__ == '__main__':
    main()
