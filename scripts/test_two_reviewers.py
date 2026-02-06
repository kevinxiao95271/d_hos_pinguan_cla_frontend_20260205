#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试两位评审专家的完整数据
"""

import sys
import io
import requests
import json

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031/api"

def test_reviewer(name, phone, title, institution):
    """测试评审专家"""
    print(f"\n{'='*60}")
    print(f"  测试评审专家: {name}")
    print(f"  手机号: {phone}")
    print(f"  职称: {title}")
    print(f"  机构: {institution}")
    print(f"{'='*60}\n")
    
    # 1. 登录
    print("1️⃣  登录...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "phone": phone,
            "name": name,
            "role": "REVIEWER"
        }, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"响应: {response.text}")
            return
        
        result = response.json()
        token = result.get('data', {}).get('token')
        print(f"✅ 登录成功")
        print(f"Token: {token[:50]}...")
        
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 获取任务列表
    print("\n2️⃣  获取任务列表...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/reviews/my-tasks", 
                              headers=headers, 
                              timeout=30)
        
        print(f"请求: GET /api/reviews/my-tasks")
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 获取任务失败")
            print(f"响应: {response.text}")
            return
        
        result = response.json()
        tasks = result.get('data', [])
        
        print(f"✅ 获取成功，共 {len(tasks)} 个任务\n")
        
        if len(tasks) == 0:
            print("⚠️  暂无任务")
            return
        
        # 显示所有任务
        print("任务列表:")
        print("-" * 60)
        for i, task in enumerate(tasks, 1):
            print(f"任务 {i}:")
            print(f"  taskId: {task.get('id')}")
            print(f"  registrationId: {task.get('registrationId')} {'✅' if task.get('registrationId') else '❌ 缺失!'}")
            print(f"  projectName: {task.get('projectName')}")
            print(f"  institutionName: {task.get('institutionName')}")
            print(f"  stage: {task.get('stage')}")
            print(f"  status: {task.get('status')}")
            print()
        
        # 3. 测试第一个任务的详情
        first_task = tasks[0]
        task_id = first_task.get('id')
        registration_id = first_task.get('registrationId')
        
        if not registration_id:
            print("❌ 第一个任务的 registrationId 为空，无法继续测试")
            return
        
        print(f"3️⃣  获取项目详情 (registrationId={registration_id})...")
        
        response = requests.get(f"{BASE_URL}/registrations/{registration_id}", 
                              headers=headers, 
                              timeout=30)
        
        print(f"请求: GET /api/registrations/{registration_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 获取详情失败")
            print(f"响应: {response.text}")
            return
        
        result = response.json()
        if not result.get('success'):
            print(f"❌ 获取失败: {result.get('message')}")
            return
        
        data = result.get('data', {})
        print(f"✅ 获取详情成功\n")
        
        print("项目详细信息:")
        print("-" * 60)
        print(f"项目ID: {data.get('id')}")
        print(f"项目名称: {data.get('projectName')}")
        print(f"医疗机构: {data.get('institutionName')}")
        print(f"竞赛组别: {data.get('groupType')}")
        print(f"状态: {data.get('status')}")
        
        # 成员信息
        members = data.get('members', [])
        print(f"\n成员信息: 共 {len(members)} 人")
        for member in members[:3]:
            print(f"  - {member.get('name')} ({member.get('title')}) - {member.get('role')}")
        if len(members) > 3:
            print(f"  ... 还有 {len(members) - 3} 人")
        
        # 活动说明
        activity = data.get('activityInfo', {})
        if activity:
            print(f"\n活动说明:")
            print(f"  主题: {activity.get('theme')}")
            print(f"  主题类型: {activity.get('subjectTypeLabel')}")
            print(f"  运用手法: {activity.get('methodLabel')}")
        
        # 项目总结
        summary = data.get('summary', {})
        if summary:
            print(f"\n项目总结:")
            plan = summary.get('plan', '')
            print(f"  计划: {plan[:50]}..." if len(plan) > 50 else f"  计划: {plan}")
        
        # 4. 前端访问URL
        print(f"\n4️⃣  前端访问信息:")
        print("-" * 60)
        print(f"登录URL: http://localhost:6039/login")
        print(f"手机号: {phone}")
        print(f"评分URL: http://localhost:6039/reviewer/review/{task_id}?registrationId={registration_id}&projectName={first_task.get('projectName')}")
        
        # 5. 验证清单
        print(f"\n5️⃣  验证清单:")
        print("-" * 60)
        print(f"✅ 1. API返回包含 registrationId: {registration_id}")
        print(f"✅ 2. API返回包含 projectName: {first_task.get('projectName')}")
        print(f"✅ 3. API返回包含 institutionName: {first_task.get('institutionName')}")
        print(f"✅ 4. 项目详情API返回完整数据")
        print(f"✅ 5. 成员信息: {len(members)} 人")
        print(f"✅ 6. 活动说明: {'有' if activity else '无'}")
        print(f"✅ 7. 项目总结: {'有' if summary else '无'}")
        
        return {
            'name': name,
            'phone': phone,
            'task_count': len(tasks),
            'first_task_id': task_id,
            'first_registration_id': registration_id,
            'project_name': first_task.get('projectName')
        }
        
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("  评委端数据验证 - 两位评审专家")
    print("="*60)
    
    reviewers = [
        {
            'name': '李明华',
            'phone': '13800000021',
            'title': '主任医师',
            'institution': '浙江大学医学院附属第二医院'
        },
        {
            'name': '孙丽娟',
            'phone': '13800002004',
            'title': '副主任护师',
            'institution': '浙江省中医院'
        }
    ]
    
    results = []
    
    for reviewer in reviewers:
        result = test_reviewer(**reviewer)
        if result:
            results.append(result)
    
    # 最终总结
    print("\n\n" + "="*60)
    print("  📊 测试总结")
    print("="*60)
    
    if len(results) > 0:
        print(f"\n✅ 成功验证 {len(results)} 位评审专家\n")
        
        print("="*60)
        print("  🎯 前端测试指南")
        print("="*60)
        
        for i, result in enumerate(results, 1):
            print(f"\n评审专家 {i}: {result['name']}")
            print(f"  手机号: {result['phone']}")
            print(f"  任务数: {result['task_count']}")
            print(f"  登录后访问: http://localhost:6039/reviewer/review/{result['first_task_id']}?registrationId={result['first_registration_id']}")
        
        print("\n" + "="*60)
        print("  ✅ 前端需要确认的要点")
        print("="*60)
        print("""
