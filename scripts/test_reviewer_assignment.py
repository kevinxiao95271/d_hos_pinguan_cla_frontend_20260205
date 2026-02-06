#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评委分配功能 API 测试脚本
测试报名列表、评委列表、手动分配、自动分配等接口
"""

import requests
import json
import sys

BASE_URL = "http://localhost:6031/api"

# 设置控制台输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(success, message, data=None):
    """打印结果"""
    status = "✅" if success else "❌"
    print(f"{status} {message}")
    if data:
        print(f"   数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")

def test_login():
    """测试登录并获取 token"""
    print_section("1. 测试登录 - 获取 Token")
    
    url = f"{BASE_URL}/auth/login"
    payload = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Admin",
        "role": "COMMITTEE_ADMIN"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"请求 URL: {url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('data', {}).get('token')
                print_result(True, "登录成功", {"token": token[:50] + "..." if token else None})
                return token
            else:
                print_result(False, f"登录失败: {result.get('message')}")
                return None
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return None
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return None

def test_registrations_list(token):
    """测试报名列表接口"""
    print_section("2. 测试报名列表 - GET /api/admin/registrations/filter")
    
    url = f"{BASE_URL}/admin/registrations/filter"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试1: 获取所有报名
    print("\n[测试 2.1] 获取所有报名（competitionId=21）")
    params = {"competitionId": 21}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"请求 URL: {url}?competitionId=21")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
                print_result(True, f"获取成功，共 {len(data)} 条报名")
                if len(data) > 0:
                    sample = data[0]
                    print(f"\n   样例数据字段:")
                    print(f"   - registrationId: {sample.get('registrationId')}")
                    print(f"   - projectName: {sample.get('projectName')}")
                    print(f"   - institutionName: {sample.get('institutionName')}")
                    print(f"   - groupType: {sample.get('groupType')}")
                    print(f"   - groupCode: {sample.get('groupCode')}")
                    print(f"   - methodLabel: {sample.get('methodLabel')}")
            else:
                print_result(False, f"获取失败: {result.get('message')}")
        else:
            print_result(False, f"HTTP 错误: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
    
    # 测试2: 按组别筛选（基层组）
    print("\n[测试 2.2] 按组别筛选（groupType=BASIC）")
    params = {"competitionId": 21, "groupType": "BASIC"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"请求 URL: {url}?competitionId=21&groupType=BASIC")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
                print_result(True, f"筛选成功，基层组共 {len(data)} 条")
            else:
                print_result(False, f"筛选失败: {result.get('message')}")
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
    
    # 测试3: 按进阶组筛选（面谈用）
    print("\n[测试 2.3] 按进阶组筛选（groupType=ADVANCED）")
    params = {"competitionId": 21, "groupType": "ADVANCED"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"请求 URL: {url}?competitionId=21&groupType=ADVANCED")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
                print_result(True, f"筛选成功，进阶组共 {len(data)} 条")
            else:
                print_result(False, f"筛选失败: {result.get('message')}")
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")

def test_reviewers_list(token):
    """测试评委列表接口"""
    print_section("3. 测试评委列表 - GET /api/admin/reviewers")
    
    url = f"{BASE_URL}/admin/reviewers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"competitionId": 21}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"请求 URL: {url}?competitionId=21")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {json.dumps(result, ensure_ascii=False)[:500]}")
            
            if result.get('success'):
                data = result.get('data', [])
                print_result(True, f"获取成功，共 {len(data)} 位评委")
                
                if len(data) > 0:
                    sample = data[0]
                    print(f"\n   样例评委字段:")
                    print(f"   - id: {sample.get('id')}")
                    print(f"   - name: {sample.get('name')}")
                    print(f"   - title: {sample.get('title')}")
                    print(f"   - institutionName: {sample.get('institutionName')}")
                    print(f"   - institutionId: {sample.get('institutionId')}")
                    print(f"   - background: {sample.get('background')}")
                    print(f"   - currentLoad: {sample.get('currentLoad')}")
                else:
                    print(f"\n   ⚠️ 警告：评委列表为空！")
                    print(f"   可能原因：")
                    print(f"   1. 数据库中没有评委数据")
                    print(f"   2. 后端接口返回结构不正确")
                    print(f"   3. competitionId 参数无效")
            else:
                print_result(False, f"获取失败: {result.get('message')}")
        else:
            print_result(False, f"HTTP 错误: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")

def test_manual_assign(token):
    """测试手动分配评委"""
    print_section("4. 测试手动分配 - POST /api/admin/reviews/tasks")
    
    url = f"{BASE_URL}/admin/reviews/tasks"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 先获取一个报名ID和评委ID
    print("\n[准备] 获取测试数据...")
    
    # 获取报名ID
    reg_url = f"{BASE_URL}/admin/registrations/filter"
    reg_response = requests.get(reg_url, headers=headers, params={"competitionId": 21}, timeout=30)
    
    registration_id = None
    if reg_response.status_code == 200:
        reg_data = reg_response.json().get('data', [])
        if len(reg_data) > 0:
            registration_id = reg_data[0].get('registrationId')
            print(f"   找到报名ID: {registration_id}")
    
    # 获取评委ID
    rev_url = f"{BASE_URL}/admin/reviewers"
    rev_response = requests.get(rev_url, headers=headers, params={"competitionId": 21}, timeout=30)
    
    reviewer_id = None
    if rev_response.status_code == 200:
        rev_data = rev_response.json().get('data', [])
        if len(rev_data) > 0:
            reviewer_id = rev_data[0].get('id')
            print(f"   找到评委ID: {reviewer_id}")
    
    if not registration_id or not reviewer_id:
        print_result(False, "无法获取测试数据，跳过手动分配测试")
        return
    
    # 测试手动分配
    print(f"\n[测试 4.1] 手动分配评委")
    payload = {
        "registrationId": registration_id,
        "reviewerId": reviewer_id,
        "stage": "BOOK"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"请求 URL: {url}")
        print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_result(True, "手动分配成功")
            else:
                print_result(False, f"分配失败: {result.get('message')}")
        else:
            print_result(False, f"HTTP 错误: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")

def test_auto_assign(token):
    """测试自动分配评委"""
    print_section("5. 测试自动分配 - POST /api/admin/reviews/auto-assign")
    
    url = f"{BASE_URL}/admin/reviews/auto-assign"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "competitionId": 21,
        "stage": "BOOK",
        "reviewersPerRegistration": 2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"请求 URL: {url}")
        print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_result(True, "自动分配成功")
            else:
                print_result(False, f"自动分配失败: {result.get('message')}")
        else:
            print_result(False, f"HTTP 错误: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  评委分配功能 API 测试")
    print("="*60)
    
    # 1. 登录获取 token
    token = test_login()
    if not token:
        print("\n❌ 登录失败，测试终止")
        return
    
    # 2. 测试报名列表
    test_registrations_list(token)
    
    # 3. 测试评委列表
    test_reviewers_list(token)
    
    # 4. 测试手动分配
    test_manual_assign(token)
    
    # 5. 测试自动分配
    # test_auto_assign(token)  # 注释掉，避免重复分配
    
    print_section("测试总结")
    print("""
请检查以上测试结果：

1. 报名列表 API (/api/admin/registrations/filter)
   - 是否返回 200？
   - 数据结构是否包含 registrationId, projectName 等字段？
   - 筛选功能是否正常？

2. 评委列表 API (/api/admin/reviewers)
   ⚠️  重点检查：
   - 是否返回 200？
   - data 数组是否为空？
   - 如果为空，数据库中是否有评委数据？
   - 返回字段是否包含 id, name, institutionName, background, currentLoad？

3. 手动分配 API (/api/admin/reviews/tasks)
   - 是否支持创建评审任务？
   - 冲突检测是否正常？

4. 自动分配 API (/api/admin/reviews/auto-assign)
   - 是否支持批量分配？
   - 是否满足约束条件？
    """)

if __name__ == "__main__":
    main()
