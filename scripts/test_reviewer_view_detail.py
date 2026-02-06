#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试评审专家查看项目详情的完整流程
"""

import sys
import io
import requests
import json

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031/api"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def main():
    print("\n" + "=" * 60)
    print("  评审专家查看项目详情 - 完整流程测试")
    print("=" * 60)
    
    # 步骤1: 评委登录
    print_section("1. 评委登录")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "phone": "13800000021",
            "name": "Reviewer A",
            "role": "REVIEWER"
        }, timeout=30)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            token = result.get('data', {}).get('token')
            print(f"✅ 登录成功")
            print(f"Token: {token[:50]}...")
        else:
            print(f"❌ 登录失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 步骤2: 获取任务列表
    print_section("2. 获取任务列表")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/reviews/my-tasks", 
                              headers=headers, 
                              timeout=30)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            tasks = result.get('data', [])
            print(f"✅ 获取任务成功，共 {len(tasks)} 个任务")
            
            if len(tasks) > 0:
                task = tasks[0]
                print(f"\n任务详情:")
                print(f"  taskId: {task.get('id')}")
                print(f"  registrationId: {task.get('registrationId')}")
                print(f"  projectName: {task.get('projectName')}")
                print(f"  institutionName: {task.get('institutionName')}")
                print(f"  stage: {task.get('stage')}")
                print(f"  status: {task.get('status')}")
                
                task_id = task.get('id')
                registration_id = task.get('registrationId')
                
                if not registration_id:
                    print("\n❌ 警告: registrationId 为空!")
                    print("这将导致无法获取项目详情")
                    return
            else:
                print("⚠️ 暂无任务，无法继续测试")
                return
        else:
            print(f"❌ 获取任务失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取任务异常: {e}")
        return
    
    # 步骤3: 获取项目详情
    print_section("3. 获取项目详情")
    print(f"registrationId: {registration_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/registrations/{registration_id}", 
                              headers=headers, 
                              timeout=30)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                print(f"✅ 获取项目详情成功")
                
                print(f"\n项目基本信息:")
                print(f"  id: {data.get('id')}")
                print(f"  projectName: {data.get('projectName')}")
                print(f"  institutionName: {data.get('institutionName')}")
                print(f"  groupType: {data.get('groupType')}")
                print(f"  status: {data.get('status')}")
                
                # 成员信息
                members = data.get('members', [])
                print(f"\n成员信息: 共 {len(members)} 人")
                for i, member in enumerate(members[:3], 1):
                    print(f"  {i}. {member.get('name')} - {member.get('title')} - {member.get('role')}")
                
                # 活动说明
                activity = data.get('activityInfo', {})
                if activity:
                    print(f"\n活动说明:")
                    print(f"  theme: {activity.get('theme')}")
                    print(f"  subjectTypeLabel: {activity.get('subjectTypeLabel')}")
                    print(f"  methodLabel: {activity.get('methodLabel')}")
                
                # 项目总结
                summary = data.get('summary', {})
                if summary:
                    print(f"\n项目总结:")
                    print(f"  plan: {summary.get('plan', '')[:50]}...")
                    print(f"  problemAnalysis: {summary.get('problemAnalysis', '')[:50]}...")
                
                print("\n✅ 项目详情数据完整，可以正常显示")
                
            else:
                print(f"❌ 获取失败: {result.get('message')}")
                return
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
            print(f"响应: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取项目详情异常: {e}")
        return
    
    # 步骤4: 尝试获取已有评分
    print_section("4. 检查是否已有评分")
    print(f"taskId: {task_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/reviews/scores/{task_id}", 
                              headers=headers, 
                              timeout=30)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                print(f"✅ 已有评分")
                print(f"  totalScore: {data.get('totalScore')}")
                print(f"  highlights: {data.get('highlights', '')[:50]}...")
            else:
                print(f"ℹ️ 尚未评分: {result.get('message')}")
        else:
            print(f"ℹ️ 尚未评分（{response.status_code}）")
    except Exception as e:
        print(f"ℹ️ 尚未评分或异常: {e}")
    
    # 总结
    print_section("测试总结")
    print("✅ 评审专家查看项目详情流程测试完成")
    print("\n前端需要确认:")
    print("1. 从任务列表跳转时，确保传递 registrationId")
    print("2. 使用 registrationId 调用 GET /api/registrations/{id}")
    print("3. 正确显示项目的所有信息（基本信息、成员、活动说明、总结）")
    print("\n如果前端显示为空，检查:")
    print("- console 中是否有 registrationId")
    print("- 是否正确调用了 getRegistrationDetail API")
    print("- 数据绑定是否正确")

if __name__ == "__main__":
    main()
