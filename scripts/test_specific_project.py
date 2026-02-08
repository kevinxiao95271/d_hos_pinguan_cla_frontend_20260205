#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试显示experience_3的具体项目
"""

import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = 'http://localhost:6031'

def test():
    print('🔍 测试显示experience_3的项目')
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
    
    # 获取分组列表，找到包含experience_3的项目
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
    groups = result.get('data', [])
    
    # 遍历所有分组，查找每个项目的详情
    print('\n🔍 检查所有项目的Label字段...')
    found_project = None
    
    for group in groups:
        for item in group.get('items', []):
            reg_id = item['registrationId']
            
            # 获取详情
            detail_response = requests.get(
                f'{BASE_URL}/api/registrations/{reg_id}',
                headers={'Authorization': f'Bearer {token}'},
                timeout=30
            )
            
            if detail_response.status_code == 200:
                detail_result = detail_response.json()
                if detail_result.get('success'):
                    activity_info = detail_result['data']['activityInfo']
                    exp_code = activity_info.get('experienceImproveCode')
                    
                    # 找到experience_3的项目
                    if exp_code == 'experience_3':
                        found_project = {
                            'id': reg_id,
                            'name': item['projectName'],
                            'activityInfo': activity_info
                        }
                        break
        
        if found_project:
            break
    
    if not found_project:
        print('❌ 没有找到experienceImproveCode为experience_3的项目')
        print('   尝试第一个项目...')
        
        # 使用第一个项目
        first_item = groups[0]['items'][0]
        reg_id = first_item['registrationId']
        
        response = requests.get(
            f'{BASE_URL}/api/registrations/{reg_id}',
            headers={'Authorization': f'Bearer {token}'},
            timeout=30
        )
        
        result = response.json()
        found_project = {
            'id': reg_id,
            'name': first_item['projectName'],
            'activityInfo': result['data']['activityInfo']
        }
    
    print(f'\n✅ 分析项目: {found_project["name"]} (ID: {found_project["id"]})')
    print('=' * 80)
    
    activity_info = found_project['activityInfo']
    
    print('\n【改善就医环境】')
    exp_code = activity_info.get('experienceImproveCode')
    exp_label = activity_info.get('experienceImproveLabel')
    exp_other = activity_info.get('experienceImproveOther')
    
    print(f'Code:  "{exp_code}"')
    print(f'Label: "{exp_label}"')
    print(f'Other: "{exp_other}"')
    print(f'\nLabel检查:')
    print(f'  类型: {type(exp_label)}')
    print(f'  值: {repr(exp_label)}')
    print(f'  长度: {len(exp_label) if exp_label else 0}')
    print(f'  是None: {exp_label is None}')
    print(f'  是空字符串: {exp_label == ""}')
    print(f'  布尔值: {bool(exp_label)}')
    
    # 模拟前端逻辑
    result_value = exp_label or exp_code
    print(f'\n前端逻辑: experienceImproveLabel || experienceImproveCode')
    print(f'  结果: "{result_value}"')
    print(f'  显示的是Label? {result_value == exp_label}')
    print(f'  显示的是Code? {result_value == exp_code}')
    
    print('\n【医疗质量相关主题】')
    qual_code = activity_info.get('qualityTopicCode')
    qual_label = activity_info.get('qualityTopicLabel')
    qual_other = activity_info.get('qualityTopicOther')
    
    print(f'Code:  "{qual_code}"')
    print(f'Label: "{qual_label}"')
    print(f'Other: "{qual_other}"')
    
    # 模拟前端逻辑
    result_value = qual_label or qual_code
    print(f'\n前端逻辑: qualityTopicLabel || qualityTopicCode')
    print(f'  结果: "{result_value}"')
    print(f'  显示的是Label? {result_value == qual_label}')
    
    print('\n' + '=' * 80)
    print('📝 完整的activityInfo:')
    print('=' * 80)
    print(json.dumps(activity_info, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    test()