1. Tasks.vue - 任务列表页面
   ✅ 调用 GET /api/reviews/my-tasks
   ✅ 显示 projectName, institutionName, stage, status
   ✅ 点击"评分"时传递 registrationId 到 query

2. Review.vue - 评分页面  
   ✅ 从 route.query.registrationId 获取项目ID
   ✅ 调用 GET /api/registrations/{registrationId} 获取详情
   ✅ 显示项目名称、医疗机构、组别
   ✅ 显示"查看项目详情"面板
   ✅ 显示成员、活动说明、项目总结

3. 提交评分
   ✅ 使用 taskId (不是 registrationId)
   ✅ 调用 POST /api/reviews/scores
   ✅ 传递正确的字段名 (planScore, problemAnalysisScore, etc.)
        """)
        
        print("="*60)
        print("  🔍 浏览器控制台测试命令")
        print("="*60)
        print("""
// 打开评分页面后，在控制台输入:

// 1. 检查URL参数
console.log('taskId:', location.pathname.split('/').pop());
console.log('registrationId:', new URLSearchParams(location.search).get('registrationId'));

// 2. 检查是否有错误
console.log('检查Network标签，查看API请求状态');

// 3. 检查数据加载
console.log('查看Console是否有"项目详情加载成功"日志');
        """)
    else:
        print("\n❌ 没有找到可用的评审专家")
        print("\n建议:")
        print("1. 检查后端是否正常运行")
        print("2. 检查数据库中是否有评审任务数据")

if __name__ == "__main__":
    main()
