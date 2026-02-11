#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试赛事详情API
GET /api/competition/{id}
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


def test_competition_detail(token, competition_id):
    """测试赛事详情API"""
    url = f'{BASE_URL}/competitions/{competition_id}'
    headers = {'Authorization': f'Bearer {token}'}
    
    print('=' * 80)
    print('📊 测试赛事详情API')
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
                competition = data.get('data', {})
                
                print('=' * 80)
                print('📦 返回数据结构:')
                print('=' * 80)
                print(json.dumps(competition, ensure_ascii=False, indent=2))
                
                print('\n' + '=' * 80)
                print('🔍 关键字段检查（阶段时间）:')
                print('=' * 80)
                
                # 检查时间字段
                time_fields = [
                    ('registrationStartTime', '报名开始时间'),
                    ('registrationEndTime', '报名结束时间'),
                    ('bookStartTime', '书审开始时间'),
                    ('bookEndTime', '书审结束时间'),
                    ('interviewStartTime', '面谈开始时间'),
                    ('interviewEndTime', '面谈结束时间'),
                    ('finalStartTime', '决赛开始时间'),
                    ('finalEndTime', '决赛结束时间'),
                ]
                
                for field_name, field_label in time_fields:
                    field_value = competition.get(field_name)
                    if field_value:
                        print(f'   ✅ {field_label} ({field_name}): {field_value}')
                    else:
                        print(f'   ❌ {field_label} ({field_name}): 缺失或为null')
                
                # 其他关键字段
                print('\n' + '=' * 80)
                print('🔍 其他关键字段:')
                print('=' * 80)
                other_fields = [
                    ('id', '赛事ID'),
                    ('name', '赛事名称'),
                    ('currentStage', '当前阶段'),
                    ('status', '状态'),
                ]
                
                for field_name, field_label in other_fields:
                    field_value = competition.get(field_name)
                    if field_value:
                        print(f'   ✅ {field_label} ({field_name}): {field_value}')
                    else:
                        print(f'   ❌ {field_label} ({field_name}): 缺失或为null')
                
            else:
                print(f'⚠️ 业务失败: {data.get("message")}')
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            print(f'   响应: {response.text[:500]}')
    except Exception as e:
        print(f'❌ 异常: {e}')


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 25 + '赛事详情API测试' + ' ' * 25 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    # 登录
    token = login_as_contestant()
    if not token:
        print('❌ 无法获取token，终止测试')
        return 1
    
    # 测试赛事详情API（默认赛事ID=21）
    competition_id = 21
    print(f'🎯 测试赛事ID: {competition_id}\n')
    test_competition_detail(token, competition_id)
    
    print('\n' + '=' * 80)
    print('✅ 测试完成')
    print('=' * 80)
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
