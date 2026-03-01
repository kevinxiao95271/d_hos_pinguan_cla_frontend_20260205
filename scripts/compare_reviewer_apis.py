#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比书审评委分配和系统管理评委列表的API调用
检查为什么返回的数据不一致
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

def test_book_reviewer_api(token):
    """测试书审评委分配页面的API调用"""
    url = f"{BASE_URL}/admin/reviewers"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 书审评委分配页面的调用参数
    params = {
        "competitionId": 1,
        "page": 0,
        "size": 50
    }
    
    print("="*60)
    print("1. 书审评委分配页面 API")
    print("="*60)
    print(f"URL: {url}")
    print(f"参数: {json.dumps(params, ensure_ascii=False)}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
                
                # 判断数据格式
                if isinstance(data, dict) and 'content' in data:
                    reviewers = data.get('content', [])
                    total = data.get('totalElements', 0)
                    print(f"✅ 分页格式")
                    print(f"总数: {total}")
                    print(f"当前页: {len(reviewers)} 位")
                elif isinstance(data, list):
                    reviewers = data
                    total = len(reviewers)
                    print(f"✅ 数组格式")
                    print(f"返回: {total} 位")
                else:
                    reviewers = []
                    total = 0
                    print(f"⚠️ 未知格式")
                
                if len(reviewers) > 0:
                    print(f"\n第一位评委:")
                    print(json.dumps(reviewers[0], indent=2, ensure_ascii=False))
                
                return reviewers, total
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return [], 0

def test_ops_reviewer_api(token):
    """测试系统管理评委列表的API调用"""
    url = f"{BASE_URL}/admin/reviewers"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 系统管理页面的调用参数（不带筛选）
    params = {}
    
    print("\n" + "="*60)
    print("2. 系统管理评委列表 API (无筛选)")
    print("="*60)
    print(f"URL: {url}")
    print(f"参数: {json.dumps(params, ensure_ascii=False) if params else '无'}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
                
                # 判断数据格式
                if isinstance(data, dict) and 'content' in data:
                    reviewers = data.get('content', [])
                    total = data.get('totalElements', 0)
                    print(f"✅ 分页格式")
                    print(f"总数: {total}")
                    print(f"当前页: {len(reviewers)} 位")
                elif isinstance(data, list):
                    reviewers = data
                    total = len(reviewers)
                    print(f"✅ 数组格式")
                    print(f"返回: {total} 位")
                else:
                    reviewers = []
                    total = 0
                    print(f"⚠️ 未知格式")
                
                if len(reviewers) > 0:
                    print(f"\n第一位评委:")
                    print(json.dumps(reviewers[0], indent=2, ensure_ascii=False))
                
                return reviewers, total
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return [], 0

def test_ops_with_filters(token):
    """测试系统管理评委列表的API调用（带筛选）"""
    url = f"{BASE_URL}/admin/reviewers"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 系统管理页面的调用参数（带筛选）
    params = {
        "institutionId": 36232,  # 示例机构ID
    }
    
    print("\n" + "="*60)
    print("3. 系统管理评委列表 API (带机构筛选)")
    print("="*60)
    print(f"URL: {url}")
    print(f"参数: {json.dumps(params, ensure_ascii=False)}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
                
                # 判断数据格式
                if isinstance(data, dict) and 'content' in data:
                    reviewers = data.get('content', [])
                    total = data.get('totalElements', 0)
                    print(f"✅ 分页格式")
                    print(f"总数: {total}")
                    print(f"当前页: {len(reviewers)} 位")
                elif isinstance(data, list):
                    reviewers = data
                    total = len(reviewers)
                    print(f"✅ 数组格式")
                    print(f"返回: {total} 位")
                else:
                    reviewers = []
                    total = 0
                    print(f"⚠️ 未知格式")
                
                return reviewers, total
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return [], 0

def compare_results(book_reviewers, book_total, ops_reviewers, ops_total):
    """对比两个API的返回结果"""
    print("\n" + "="*60)
    print("4. 结果对比")
    print("="*60)
    
    print(f"\n书审评委分配页面:")
    print(f"  - 返回数量: {len(book_reviewers)}")
    print(f"  - 总数: {book_total}")
    
    print(f"\n系统管理评委列表:")
    print(f"  - 返回数量: {len(ops_reviewers)}")
    print(f"  - 总数: {ops_total}")
    
    # 提取评委ID
    book_ids = set(r.get('id') for r in book_reviewers if r.get('id'))
    ops_ids = set(r.get('id') for r in ops_reviewers if r.get('id'))
    
    print(f"\n评委ID对比:")
    print(f"  - 书审页面评委ID数: {len(book_ids)}")
    print(f"  - 系统管理评委ID数: {len(ops_ids)}")
    
    # 找出差异
    only_in_book = book_ids - ops_ids
    only_in_ops = ops_ids - book_ids
    common = book_ids & ops_ids
    
    print(f"  - 共同的评委: {len(common)}")
    print(f"  - 仅在书审页面: {len(only_in_book)}")
    print(f"  - 仅在系统管理: {len(only_in_ops)}")
    
    if only_in_book:
        print(f"\n仅在书审页面的评委ID: {sorted(only_in_book)[:10]}")
        if len(only_in_book) > 10:
            print(f"  ... 还有 {len(only_in_book) - 10} 个")
    
    if only_in_ops:
        print(f"\n仅在系统管理的评委ID: {sorted(only_in_ops)[:10]}")
        if len(only_in_ops) > 10:
            print(f"  ... 还有 {len(only_in_ops) - 10} 个")
    
    # 提取评委姓名
    book_names = set(r.get('name') for r in book_reviewers if r.get('name'))
    ops_names = set(r.get('name') for r in ops_reviewers if r.get('name'))
    
    print(f"\n评委姓名对比:")
    print(f"  - 书审页面有姓名的评委: {len(book_names)}")
    print(f"  - 系统管理有姓名的评委: {len(ops_names)}")
    
    only_names_in_book = book_names - ops_names
    only_names_in_ops = ops_names - book_names
    
    if only_names_in_book:
        print(f"\n仅在书审页面的评委姓名:")
        for name in sorted(only_names_in_book)[:20]:
            print(f"  - {name}")
        if len(only_names_in_book) > 20:
            print(f"  ... 还有 {len(only_names_in_book) - 20} 位")
    
    if only_names_in_ops:
        print(f"\n仅在系统管理的评委姓名:")
        for name in sorted(only_names_in_ops)[:20]:
            print(f"  - {name}")
        if len(only_names_in_ops) > 20:
            print(f"  ... 还有 {len(only_names_in_ops) - 20} 位")
    
    # 结论
    print(f"\n结论:")
    if book_total == ops_total and len(book_ids) == len(ops_ids) and book_ids == ops_ids:
        print("  ✅ 两个API返回的数据完全一致")
    else:
        print("  ❌ 两个API返回的数据不一致")
        if book_total != ops_total:
            print(f"     - 总数不同: {book_total} vs {ops_total}")
        if len(book_ids) != len(ops_ids):
            print(f"     - 返回数量不同: {len(book_ids)} vs {len(ops_ids)}")
        if book_ids != ops_ids:
            print(f"     - 评委ID集合不同")

def main():
    print("="*60)
    print("对比书审评委分配和系统管理评委列表的API")
    print("="*60)
    print()
    
    token = login()
    if not token:
        print("❌ 无法获取token，测试终止")
        return
    
    # 测试两个页面的API调用
    book_reviewers, book_total = test_book_reviewer_api(token)
    ops_reviewers, ops_total = test_ops_reviewer_api(token)
    
    # 测试带筛选的调用
    test_ops_with_filters(token)
    
    # 对比结果
    compare_results(book_reviewers, book_total, ops_reviewers, ops_total)
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()
