#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找有评审任务的评审专家
"""

import sys
import io
import requests
import json

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031/api"

# 测试用的评审专家账号列表
REVIEWERS = [
    {"phone": "13800000021", "name": "Reviewer A", "role": "REVIEWER"},
    {"phone": "13800000022", "name": "Reviewer B", "role": "REVIEWER"},
    {"phone": "13800000023", "name": "Reviewer C", "role": "REVIEWER"},
    {"phone": "13800000024", "name": "Reviewer D", "role": "REVIEWER"},
    {"phone": "13800000025", "name": "Reviewer E", "role": "REVIEWER"},
    {"phone": "13800000026", "name": "Reviewer F", "role": "REVIEWER"},
]

def check_reviewer_tasks(reviewer):
    """检查评审专家的任务"""
    print(f"\n检查评审专家: {reviewer['name']} ({reviewer['phone']})")
    
    # 登录
    try:
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json=reviewer, 
                               timeout=30)
        
        if response.status_code != 200:
            print(f"  ❌ 登录失败: {response.status_code}")
            return None
        
        result = response.json()
        token = result.get('data', {}).get('token')
        print(f"  ✅ 登录成功")
        
    except Exception as e:
        print(f"  ❌ 登录异常: {e}")
        return None
    
    # 获取任务列表
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/reviews/my-tasks", 
                              headers=headers, 
                              timeout=30)
        
        if response.status_code != 200:
            print(f"  ❌ 获取任务失败: {response.status_code}")
            return None
        
        result = response.json()
        tasks = result.get('data', [])
        
        if len(tasks) > 0:
            print(f"  ✅ 有 {len(tasks)} 个任务")
            
            # 显示第一个任务的详情
            task = tasks[0]
            print(f"    任务ID: {task.get('id')}")
            print(f"    项目ID: {task.get('registrationId')}")
            print(f"    项目名: {task.get('projectName')}")
            print(f"    状态: {task.get('status')}")
            
            return {
                'reviewer': reviewer,
                'task_count': len(tasks),
                'first_task': task
            }
        else:
            print(f"  ⚠️  暂无任务")
            return None
            
    except Exception as e:
        print(f"  ❌ 获取任务异常: {e}")
        return None

def main():
    print("=" * 60)
    print("  查找有评审任务的评审专家")
    print("=" * 60)
    
    reviewers_with_tasks = []
    
    for reviewer in REVIEWERS:
        result = check_reviewer_tasks(reviewer)
        if result:
            reviewers_with_tasks.append(result)
    
    print("\n" + "=" * 60)
    print("  汇总结果")
    print("=" * 60)
    
    if len(reviewers_with_tasks) >= 4:
        print(f"\n✅ 找到 {len(reviewers_with_tasks)} 位有任务的评审专家\n")
        
        print("=" * 60)
        print("  前端测试用的评审专家登录信息")
        print("=" * 60)
        
        for i, item in enumerate(reviewers_with_tasks[:4], 1):
            reviewer = item['reviewer']
            task = item['first_task']
            print(f"\n评审专家 {i}:")
            print(f"  手机号: {reviewer['phone']}")
            print(f"  姓名: {reviewer['name']}")
            print(f"  角色: REVIEWER")
            print(f"  任务数: {item['task_count']}")
            print(f"  访问URL: http://localhost:6039/reviewer/review/{task.get('id')}?registrationId={task.get('registrationId')}&projectName={task.get('projectName')}")
        
        print("\n" + "=" * 60)
        print("  快速测试步骤")
        print("=" * 60)
        print("\n1. 打开浏览器访问: http://localhost:6039/login")
        print("\n2. 选择以下任一评审专家登录:")
        for i, item in enumerate(reviewers_with_tasks[:4], 1):
            reviewer = item['reviewer']
            print(f"   {i}. 手机号: {reviewer['phone']} (姓名: {reviewer['name']})")
        
        print("\n3. 登录后点击'评审任务'菜单")
        print("\n4. 查看任务列表，点击'评分'按钮")
        print("\n5. 应该能看到完整的项目信息：")
        print("   - 项目名称")
        print("   - 医疗机构")
        print("   - 竞赛组别")
        print("   - 项目详情（展开查看）")
        
    else:
        print(f"\n⚠️  只找到 {len(reviewers_with_tasks)} 位有任务的评审专家")
        print("\n建议:")
        print("1. 在管理端为评审专家分配评审任务")
        print("2. 确保评审任务的 registrationId 不为空")
        print("3. 重新运行此脚本")

if __name__ == "__main__":
    main()
