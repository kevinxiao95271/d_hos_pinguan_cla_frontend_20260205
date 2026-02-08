#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试所有场景的API，检查experienceImproveLabel和qualityTopicLabel字段
"""

import sys
import io
import requests
import json

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = 'http://localhost:6031'

# 测试账号
ACCOUNTS = {
    'contestant': {'phone': '13800000001', 'name': '张三', 'role': 'CONTESTANT'},
    'committee': {'phone': '13800000041', 'name': 'CommitteeAdmin A', 'role': 'COMMITTEE_ADMIN'},
    'reviewer': {'phone': '13900000001', 'name': '李明华', 'role': 'REVIEWER'}
}

def login(account_type):
    """登录并获取token"""
    account = ACCOUNTS[account_type]
    print(f'\n🔐 登录 {account_type} 账号...')
    print(f'   手机号: {account["phone"]}')
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/auth/login',
            json=account,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('data', {}).get('token')
                print(f'✅ 登录成功！')
                return token
            else:
                print(f'❌ 登录失败: {result.get("message")}')
                return None
        else:
            print(f'❌ 登录请求失败: {response.status_code}')
            return None
    except Exception as e:
        print(f'❌ 登录异常: {e}')
        return None

def check_labels(data, api_name, scenario):
    """检查Label字段"""
    activity_info = None
    
    # 不同API的数据结构不同
    if 'activityInfo' in data:
        activity_info = data['activityInfo']
    elif 'registration' in data and 'activityInfo' in data:
        activity_info = data['activityInfo']
    
    if not activity_info:
        print(f'   ⚠️  没有找到 activityInfo 对象')
        return False
    
    print(f'\n   📋 {api_name} - {scenario}')
    print(f'   ' + '=' * 70)
    
    # 检查改善就医环境
    exp_code = activity_info.get('experienceImproveCode')
    exp_label = activity_info.get('experienceImproveLabel')
    exp_other = activity_info.get('experienceImproveOther')
    
    print(f'   【改善就医环境】')
    print(f'     experienceImproveCode:  {exp_code}')
    print(f'     experienceImproveLabel: {exp_label} {"✅" if exp_label else "❌ 缺失"}')
    print(f'     experienceImproveOther: {exp_other}')
    
    # 检查医疗质量相关主题
    qual_code = activity_info.get('qualityTopicCode')
    qual_label = activity_info.get('qualityTopicLabel')
    qual_other = activity_info.get('qualityTopicOther')
    
    print(f'   【医疗质量相关主题】')
    print(f'     qualityTopicCode:  {qual_code}')
    print(f'     qualityTopicLabel: {qual_label} {"✅" if qual_label else "❌ 缺失"}')
    print(f'     qualityTopicOther: {qual_other}')
    
    has_both = bool(exp_label) and bool(qual_label)
    
    if has_both:
        print(f'   ✅ 该API返回了完整的Label字段')
    else:
        print(f'   ❌ 该API缺少Label字段')
    
    return has_both

def test_scenario_1_contestant(token):
    """场景1: 参赛者 - 我的报名"""
    print(f'\n' + '=' * 80)
    print(f'📊 场景1: 参赛者 - 我的报名详情')
    print(f'=' * 80)
    
    # 先获取我的报名列表
    print(f'\n步骤1: 获取我的报名列表')
    response = requests.get(
        f'{BASE_URL}/api/registrations/my',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f'❌ 获取列表失败: {response.status_code}')
        return
    
    result = response.json()
    if not result.get('success'):
        print(f'❌ 请求失败: {result.get("message")}')
        return
    
    data = result.get('data', [])
    if not data:
        print(f'❌ 列表为空')
        return
    
    # 尝试不同的字段名
    first_item = data[0]
    registration_id = first_item.get('id') or first_item.get('registrationId')
    
    if not registration_id:
        print(f'❌ 无法获取报名ID，数据结构: {first_item.keys()}')
        return
        
    print(f'✅ 找到报名ID: {registration_id}')
    
    # 获取详情
    print(f'\n步骤2: 获取报名详情')
    print(f'API: GET /api/registrations/{registration_id}')
    
    response = requests.get(
        f'{BASE_URL}/api/registrations/{registration_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data'):
            print(f'✅ 获取成功')
            check_labels(result['data'], 'GET /api/registrations/{id}', '参赛者查看自己的报名')
        else:
            print(f'❌ 请求失败: {result.get("message")}')
    else:
        print(f'❌ HTTP {response.status_code}')

def test_scenario_2_committee_book(token):
    """场景2: 组委会 - 书审分组 - 项目详情"""
    print(f'\n' + '=' * 80)
    print(f'📊 场景2: 组委会 - 书审分组 - 项目详情')
    print(f'=' * 80)
    
    # 先获取书审分组列表
    print(f'\n步骤1: 获取书审分组列表')
    print(f'API: GET /api/admin/registrations/interview-groups?competitionId=21')
    
    response = requests.get(
        f'{BASE_URL}/api/admin/registrations/interview-groups?competitionId=21',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f'❌ 获取列表失败: {response.status_code}')
        return
    
    result = response.json()
    if not result.get('success') or not result.get('data'):
        print(f'❌ 列表为空或请求失败')
        return
    
    # 找到第一个分组的第一个项目
    groups = result['data']
    if not groups or not groups[0].get('items'):
        print(f'❌ 没有找到项目')
        return
    
    # 打印数据结构
    print(f'   数据结构: {json.dumps(groups[0]["items"][0], indent=2, ensure_ascii=False)}')
    
    # 尝试不同的字段名
    first_item = groups[0]['items'][0]
    registration_id = first_item.get('id') or first_item.get('registrationId')
    
    if not registration_id:
        print(f'❌ 无法获取报名ID，数据结构: {first_item.keys()}')
        return
    
    print(f'✅ 找到报名ID: {registration_id}')
    
    # 获取详情
    print(f'\n步骤2: 获取报名详情')
    print(f'API: GET /api/registrations/{registration_id}')
    
    response = requests.get(
        f'{BASE_URL}/api/registrations/{registration_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data'):
            print(f'✅ 获取成功')
            check_labels(result['data'], 'GET /api/registrations/{id}', '组委会-书审分组详情')
        else:
            print(f'❌ 请求失败: {result.get("message")}')
    else:
        print(f'❌ HTTP {response.status_code}')

def test_scenario_3_committee_filter(token):
    """场景3: 组委会 - 筛选项目列表 - 项目详情"""
    print(f'\n' + '=' * 80)
    print(f'📊 场景3: 组委会 - 筛选项目列表 - 项目详情')
    print(f'=' * 80)
    
    # 先筛选项目
    print(f'\n步骤1: 筛选项目列表')
    print(f'API: GET /api/admin/registrations/filter?competitionId=21')
    
    response = requests.get(
        f'{BASE_URL}/api/admin/registrations/filter?competitionId=21',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f'❌ 筛选失败: {response.status_code}')
        return
    
    result = response.json()
    if not result.get('success') or not result.get('data'):
        print(f'❌ 列表为空或请求失败')
        return
    
    projects = result['data']
    if not projects:
        print(f'❌ 没有找到项目')
        return
    
    # 尝试不同的字段名
    first_project = projects[0]
    registration_id = first_project.get('id') or first_project.get('registrationId')
    
    if not registration_id:
        print(f'❌ 无法获取报名ID，数据结构: {first_project.keys()}')
        return
        
    print(f'✅ 找到报名ID: {registration_id}')
    
    # 检查筛选列表中是否有Label
    print(f'\n步骤1.5: 检查筛选列表中的Label字段')
    first_project = projects[0]
    print(f'   experienceImproveLabel: {first_project.get("experienceImproveLabel")} {"✅" if first_project.get("experienceImproveLabel") else "❌"}')
    print(f'   qualityTopicLabel: {first_project.get("qualityTopicLabel")} {"✅" if first_project.get("qualityTopicLabel") else "❌"}')
    
    # 获取详情
    print(f'\n步骤2: 获取报名详情')
    print(f'API: GET /api/registrations/{registration_id}')
    
    response = requests.get(
        f'{BASE_URL}/api/registrations/{registration_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data'):
            print(f'✅ 获取成功')
            check_labels(result['data'], 'GET /api/registrations/{id}', '组委会-筛选列表详情')
        else:
            print(f'❌ 请求失败: {result.get("message")}')
    else:
        print(f'❌ HTTP {response.status_code}')

def test_scenario_4_reviewer(token):
    """场景4: 评委 - 评审任务详情"""
    print(f'\n' + '=' * 80)
    print(f'📊 场景4: 评委 - 评审任务详情')
    print(f'=' * 80)
    
    # 先获取我的任务
    print(f'\n步骤1: 获取我的评审任务')
    print(f'API: GET /api/reviews/my-tasks?competitionId=21')
    
    response = requests.get(
        f'{BASE_URL}/api/reviews/my-tasks?competitionId=21',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f'❌ 获取任务失败: {response.status_code}')
        return
    
    result = response.json()
    if not result.get('success') or not result.get('data'):
        print(f'❌ 任务为空或请求失败')
        return
    
    tasks = result['data']
    if not tasks:
        print(f'❌ 没有找到任务')
        return
    
    # 尝试不同的字段名
    first_task = tasks[0]
    registration_id = first_task.get('registrationId') or first_task.get('id')
    
    if not registration_id:
        print(f'❌ 无法获取报名ID，数据结构: {first_task.keys()}')
        return
        
    print(f'✅ 找到报名ID: {registration_id}')
    
    # 获取详情
    print(f'\n步骤2: 获取报名详情')
    print(f'API: GET /api/registrations/{registration_id}')
    
    response = requests.get(
        f'{BASE_URL}/api/registrations/{registration_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data'):
            print(f'✅ 获取成功')
            check_labels(result['data'], 'GET /api/registrations/{id}', '评委-评审任务详情')
        else:
            print(f'❌ 请求失败: {result.get("message")}')
    else:
        print(f'❌ HTTP {response.status_code}')

def main():
    print('🧪 测试所有场景的Label字段')
    print('=' * 80)
    print('目标: 找出哪个场景的API缺少 experienceImproveLabel 和 qualityTopicLabel')
    print('=' * 80)
    
    # 场景1: 参赛者
    token_contestant = login('contestant')
    if token_contestant:
        test_scenario_1_contestant(token_contestant)
    
    # 场景2和3: 组委会
    token_committee = login('committee')
    if token_committee:
        test_scenario_2_committee_book(token_committee)
        test_scenario_3_committee_filter(token_committee)
    
    # 场景4: 评委
    token_reviewer = login('reviewer')
    if token_reviewer:
        test_scenario_4_reviewer(token_reviewer)
    
    print(f'\n' + '=' * 80)
    print(f'📝 结论:')
    print(f'=' * 80)
    print(f'所有场景都调用同一个API: GET /api/registrations/{{id}}')
    print(f'如果某个场景显示的是Code而不是Label，可能是:')
    print(f'  1. 前端代码中直接显示了Code字段，而不是Label')
    print(f'  2. 前端的处理函数有问题')
    print(f'  3. Label字段为空字符串（不是null或undefined）')

if __name__ == '__main__':
    main()
