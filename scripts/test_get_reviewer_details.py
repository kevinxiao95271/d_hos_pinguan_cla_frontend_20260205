#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试获取评委详细打分的方法
"""

import sys
import io
import requests
import json

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = 'http://localhost:6031'

# 测试用户（组委会管理员）
TEST_USER = {
    'phone': '13800000041',
    'password': '123456',
    'name': 'CommitteeAdmin A',
    'title': '主任',
    'role': 'COMMITTEE_ADMIN',
    'institutionId': 1
}

def login():
    """登录并获取token"""
    print('🔐 正在登录...')
    
    response = requests.post(
        f'{BASE_URL}/api/auth/login',
        json=TEST_USER,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            token = result.get('data', {}).get('token')
            print(f'✅ 登录成功！')
            return token
    return None

def test_admin_review_tasks(token, registration_id):
    """测试获取某个项目的所有评审任务"""
    print(f'\n📊 测试: 获取项目{registration_id}的评审任务')
    print('=' * 80)
    
    # 先获取所有书审任务
    response = requests.get(
        f'{BASE_URL}/api/admin/reviews/tasks',
        params={'competitionId': 21, 'stage': 'BOOK'},
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            all_tasks = result.get('data', [])
            print(f'✅ 获取到所有书审任务: {len(all_tasks)} 条')
            
            # 筛选出指定项目的任务
            project_tasks = [t for t in all_tasks if t.get('registrationId') == registration_id]
            print(f'✅ 项目{registration_id}的任务: {len(project_tasks)} 条')
            
            if project_tasks:
                print(f'\n任务详情:')
                for i, task in enumerate(project_tasks, 1):
                    print(f'\n--- 任务 {i} ---')
                    print(json.dumps(task, indent=2, ensure_ascii=False))
                
                return project_tasks
            else:
                print(f'⚠️  该项目没有评审任务')
                return []
    return []

def test_review_score(token, review_task_id):
    """测试获取单个评审任务的评分"""
    print(f'\n📊 测试: 获取评审任务{review_task_id}的评分')
    print('=' * 80)
    
    response = requests.get(
        f'{BASE_URL}/api/reviews/scores/{review_task_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    print(f'状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            score = result.get('data')
            print(f'✅ 获取成功')
            print(f'\n评分详情:')
            print(json.dumps(score, indent=2, ensure_ascii=False))
            return score
        else:
            print(f'❌ 请求失败: {result.get("message")}')
    else:
        print(f'❌ HTTP {response.status_code} 错误')
        print(f'响应: {response.text[:500]}')
    
    return None

def main():
    print('🧪 测试获取评委详细打分')
    print('=' * 80)
    
    # 登录
    token = login()
    if not token:
        return
    
    # 测试项目ID 106（护理交接班规范化-1）
    registration_id = 106
    
    # 1. 获取该项目的所有评审任务
    tasks = test_admin_review_tasks(token, registration_id)
    
    if tasks:
        # 2. 获取每个任务的评分详情
        print('\n' + '=' * 80)
        print('📊 获取每个评委的详细评分:')
        print('=' * 80)
        
        reviewer_scores = []
        for task in tasks:
            task_id = task.get('id')
            reviewer_name = task.get('reviewerName')
            status = task.get('status')
            
            print(f'\n评委: {reviewer_name} (任务ID: {task_id}, 状态: {status})')
            
            if status == 'SCORED':
                score = test_review_score(token, task_id)
                if score:
                    reviewer_scores.append({
                        'task': task,
                        'score': score
                    })
            else:
                print(f'⚠️  该任务状态为 {status}，无评分')
        
        # 3. 总结
        print('\n' + '=' * 80)
        print('📝 总结:')
        print(f'   项目ID: {registration_id}')
        print(f'   分配的评委数: {len(tasks)}')
        print(f'   已完成评分的评委数: {len(reviewer_scores)}')
        
        if reviewer_scores:
            print(f'\n✅ 可以通过以下方式获取评委详细评分:')
            print(f'   1. 调用 /api/admin/reviews/tasks 获取任务列表')
            print(f'   2. 筛选出指定项目的任务')
            print(f'   3. 对每个已完成的任务，调用 /api/reviews/scores/{{taskId}} 获取评分')
        else:
            print(f'\n⚠️  没有已完成的评分')

if __name__ == '__main__':
    main()
