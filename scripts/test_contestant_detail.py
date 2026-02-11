#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试参赛者项目详情API
GET /api/registrations/{id}
"""

import sys
import codecs
import requests
import json

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = 'http://localhost:6031/api'

def login_as_contestant():
    """以参赛者身份登录"""
    url = f'{BASE_URL}/auth/login'
    data = {
        'phone': '13799999112',
        'name': '王建国',
        'role': 'CONTESTANT'
    }
    
    print('🔐 登录参赛者账号...')
    response = requests.post(url, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data', {}).get('token'):
            token = result['data']['token']
            print(f'✅ 登录成功: {data["name"]}\n')
            return token
    
    print('❌ 登录失败')
    return None


def test_registration_detail(token, registration_id):
    """测试报名详情API"""
    url = f'{BASE_URL}/registrations/{registration_id}'
    headers = {'Authorization': f'Bearer {token}'}
    
    print('=' * 80)
    print('📊 测试报名详情API')
    print('=' * 80)
    print(f'API端点: {url}')
    print(f'Method: GET\n')
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f'Status Code: {response.status_code}\n')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API调用成功\n')
            
            if data.get('success'):
                detail = data.get('data', {})
                
                print('=' * 80)
                print('📦 返回数据结构:')
                print('=' * 80)
                print(json.dumps(detail, ensure_ascii=False, indent=2))
                
                print('\n' + '=' * 80)
                print('🔍 关键字段检查:')
                print('=' * 80)
                
                # 检查主要字段
                checks = [
                    ('registration', detail.get('registration')),
                    ('registration.id', detail.get('registration', {}).get('id')),
                    ('registration.competitionId', detail.get('registration', {}).get('competitionId')),
                    ('registration.projectName', detail.get('registration', {}).get('projectName')),
                    ('registration.institutionName', detail.get('registration', {}).get('institutionName')),
                    ('registration.groupType', detail.get('registration', {}).get('groupType')),
                    ('registration.submittedAt', detail.get('registration', {}).get('submittedAt')),
                    ('institution', detail.get('institution')),
                    ('institution.name', detail.get('institution', {}).get('name')),
                    ('institution.level', detail.get('institution', {}).get('level')),
                    ('institution.code', detail.get('institution', {}).get('code')),
                    ('members', detail.get('members')),
                    ('activityInfo', detail.get('activityInfo')),
                    ('projectSummary', detail.get('projectSummary')),
                ]
                
                for field_name, field_value in checks:
                    if field_value:
                        value_preview = str(field_value)[:100] if not isinstance(field_value, (dict, list)) else type(field_value).__name__
                        print(f'   ✅ {field_name}: {value_preview}')
                    else:
                        print(f'   ❌ {field_name}: 缺失')
                
                # 统计成员
                members = detail.get('members', [])
                if members:
                    print(f'\n   成员总数: {len(members)}')
                    participants = [m for m in members if m.get('role') == 'PARTICIPANT']
                    mentors = [m for m in members if m.get('role') == 'MENTOR']
                    print(f'   - 圈员: {len(participants)} 人')
                    print(f'   - 辅导员: {len(mentors)} 人')
                
            else:
                print(f'⚠️ 业务失败: {data.get("message")}')
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            print(f'   响应: {response.text[:500]}')
    except Exception as e:
        print(f'❌ 异常: {e}')


def get_my_registrations(token):
    """获取我的报名列表，找到第一个报名ID"""
    url = f'{BASE_URL}/registrations/my'
    headers = {'Authorization': f'Bearer {token}'}
    
    print('📋 获取我的报名列表...')
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Response: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}')
            if data.get('success') and data.get('data'):
                registrations = data['data']
                if registrations:
                    first_id = registrations[0].get('id')
                    project_name = registrations[0].get('projectName')
                    print(f'✅ 找到报名记录: ID={first_id}, 项目名={project_name}\n')
                    return first_id
                else:
                    print('⚠️ 该账号暂无报名记录，使用测试ID=106\n')
                    return 106
        else:
            print(f'   Error: {response.text[:200]}')
            print('⚠️ 获取失败，使用测试ID=106\n')
            return 106
    except Exception as e:
        print(f'❌ 获取报名列表失败: {e}，使用测试ID=106\n')
        return 106


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 22 + '参赛者项目详情测试' + ' ' * 23 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    # 登录
    token = login_as_contestant()
    if not token:
        print('❌ 无法获取token，终止测试')
        return 1
    
    # 获取报名ID（如果没有就使用测试ID）
    registration_id = get_my_registrations(token)
    if not registration_id:
        registration_id = 106  # 使用已知的测试ID
        print(f'⚠️ 使用默认测试ID: {registration_id}\n')
    
    # 测试报名详情API
    test_registration_detail(token, registration_id)
    
    print('\n' + '=' * 80)
    print('✅ 测试完成')
    print('=' * 80)
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
