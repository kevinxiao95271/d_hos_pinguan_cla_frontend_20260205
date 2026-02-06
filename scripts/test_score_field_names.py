#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试不同的字段名组合
"""

import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031/api"

def login():
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000021",
        "name": "李明华",
        "title": "主任医师",
        "role": "REVIEWER"
    }, timeout=30)
    
    if response.status_code == 200:
        return response.json().get('data', {}).get('token')
    return None

def get_first_task(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/reviews/my-tasks", headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data'):
            return result['data'][0] if len(result['data']) > 0 else None
    return None

def test_field_combinations(token, task):
    """测试不同的字段名组合"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试各种可能的字段名
    test_cases = [
        # 测试1: 使用 plan 而不是 planScore
        {
            "name": "字段名无Score后缀",
            "data": {
                "reviewTaskId": task['id'],
                "plan": 18,
                "problemAnalysis": 17,
                "implementation": 16,
                "result": 15,
                "review": 14,
                "operation": 13,
                "presentation": 12,
                "highlights": "测试亮点",
                "shortcomings": "测试不足"
            }
        },
        # 测试2: 使用蛇形命名
        {
            "name": "蛇形命名",
            "data": {
                "review_task_id": task['id'],
                "plan_score": 18,
                "problem_analysis_score": 17,
                "implementation_score": 16,
                "result_score": 15,
                "review_score": 14,
                "operation_score": 13,
                "presentation_score": 12,
                "highlights": "测试亮点",
                "shortcomings": "测试不足"
            }
        },
        # 测试3: 不传 registrationId
        {
            "name": "不传registrationId（只用reviewTaskId）",
            "data": {
                "reviewTaskId": task['id'],
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
        # 测试4: 只传分数和评语
        {
            "name": "最小参数集（只传reviewTaskId和分数）",
            "data": {
                "reviewTaskId": task['id'],
                "scores": {
                    "plan": 18,
                    "problemAnalysis": 17,
                    "implementation": 16,
                    "result": 15,
                    "review": 14,
                    "operation": 13,
                    "presentation": 12
                },
                "highlights": "测试亮点",
                "shortcomings": "测试不足"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*70}")
        print(f"测试: {test_case['name']}")
        print(f"{'='*70}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/reviews/scores",
                headers=headers,
                json=test_case['data'],
                timeout=30
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 成功!")
                    print(f"\n正确的参数格式:")
                    print(json.dumps(test_case['data'], ensure_ascii=False, indent=2))
                    return test_case
                else:
                    print(f"❌ 失败: {result.get('message')}")
            elif response.status_code == 400:
                result = response.json()
                print(f"❌ 参数错误: {result.get('message')}")
                # 尝试从错误信息中提取有用信息
                if 'message' in result:
                    print(f"   错误详情: {result['message']}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    return None

def main():
    print("\n" + "="*70)
    print("  测试评分字段名组合")
    print("="*70)
    
    # 登录
    print("\n登录...")
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    print("✅ 登录成功")
    
    # 获取任务
    print("\n获取任务...")
    task = get_first_task(token)
    if not task:
        print("❌ 没有任务")
        return
    print(f"✅ 任务ID: {task['id']}, 项目ID: {task['registrationId']}")
    
    # 测试
    print("\n开始测试...")
    success = test_field_combinations(token, task)
    
    if not success:
        print("\n\n" + "="*70)
        print("  ⚠️  所有测试都失败")
        print("="*70)
        print("\n请提供后端API文档或Swagger定义来确认正确的字段名")
        print("或者查看后端代码中的 DTO/Request 类定义")

if __name__ == "__main__":
    main()
