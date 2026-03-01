#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试评分数据
1. 用评委账号登录
2. 查看是否有待评审任务
3. 如果有，提交一个测试评分
4. 然后用组委会账号查看 summary API 返回的数据结构
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"
TIMEOUT = 10

def login_reviewer():
    """登录评委账号"""
    url = f"{BASE_URL}/auth/login-with-password"
    # 尝试几个评委账号
    reviewers = [
        {"phone": "13800000021", "password": "reviewer2026", "name": "评委1"},
        {"phone": "13800000022", "password": "reviewer2026", "name": "评委2"},
        {"phone": "13800000023", "password": "reviewer2026", "name": "评委3"},
    ]
    
    print("="*60)
    print("尝试登录评委账号")
    print("="*60)
    
    for reviewer in reviewers:
        print(f"\n尝试登录: {reviewer['name']} ({reviewer['phone']})")
        try:
            response = requests.post(url, json={
                "phone": reviewer['phone'],
                "password": reviewer['password']
            }, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    token = result['data']['token']
                    print(f"✅ 登录成功")
                    return token, reviewer['name']
                else:
                    print(f"❌ 登录失败: {result.get('message')}")
            else:
                print(f"❌ 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    return None, None

def check_reviewer_tasks(token):
    """检查评委的待评审任务"""
    url = f"{BASE_URL}/reviews/my-tasks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"stage": "BOOK"}
    
    print("\n" + "="*60)
    print("检查评委的待评审任务")
    print("="*60)
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                tasks = result.get('data', [])
                print(f"✅ 找到 {len(tasks)} 个任务")
                
                if len(tasks) > 0:
                    print(f"\n任务列表:")
                    for i, task in enumerate(tasks, 1):
                        print(f"\n任务 {i}:")
                        print(f"  - taskId: {task.get('taskId')}")
                        print(f"  - registrationId: {task.get('registrationId')}")
                        print(f"  - projectName: {task.get('projectName')}")
                        print(f"  - status: {task.get('status')}")
                        print(f"  - stage: {task.get('stage')}")
                    
                    return tasks
                else:
                    print("⚠️ 没有待评审任务")
            else:
                print(f"❌ 失败: {result.get('message')}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return []

def submit_test_score(token, task):
    """提交一个测试评分"""
    url = f"{BASE_URL}/reviews/scores"
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "reviewTaskId": task.get('taskId'),
        "registrationId": task.get('registrationId'),
        "stage": "BOOK",
        "plan": 15.0,
        "problem": 14.5,
        "action": 16.0,
        "success": 15.5,
        "review": 14.0,
        "operation": 13.5,
        "presentation": 12.0
    }
    
    print("\n" + "="*60)
    print("提交测试评分")
    print("="*60)
    print(f"任务: {task.get('projectName')}")
    print(f"评分数据: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 评分提交成功")
                return True
            else:
                print(f"❌ 提交失败: {result.get('message')}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return False

def login_committee():
    """登录组委会账号"""
    url = f"{BASE_URL}/auth/login-with-password"
    data = {"phone": "13800000127", "password": "committee2026"}
    
    print("\n" + "="*60)
    print("登录组委会账号")
    print("="*60)
    
    try:
        response = requests.post(url, json=data, timeout=TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 登录成功")
                return result['data']['token']
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return None

def check_summary_api(token):
    """检查 summary API 返回的数据结构"""
    url = f"{BASE_URL}/admin/reviews/summary"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"competitionId": 1, "stage": "BOOK"}
    
    print("\n" + "="*60)
    print("检查 /admin/reviews/summary 数据结构")
    print("="*60)
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
                print(f"✅ 返回 {len(data)} 条记录")
                
                if len(data) > 0:
                    print(f"\n第一条记录:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
                    
                    # 检查字段
                    print(f"\n字段检查:")
                    required_fields = [
                        'scoreId', 'projectName', 'institutionName', 'institutionLevel',
                        'groupType', 'groupCode', 'reviewerName', 'reviewerInstitutionName',
                        'plan', 'problem', 'action', 'success', 'review', 'operation', 
                        'presentation', 'total', 'submittedAt'
                    ]
                    
                    first_record = data[0]
                    missing_fields = []
                    extra_fields = []
                    
                    for field in required_fields:
                        if field in first_record:
                            print(f"  ✅ {field}: {first_record[field]}")
                        else:
                            print(f"  ❌ {field} (缺失)")
                            missing_fields.append(field)
                    
                    # 检查额外字段
                    for field in first_record.keys():
                        if field not in required_fields:
                            extra_fields.append(field)
                    
                    if extra_fields:
                        print(f"\n额外字段:")
                        for field in extra_fields:
                            print(f"  ℹ️ {field}: {first_record[field]}")
                    
                    if missing_fields:
                        print(f"\n⚠️ 缺失字段: {', '.join(missing_fields)}")
                        print(f"\n结论: ❌ 数据结构不完全匹配，需要后端调整或前端适配")
                    else:
                        print(f"\n结论: ✅ 数据结构完全匹配，可以直接使用！")
                else:
                    print("⚠️ 仍然返回空数组")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 异常: {e}")

def main():
    print("="*60)
    print("创建测试评分数据并验证API")
    print("="*60)
    
    # 1. 登录评委账号
    reviewer_token, reviewer_name = login_reviewer()
    if not reviewer_token:
        print("\n❌ 无法登录评委账号")
        print("说明: 可能没有配置评委账号，或密码不正确")
        print("\n跳过评分提交，直接检查现有数据...")
        
        # 直接用组委会账号检查
        committee_token = login_committee()
        if committee_token:
            check_summary_api(committee_token)
        return
    
    # 2. 检查待评审任务
    tasks = check_reviewer_tasks(reviewer_token)
    if not tasks:
        print("\n⚠️ 评委没有待评审任务")
        print("说明: 可能还没有分配评审任务")
        print("\n无法创建测试数据，直接检查现有数据...")
        
        # 直接用组委会账号检查
        committee_token = login_committee()
        if committee_token:
            check_summary_api(committee_token)
        return
    
    # 3. 提交一个测试评分
    first_task = tasks[0]
    if first_task.get('status') == 'PENDING':
        success = submit_test_score(reviewer_token, first_task)
        if not success:
            print("\n❌ 评分提交失败")
            return
    else:
        print(f"\n⚠️ 第一个任务状态不是PENDING: {first_task.get('status')}")
        print("尝试查找PENDING状态的任务...")
        
        pending_task = None
        for task in tasks:
            if task.get('status') == 'PENDING':
                pending_task = task
                break
        
        if pending_task:
            success = submit_test_score(reviewer_token, pending_task)
            if not success:
                print("\n❌ 评分提交失败")
                return
        else:
            print("\n⚠️ 没有找到PENDING状态的任务")
    
    # 4. 用组委会账号检查数据结构
    committee_token = login_committee()
    if committee_token:
        check_summary_api(committee_token)
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()
