#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试评审专家前端问题 - 模拟前端完整流程
"""

import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031/api"

def login(phone, name):
    """登录"""
    print(f"\n{'='*60}")
    print(f"1️⃣  登录: {name} ({phone})")
    print(f"{'='*60}")
    
    login_data = {
        "phone": phone,
        "name": name,
        "title": "评委",
        "role": "REVIEWER",
        "reviewerGroupCode": "A1",
        "interviewGroupCode": "A1",
        "expertBackground": "MEDICAL"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('data', {}).get('token')
                print(f"✅ 登录成功")
                print(f"Token: {token[:50]}...")
                return token
        print(f"❌ 登录失败: {response.text}")
        return None
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def get_tasks(token):
    """获取任务列表"""
    print(f"\n{'='*60}")
    print(f"2️⃣  获取任务列表")
    print(f"{'='*60}")
    print(f"请求: GET /api/reviews/my-tasks")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/reviews/my-tasks", headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n响应数据:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            if result.get('success'):
                tasks = result.get('data', [])
                print(f"\n✅ 成功获取 {len(tasks)} 个任务\n")
                
                if len(tasks) > 0:
                    print("="*60)
                    print("任务列表数据结构分析:")
                    print("="*60)
                    
                    for i, task in enumerate(tasks[:3], 1):
                        print(f"\n任务 {i}:")
                        print(f"  id: {task.get('id')}")
                        print(f"  projectName: {task.get('projectName')} {'✅' if task.get('projectName') else '❌ 缺失!'}")
                        print(f"  institutionName: {task.get('institutionName')} {'✅' if task.get('institutionName') else '❌ 缺失!'}")
                        print(f"  registrationId: {task.get('registrationId')} {'✅' if task.get('registrationId') else '❌ 缺失!'}")
                        print(f"  stage: {task.get('stage')}")
                        print(f"  status: {task.get('status')}")
                        print(f"  assignedAt: {task.get('assignedAt')}")
                    
                    if len(tasks) > 3:
                        print(f"\n  ... 还有 {len(tasks) - 3} 个任务")
                    
                    return tasks
                else:
                    print("⚠️  任务列表为空")
                    return []
            else:
                print(f"❌ 响应失败: {result.get('message')}")
                return None
        else:
            print(f"❌ 请求失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def get_project_detail(token, registration_id):
    """获取项目详情"""
    print(f"\n{'='*60}")
    print(f"3️⃣  获取项目详情 (registrationId={registration_id})")
    print(f"{'='*60}")
    print(f"请求: GET /api/registrations/{registration_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/registrations/{registration_id}", headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n响应数据:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            if result.get('success'):
                data = result.get('data', {})
                print(f"\n✅ 成功获取项目详情\n")
                
                print("="*60)
                print("项目详情数据结构分析:")
                print("="*60)
                print(f"  projectName: {data.get('projectName')} {'✅' if data.get('projectName') else '❌ 缺失!'}")
                print(f"  institutionName: {data.get('institutionName')} {'✅' if data.get('institutionName') else '❌ 缺失!'}")
                print(f"  groupType: {data.get('groupType')} {'✅' if data.get('groupType') else '❌ 缺失!'}")
                print(f"  status: {data.get('status')}")
                
                members = data.get('members', [])
                print(f"\n  members: {len(members)} 人 {'✅' if len(members) > 0 else '⚠️ 无成员'}")
                if len(members) > 0:
                    for member in members[:2]:
                        print(f"    - {member.get('name')} ({member.get('title')}) - {member.get('role')}")
                    if len(members) > 2:
                        print(f"    ... 还有 {len(members) - 2} 人")
                
                activity = data.get('activityInfo')
                print(f"\n  activityInfo: {'✅ 有' if activity else '❌ 无'}")
                if activity:
                    print(f"    theme: {activity.get('theme')}")
                    print(f"    subjectTypeLabel: {activity.get('subjectTypeLabel')}")
                    print(f"    methodLabel: {activity.get('methodLabel')}")
                
                summary = data.get('summary')
                print(f"\n  summary: {'✅ 有' if summary else '❌ 无'}")
                if summary:
                    print(f"    plan: {summary.get('plan', '')[:50]}...")
                
                return data
            else:
                print(f"❌ 响应失败: {result.get('message')}")
                return None
        else:
            print(f"❌ 请求失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("  🔍 调试评审专家前端问题")
    print("="*60)
    
    # 使用李明华账号测试
    phone = "13800000021"
    name = "李明华"
    
    # 1. 登录
    token = login(phone, name)
    if not token:
        print("\n❌ 登录失败，测试终止")
        return
    
    # 2. 获取任务列表
    tasks = get_tasks(token)
    if tasks is None:
        print("\n❌ 获取任务列表失败，测试终止")
        return
    
    if len(tasks) == 0:
        print("\n⚠️  任务列表为空，无法继续测试")
        print("\n建议:")
        print("1. 在管理端为该评审专家分配任务")
        print("2. 确保任务包含 projectName 和 institutionName")
        return
    
    # 3. 获取第一个任务的项目详情
    first_task = tasks[0]
    registration_id = first_task.get('registrationId')
    
    if not registration_id:
        print(f"\n❌ 第一个任务缺少 registrationId")
        print("任务数据:", json.dumps(first_task, ensure_ascii=False, indent=2))
        return
    
    detail = get_project_detail(token, registration_id)
    
    # 4. 总结
    print("\n\n" + "="*60)
    print("  📊 诊断结果")
    print("="*60)
    
    if tasks and len(tasks) > 0 and detail:
        print("\n✅ 后端API完全正常\n")
        
        # 检查前端可能的问题
        print("="*60)
        print("  ⚠️  前端问题排查")
        print("="*60)
        
        issues = []
        
        # 检查任务列表数据
        if not first_task.get('projectName'):
            issues.append("❌ 任务列表中 projectName 字段缺失")
        if not first_task.get('institutionName'):
            issues.append("❌ 任务列表中 institutionName 字段缺失")
        
        # 检查详情数据
        if not detail.get('projectName'):
            issues.append("❌ 项目详情中 projectName 字段缺失")
        if not detail.get('institutionName'):
            issues.append("❌ 项目详情中 institutionName 字段缺失")
        if not detail.get('members') or len(detail.get('members', [])) == 0:
            issues.append("⚠️  项目详情中 members 为空")
        
        if issues:
            print("\n发现以下问题:")
            for issue in issues:
                print(f"  {issue}")
            print("\n建议:")
            print("1. 检查后端返回的数据结构")
            print("2. 确保后端API返回完整的字段")
            print("3. 检查前端是否正确解析数据")
        else:
            print("\n✅ 数据完整，前端可能的问题:")
            print("\n1. 前端未正确绑定数据到模板")
            print("   检查: Tasks.vue 的 <el-table-column prop='projectName' />")
            print("   检查: Review.vue 的 {{ taskInfo.projectName }}")
            print("\n2. 前端未正确调用API")
            print("   检查: Tasks.vue 的 getMyReviewTasks() 调用")
            print("   检查: Review.vue 的 getRegistrationDetail() 调用")
            print("\n3. 数据响应格式不匹配")
            print("   检查: res.data 是否正确提取")
            print("   检查: 是否需要 res.data.data")
            
            print("\n" + "="*60)
            print("  🔧 前端调试建议")
            print("="*60)
            print("\n在浏览器控制台输入以下命令调试:\n")
            print("// 1. 检查API调用")
            print("fetch('http://localhost:6031/api/reviews/my-tasks', {")
            print("  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }")
            print("}).then(r => r.json()).then(d => console.log('任务列表:', d))")
            print("\n// 2. 检查数据是否有 projectName")
            print("console.log('检查tasks数组:', tasks)")
            print("console.log('第一个任务:', tasks[0])")
            print("console.log('projectName:', tasks[0]?.projectName)")
    else:
        print("\n❌ 存在问题:")
        if not tasks or len(tasks) == 0:
            print("  - 任务列表为空")
        if not detail:
            print("  - 无法获取项目详情")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
