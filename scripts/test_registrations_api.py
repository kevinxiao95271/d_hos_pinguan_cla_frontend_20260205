#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试各种报名相关的 API
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

def login():
    """登录获取 token"""
    payload = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN",
        "title": "组委会成员",
        "institutionId": None,
        "reviewerGroupCode": None,
        "interviewGroupCode": None,
        "expertBackground": None
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            return data["data"].get("token")
    return None

def test_api(token, method, url, params=None, data=None):
    """通用API测试函数"""
    print(f"\n[测试] {method.upper()} {url}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        if method.lower() == 'get':
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method.lower() == 'post':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"[状态码] {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[成功] {result.get('message', 'OK')}")
            if result.get('data'):
                if isinstance(result['data'], list):
                    print(f"[数据] 列表，共 {len(result['data'])} 条")
                    if len(result['data']) > 0:
                        print(f"[示例] {json.dumps(result['data'][0], ensure_ascii=False)[:200]}...")
                else:
                    print(f"[数据] {str(result['data'])[:200]}...")
            return True
        elif response.status_code == 401:
            print(f"[失败] 401 未授权")
            print(f"[响应] {response.text}")
            return False
        elif response.status_code == 404:
            print(f"[失败] 404 API不存在")
            return False
        else:
            print(f"[失败] HTTP {response.status_code}")
            print(f"[响应] {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"[异常] {str(e)}")
        return False

def main():
    print("="*60)
    print("报名 API 全面测试")
    print("="*60)
    
    token = login()
    if not token:
        print("[错误] 登录失败")
        return
    
    print(f"[Token] {token[:30]}...")
    
    # 测试各种 API 端点
    apis = [
        # 1. 通用报名列表
        ("GET", f"{BASE_URL}/registrations", None, None),
        
        # 2. 按赛事获取报名列表（尝试不同参数）
        ("GET", f"{BASE_URL}/registrations", {"competitionId": 21}, None),
        
        # 3. Admin 筛选接口
        ("GET", f"{BASE_URL}/admin/registrations/filter", {"competitionId": 21}, None),
        
        # 4. 尝试获取所有报名（没有参数）
        ("GET", f"{BASE_URL}/admin/registrations", None, None),
        
        # 5. 尝试获取竞赛的报名统计
        ("GET", f"{BASE_URL}/admin/competitions/21/registrations", None, None),
        
        # 6. 尝试通过竞赛ID获取
        ("GET", f"{BASE_URL}/competitions/21/registrations", None, None),
    ]
    
    results = {}
    for method, url, params, data in apis:
        success = test_api(token, method, url, params, data)
        results[url] = success
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    for url, success in results.items():
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {url}")
    
    print("\n建议:")
    working_apis = [url for url, success in results.items() if success]
    if working_apis:
        print(f"可用的 API: {working_apis[0]}")
    else:
        print("没有找到可用的报名列表 API，可能需要后端开发人员确认")

if __name__ == "__main__":
    main()
