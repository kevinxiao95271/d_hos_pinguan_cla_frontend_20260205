#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试后端修复后Label字段的实际值
"""

import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = 'http://localhost:6031'

def test():
    print('🔍 测试后端修复后的Label字段')
    print('=' * 80)
    
    # 登录
    response = requests.post(
        f'{BASE_URL}/api/auth/login',
        json={'phone': '13800000041', 'name': 'CommitteeAdmin A', 'role': 'COMMITTEE_ADMIN'},
        timeout=30
    )
    
    if response.status_code != 200:
        print('❌ 登录失败')
        return
    
    token = response.json()['data']['token']
    print('✅ 登录成功')
    
    # 获取分组列表
    print('\n📊 获取书审分组列表')
    response = requests.get(
        f'{BASE_URL}/api/admin/registrations/interview-groups?competitionId=21',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code != 200:
        print('❌ 获取失败')
        return
    
    result = response.json()
    if not result.get('success') or not result.get('data'):
        print('❌ 没有数据')
        return
    
    groups = result['data']
    if not groups or not groups[0].get('items'):
        print('❌ 没有项目')
        return
    
    # 获取第一个项目的ID
    registration_id = groups[0]['items'][0]['registrationId']
    project_name = groups[0]['items'][0]['projectName']
    
    print(f'✅ 找到项目: {project_name} (ID: {registration_id})')
    
    # 获取详情
    print(f'\n📋 获取详情: GET /api/registrations/{registration_id}')
    response = requests.get(
        f'{BASE_URL}/api/registrations/{registration_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code != 200:
        print('❌ 获取详情失败')
        return
    
    result = response.json()
    if not result.get('success'):
        print('❌ 请求失败')
        return
    
    activity_info = result['data']['activityInfo']
    
    print('\n' + '=' * 80)
    print('【改善就医环境】')
    print('=' * 80)
    exp_code = activity_info.get('experienceImproveCode')
    exp_label = activity_info.get('experienceImproveLabel')
    
    print(f'Code:  "{exp_code}"')
    print(f'Label: "{exp_label}"')
    print(f'  类型: {type(exp_label)}')
    print(f'  长度: {len(exp_label) if exp_label else 0}')
    print(f'  是None: {exp_label is None}')
    print(f'  是空字符串: {exp_label == ""}')
    print(f'  布尔值: {bool(exp_label)}')
    print(f'  repr: {repr(exp_label)}')
    
    # 测试逻辑
    result_value = exp_label or exp_code
    print(f'\n逻辑测试: experienceImproveLabel || experienceImproveCode')
    print(f'  结果: "{result_value}"')
    print(f'  是Label? {result_value == exp_label}')
    
    print('\n' + '=' * 80)
    print('【医疗质量相关主题】')
    print('=' * 80)
    qual_code = activity_info.get('qualityTopicCode')
    qual_label = activity_info.get('qualityTopicLabel')
    
    print(f'Code:  "{qual_code}"')
    print(f'Label: "{qual_label}"')
    print(f'  类型: {type(qual_label)}')
    print(f'  长度: {len(qual_label) if qual_label else 0}')
    print(f'  是None: {qual_label is None}')
    print(f'  是空字符串: {qual_label == ""}')
    print(f'  布尔值: {bool(qual_label)}')
    print(f'  repr: {repr(qual_label)}')
    
    # 测试逻辑
    result_value = qual_label or qual_code
    print(f'\n逻辑测试: qualityTopicLabel || qualityTopicCode')
    print(f'  结果: "{result_value}"')
    print(f'  是Label? {result_value == qual_label}')
    
    print('\n' + '=' * 80)
    print('📝 完整的activityInfo:')
    print('=' * 80)
    print(json.dumps(activity_info, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    test()
