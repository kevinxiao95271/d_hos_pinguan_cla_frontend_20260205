#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试评委列表API的分页功能
检查改变size参数是否真的生效
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"
TIMEOUT = 10

def login():
    """登录组委会账号"""
    url = f"{BASE_URL}/auth/login-with-password"
    data = {"phone": "13800000127", "password": "committee2026"}
    
    print("🔐 登录组委会账号...")
    try:
        response = requests.post(url, json=data, timeout=TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 登录成功\n")
                return result['data']['token']
    except Exception as e:
        print(f"❌ 登录失败: {e}\n")
    return None

def test_pagination(token):
    """测试不同的分页参数"""
    url = f"{BASE_URL}/admin/reviewers"
    headers = {"Authorization": f"Bearer {token}"}
    
    test_cases = [
        {"name": "默认（无参数）", "params": {"competitionId": 1}},
        {"name": "每页10条", "params": {"competitionId": 1, "page": 0, "size": 10}},
        {"name": "每页20条", "params": {"competitionId": 1, "page": 0, "size": 20}},
        {"name": "每页50条", "params": {"competitionId": 1, "page": 0, "size": 50}},
        {"name": "每页100条", "params": {"competitionId": 1, "page": 0, "size": 100}},
        {"name": "每页200条", "params": {"competitionId": 1, "page": 0, "size": 200}},
        {"name": "第2页，每页50条", "params": {"competitionId": 1, "page": 1, "size": 50}},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print("="*60)
        print(f"测试 {i}: {test_case['name']}")
        print("="*60)
        print(f"参数: {json.dumps(test_case['params'], ensure_ascii=False)}")
        
        try:
            response = requests.get(url, headers=headers, params=test_case['params'], timeout=TIMEOUT)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    data = result.get('data', [])
                    
                    # 判断数据格式
                    if isinstance(data, dict):
                        # 分页格式
                        content = data.get('content', [])
                        total = data.get('totalElements', 0)
                        page_no = data.get('pageNo', 0)
                        page_size = data.get('pageSize', 0)
                        total_pages = data.get('totalPages', 0)
                        
                        print(f"✅ 分页格式")
                        print(f"  - 总记录数: {total}")
                        print(f"  - 当前页: {page_no}")
                        print(f"  - 每页大小: {page_size}")
                        print(f"  - 总页数: {total_pages}")
                        print(f"  - 实际返回: {len(content)} 条")
                        
                        if len(content) > 0:
                            print(f"  - 第一条ID: {content[0].get('id')}")
                            print(f"  - 最后一条ID: {content[-1].get('id')}")
                    elif isinstance(data, list):
                        # 数组格式（不支持分页）
                        print(f"⚠️ 数组格式（不支持分页）")
                        print(f"  - 返回: {len(data)} 条")
                        
                        if len(data) > 0:
                            print(f"  - 第一条ID: {data[0].get('id')}")
                            print(f"  - 最后一条ID: {data[-1].get('id')}")
                    else:
                        print(f"❌ 未知格式: {type(data)}")
                else:
                    print(f"❌ 失败: {result.get('message')}")
            else:
                print(f"❌ 状态码: {response.status_code}")
                print(f"响应: {response.text[:200]}")
        except Exception as e:
            print(f"❌ 异常: {e}")
        
        print()

def main():
    print("="*60)
    print("测试评委列表API的分页功能")
    print("="*60)
    print()
    
    token = login()
    if not token:
        print("❌ 无法获取token，测试终止")
        return
    
    test_pagination(token)
    
    print("="*60)
    print("测试完成")
    print("="*60)
    print()
    print("结论:")
    print("- 如果所有测试都返回相同数量的数据，说明API不支持分页")
    print("- 如果返回的是数组格式，说明后端没有实现分页")
    print("- 如果返回的是分页格式但数量不变，说明后端忽略了size参数")

if __name__ == "__main__":
    main()
