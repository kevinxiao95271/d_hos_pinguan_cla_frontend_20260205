#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评委评审流程端到端测试
测试评委登录 → 查看任务 → 评审打分 → 提交结果
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

def test_reviewer_login():
    """测试评委登录"""
    print_section("1. 评委登录")
    
    url = f"{BASE_URL}/auth/login"
    payload = {
        "phone": "13800000021",
        "name": "Reviewer A",
        "title": "Expert",
        "role": "REVIEWER",
        "institutionId": 2
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"请求 URL: {url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('data', {}).get('token')
                print_result(True, "评委登录成功", {"token": token[:50] + "..." if token else None})
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

def test_get_review_tasks(token):
    """获取评审任务列表"""
    print_section("2. 获取评审任务列表 (我的任务)")
    
    url = f"{BASE_URL}/reviews/my-tasks"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"请求 URL: {url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                tasks = result.get('data', [])
                print_result(True, f"获取任务成功，共 {len(tasks)} 个任务")
                
                if len(tasks) > 0:
                    task = tasks[0]
                    print(f"\n   任务样例:")
                    print(f"   - taskId: {task.get('id')}")
                    print(f"   - registrationId: {task.get('registrationId')}")
                    print(f"   - projectName: {task.get('projectName')}")
                    print(f"   - stage: {task.get('stage')}")
                    print(f"   - status: {task.get('status')}")
                    return tasks
                else:
                    print("   ⚠️ 暂无评审任务")
                    return []
            else:
                print_result(False, f"获取失败: {result.get('message')}")
                return []
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return []
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return []

def test_get_registration_detail(token, registration_id):
    """获取报名详情"""
    print_section(f"3. 获取报名详情 (registrationId={registration_id})")
    
    url = f"{BASE_URL}/registrations/{registration_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"请求 URL: {url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                print_result(True, "获取报名详情成功")
                print(f"\n   项目信息:")
                print(f"   - projectName: {data.get('projectName')}")
                print(f"   - institutionName: {data.get('institutionName')}")
                print(f"   - groupType: {data.get('groupType')}")
                return data
            else:
                print_result(False, f"获取失败: {result.get('message')}")
                return None
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return None
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return None

def test_submit_review(token, task_id, registration_id):
    """提交评审结果"""
    print_section(f"4. 提交评审结果 (taskId={task_id})")
    
    url = f"{BASE_URL}/reviews/scores"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 书审评分数据
    payload = {
        "taskId": task_id,
        "registrationId": registration_id,
        "planScore": 15,
        "problemAnalysisScore": 20,
        "implementationScore": 25,
        "resultScore": 20,
        "reviewScore": 10,
        "operationScore": 5,
        "presentationScore": 5,
        "highlights": "项目规划清晰，实施方案完善，数据分析详实。",
        "shortcomings": "部分改进措施可以进一步量化，建议增加更多的对比数据。"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"请求 URL: {url}")
        print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_result(True, "评审提交成功")
                total_score = sum([
                    payload['planScore'],
                    payload['problemAnalysisScore'],
                    payload['implementationScore'],
                    payload['resultScore'],
                    payload['reviewScore'],
                    payload['operationScore'],
                    payload['presentationScore']
                ])
                print(f"   总分: {total_score}")
                return True
            else:
                print_result(False, f"提交失败: {result.get('message')}")
                return False
        else:
            print_result(False, f"HTTP 错误: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return False

def test_get_review_score(token, task_id):
    """查看评审评分"""
    print_section(f"5. 查看已提交的评分 (taskId={task_id})")
    
    url = f"{BASE_URL}/reviews/scores/{task_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"请求 URL: {url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                print_result(True, "获取评分成功")
                
                print(f"\n   评分详情:")
                print(f"   - 计划: {data.get('planScore')}")
                print(f"   - 问题分析: {data.get('problemAnalysisScore')}")
                print(f"   - 实施: {data.get('implementationScore')}")
                print(f"   - 结果: {data.get('resultScore')}")
                print(f"   - 总分: {data.get('totalScore')}")
                
                return True
            else:
                print_result(False, f"获取失败: {result.get('message')}")
                return False
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  评委评审流程端到端测试")
    print("="*60)
    
    # 1. 评委登录
    token = test_reviewer_login()
    if not token:
        print("\n❌ 登录失败，测试终止")
        return
    
    # 2. 获取评审任务
    tasks = test_get_review_tasks(token)
    if not tasks:
        print("\n⚠️ 没有评审任务，无法继续测试")
        print("提示：请先在管理端分配评审任务")
        return
    
    # 使用第一个PENDING状态的任务
    pending_task = None
    for task in tasks:
        if task.get('status') == 'PENDING':
            pending_task = task
            break
    
    if not pending_task:
        print("\n⚠️ 没有待评审的任务（PENDING状态）")
        print(f"当前任务状态: {[t.get('status') for t in tasks]}")
        
        # 如果有已完成的任务，可以查看评分
        if tasks:
            completed_task = tasks[0]
            test_get_review_score(token, completed_task.get('id'))
        return
    
    task_id = pending_task.get('id')
    registration_id = pending_task.get('registrationId')
    
    # 3. 获取报名详情
    detail = test_get_registration_detail(token, registration_id)
    if not detail:
        print("\n❌ 获取报名详情失败")
        return
    
    # 4. 提交评审结果
    success = test_submit_review(token, task_id, registration_id)
    if not success:
        print("\n❌ 提交评审失败")
        return
    
    # 5. 查看已提交的评分
    test_get_review_score(token, task_id)
    
    print_section("测试总结")
    print("""
✅ 评委评审完整流程测试完成

流程说明：
1. 评委登录 → 获取 token
2. 查看分配的评审任务列表
3. 选择待评审任务，查看项目详情
4. 填写评分和意见，提交评审
5. 查看已提交的评审结果

前端页面对应：
- 评委登录：/login
- 任务列表：/reviewer/tasks
- 项目详情：点击"详情"按钮
- 评审打分：点击"评分"按钮
    """)

if __name__ == "__main__":
    main()
