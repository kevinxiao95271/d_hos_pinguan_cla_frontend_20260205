#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探测 /admin/reviews/summary API
查看返回的数据结构是否符合前端需求
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

def test_summary_api(token):
    """测试 summary API 的各种参数组合"""
    url = f"{BASE_URL}/admin/reviews/summary"
    headers = {"Authorization": f"Bearer {token}"}
    
    test_cases = [
        {
            "name": "只带 competitionId 和 stage",
            "params": {"competitionId": 1, "stage": "BOOK"}
        },
        {
            "name": "带 groupType 筛选",
            "params": {"competitionId": 1, "stage": "BOOK", "groupType": "ADVANCED"}
        },
        {
            "name": "带 reviewerName 筛选",
            "params": {"competitionId": 1, "stage": "BOOK", "reviewerName": "李"}
        },
        {
            "name": "带 institutionName 筛选",
            "params": {"competitionId": 1, "stage": "BOOK", "institutionName": "医院"}
        },
        {
            "name": "所有筛选条件",
            "params": {
                "competitionId": 1, 
                "stage": "BOOK",
                "groupType": "ADVANCED",
                "reviewerName": "李",
                "institutionName": "医院"
            }
        }
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
                    print(f"✅ 成功 - 返回 {len(data)} 条记录")
                    
                    if len(data) > 0:
                        print(f"\n第一条记录的字段:")
                        first_record = data[0]
                        for key, value in first_record.items():
                            value_str = str(value)
                            if len(value_str) > 50:
                                value_str = value_str[:50] + "..."
                            print(f"  - {key}: {value_str}")
                        
                        print(f"\n完整的第一条记录:")
                        print(json.dumps(first_record, indent=2, ensure_ascii=False))
                        
                        # 检查前端需要的字段
                        print(f"\n字段检查:")
                        required_fields = [
                            'scoreId', 'projectName', 'institutionName', 'institutionLevel',
                            'groupType', 'groupCode', 'reviewerName', 'reviewerInstitutionName',
                            'plan', 'problem', 'action', 'success', 'review', 'operation', 
                            'presentation', 'total', 'submittedAt'
                        ]
                        
                        missing_fields = []
                        for field in required_fields:
                            if field in first_record:
                                print(f"  ✅ {field}")
                            else:
                                print(f"  ❌ {field} (缺失)")
                                missing_fields.append(field)
                        
                        if missing_fields:
                            print(f"\n⚠️ 缺失字段: {', '.join(missing_fields)}")
                        else:
                            print(f"\n✅ 所有必需字段都存在！")
                    else:
                        print("⚠️ 返回空数组，可能还没有评分数据")
                else:
                    print(f"❌ 失败: {result.get('message')}")
            elif response.status_code == 400:
                print(f"❌ 400 Bad Request")
                print(f"响应: {response.text}")
            elif response.status_code == 404:
                print(f"❌ 404 Not Found")
            else:
                print(f"⚠️ 状态码: {response.status_code}")
                print(f"响应: {response.text}")
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        print()

def check_if_has_review_data(token):
    """检查系统中是否有任何评审数据"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("="*60)
    print("检查系统中是否有评审数据")
    print("="*60)
    
    # 检查评审任务
    print("\n1. 检查评审任务 (BOOK阶段)")
    url = f"{BASE_URL}/admin/reviews/tasks"
    params = {"competitionId": 1, "stage": "BOOK"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                tasks = result.get('data', [])
                print(f"   评审任务数: {len(tasks)}")
                
                if len(tasks) > 0:
                    # 统计任务状态
                    status_count = {}
                    for task in tasks:
                        status = task.get('status', 'UNKNOWN')
                        status_count[status] = status_count.get(status, 0) + 1
                    
                    print(f"   任务状态分布:")
                    for status, count in status_count.items():
                        print(f"     - {status}: {count}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 检查所有阶段的评审汇总
    print("\n2. 检查各阶段评审汇总")
    stages = ["BOOK", "INTERVIEW", "FINAL"]
    
    for stage in stages:
        url = f"{BASE_URL}/admin/reviews/summary"
        params = {"competitionId": 1, "stage": stage}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    data = result.get('data', [])
                    print(f"   {stage}: {len(data)} 条评分记录")
        except Exception as e:
            print(f"   {stage}: 异常 - {e}")
    
    print()

def main():
    print("="*60)
    print("探测 /admin/reviews/summary API")
    print("="*60)
    print()
    
    token = login()
    if not token:
        print("❌ 无法获取token，测试终止")
        return
    
    # 先检查是否有数据
    check_if_has_review_data(token)
    
    # 测试API
    test_summary_api(token)
    
    print("="*60)
    print("探测完成")
    print("="*60)

if __name__ == "__main__":
    main()
