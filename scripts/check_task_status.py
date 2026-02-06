#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查评分后的任务状态
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

def get_tasks(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/reviews/my-tasks", headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('data', []) if result.get('success') else []
    return []

def main():
    print("\n" + "="*60)
    print("  检查任务状态")
    print("="*60)
    
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功\n")
    
    tasks = get_tasks(token)
    
    print(f"总任务数: {len(tasks)}\n")
    
    # 统计各状态的任务数
    status_count = {}
    for task in tasks:
        status = task.get('status', 'UNKNOWN')
        status_count[status] = status_count.get(status, 0) + 1
    
    print("="*60)
    print("任务状态统计:")
    print("="*60)
    for status, count in status_count.items():
        print(f"  {status}: {count} 个")
    
    print("\n" + "="*60)
    print("任务详情:")
    print("="*60)
    
    for i, task in enumerate(tasks, 1):
        print(f"\n任务 {i}:")
        print(f"  ID: {task.get('id')}")
        print(f"  项目: {task.get('projectName')}")
        print(f"  状态: {task.get('status')}")
        print(f"  阶段: {task.get('stage')}")
    
    print("\n" + "="*60)
    print("前端统计逻辑检查:")
    print("="*60)
    
    total = len(tasks)
    completed = len([t for t in tasks if t.get('status') == 'COMPLETED'])
    scored = len([t for t in tasks if t.get('status') == 'SCORED'])
    pending = len([t for t in tasks if t.get('status') == 'PENDING'])
    
    print(f"\n如果前端用 status === 'COMPLETED':")
    print(f"  待评审: {pending}")
    print(f"  已评审: {completed}")
    print(f"  总任务数: {total}")
    print(f"  完成率: {round(completed / total * 100) if total > 0 else 0}%")
    
    print(f"\n如果前端用 status === 'SCORED':")
    print(f"  待评审: {pending}")
    print(f"  已评审: {scored}")
    print(f"  总任务数: {total}")
    print(f"  完成率: {round(scored / total * 100) if total > 0 else 0}%")
    
    print("\n" + "="*60)
    print("建议:")
    print("="*60)
    
    if scored > 0 and completed == 0:
        print("\n✅ 后端返回的状态是 'SCORED'，不是 'COMPLETED'")
        print("   前端需要修改统计逻辑:")
        print("   const completed = tasks.value.filter(t => t.status === 'SCORED').length")
    elif completed > 0:
        print("\n✅ 后端返回的状态是 'COMPLETED'")
        print("   前端统计逻辑正确")
    else:
        print("\n⚠️  所有任务都是 PENDING 状态")
        print("   请提交至少一个评分后重新测试")

if __name__ == "__main__":
    main()
