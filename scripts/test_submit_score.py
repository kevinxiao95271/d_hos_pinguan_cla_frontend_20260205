#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试提交评分 - 检查需要哪些参数
"""

import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031/api"

def login():
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000021",
        "name": "李明华",
        "title": "主任医师",
        "role": "REVIEWER"
    }, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('data', {}).get('token')
    return None

def get_first_task(token):
    """获取第一个任务"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/reviews/my-tasks", headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data'):
            return result['data'][0] if len(result['data']) > 0 else None
    return None

def test_submit_score(token, task):
    """测试提交评分"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试不同的参数组合
    test_cases = [
        {
            "name": "完整参数（使用 reviewTaskId）",
            "data": {
                "reviewTaskId": task['id'],
                "registrationId": task['registrationId'],
                "planScore": 18,
                "problemAnalysisScore": 17,
                "implementationScore": 16,
                "resultScore": 15,
                "reviewScore": 14,
                "operationScore": 13,
                "presentationScore": 12,
                "highlights": "测试亮点",
                "shortcomings": "测试不足"
            }
        },
        {
            "name": "完整参数（使用 taskId）",
            "data": {
                "taskId": task['id'],
                "registrationId": task['registrationId'],
                "planScore": 18,
                "problemAnalysisScore": 17,
                "implementationScore": 16,
                "resultScore": 15,
                "reviewScore": 14,
                "operationScore": 13,
                "presentationScore": 12,
                "highlights": "测试亮点",
                "shortcomings": "测试不足"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"测试: {test_case['name']}")
        print(f"{'='*60}")
        print(f"请求参数:")
        print(json.dumps(test_case['data'], ensure_ascii=False, indent=2))
        
        try:
            response = requests.post(
                f"{BASE_URL}/reviews/scores",
                headers=headers,
                json=test_case['data'],
                timeout=30
            )
            
            print(f"\n状态码: {response.status_code}")
            print(f"响应:")
            print(json.dumps(response.json(), ensure_ascii=False, indent=2))
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"\n✅ 成功!")
                    return test_case['name'], test_case['data']
                else:
                    print(f"\n❌ 失败: {result.get('message')}")
            else:
                print(f"\n❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"\n❌ 异常: {e}")
    
    return None, None

def main():
    print("\n" + "="*60)
    print("  测试提交评分参数")
    print("="*60)
    
    # 1. 登录
    print("\n1️⃣  登录...")
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    print("✅ 登录成功")
    
    # 2. 获取任务
    print("\n2️⃣  获取第一个任务...")
    task = get_first_task(token)
    if not task:
        print("❌ 没有任务")
        return
    
    print("✅ 获取任务成功")
    print(f"   任务ID: {task['id']}")
    print(f"   项目ID: {task['registrationId']}")
    print(f"   项目名: {task['projectName']}")
    
    # 3. 测试提交评分
    print("\n3️⃣  测试提交评分...")
    success_case, success_data = test_submit_score(token, task)
    
    # 4. 总结
    print("\n\n" + "="*60)
    print("  📊 测试总结")
    print("="*60)
    
    if success_case:
        print(f"\n✅ 找到可用的参数格式: {success_case}")
        print("\n前端应该使用以下参数:")
        print(json.dumps(success_data, ensure_ascii=False, indent=2))
    else:
        print("\n❌ 所有测试都失败了")
        print("\n建议:")
        print("1. 检查后端API文档")
        print("2. 查看后端日志")
        print("3. 确认所需的字段名称")

if __name__ == "__main__":
    main()
