#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试评审任务API
GET /api/admin/reviews/tasks
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

def login_as_committee():
    """以组委会管理员身份登录"""
    url = f'{BASE_URL}/auth/login'
    data = {
        'phone': '13800000127',
        'name': 'CommitteeAdmin A',
        'role': 'COMMITTEE_ADMIN'
    }
    
    print('🔐 登录组委会管理员账号...')
    response = requests.post(url, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data', {}).get('token'):
            token = result['data']['token']
            print(f'✅ 登录成功: {data["name"]}\n')
            return token
    
    print('❌ 登录失败')
    return None


def test_admin_review_tasks_api(token, stage):
    """测试管理端评审任务API"""
    url = f'{BASE_URL}/admin/reviews/tasks'
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'competitionId': 21,
        'stage': stage
    }
    
    print('=' * 80)
    print(f'📊 测试评审任务API - {stage}阶段')
    print('=' * 80)
    print(f'API端点: {url}')
    print(f'参数: {params}\n')
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f'Status Code: {response.status_code}\n')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API调用成功\n')
            
            if data.get('success'):
                tasks = data.get('data', [])
                print(f'📈 任务总数: {len(tasks)}\n')
                
                if tasks:
                    print('=' * 80)
                    print('📦 第一条任务数据:')
                    print('=' * 80)
                    print(json.dumps(tasks[0], ensure_ascii=False, indent=2))
                else:
                    print('⚠️ 该阶段暂无任务')
            else:
                print(f'⚠️ 业务失败: {data.get("message")}')
        elif response.status_code == 500:
            print(f'❌ 服务器内部错误 (500)\n')
            try:
                error_data = response.json()
                print('错误详情:')
                print(json.dumps(error_data, ensure_ascii=False, indent=2))
            except:
                print('错误响应:')
                print(response.text[:1000])
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            print(f'   响应: {response.text[:500]}')
    except Exception as e:
        print(f'❌ 异常: {e}')


def test_review_tasks_by_stage_api(token, stage):
    """测试评审任务API - 按阶段查询（备用API）"""
    url = f'{BASE_URL}/reviews/tasks/stage'
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'competitionId': 21,
        'stage': stage
    }
    
    print('=' * 80)
    print(f'📊 测试评审任务API(备用) - {stage}阶段')
    print('=' * 80)
    print(f'API端点: {url}')
    print(f'参数: {params}\n')
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f'Status Code: {response.status_code}\n')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API调用成功\n')
            
            if data.get('success'):
                tasks = data.get('data', [])
                print(f'📈 任务总数: {len(tasks)}\n')
                
                if tasks:
                    print('=' * 80)
                    print('📦 第一条任务数据:')
                    print('=' * 80)
                    print(json.dumps(tasks[0], ensure_ascii=False, indent=2))
                    
                    print('\n' + '=' * 80)
                    print('🔍 字段检查:')
                    print('=' * 80)
                    first = tasks[0]
                    fields = ['id', 'registrationId', 'reviewerId', 'stage', 'status', 
                             'projectName', 'reviewerName', 'institutionName']
                    for field in fields:
                        value = first.get(field)
                        status = '✅' if value is not None else '❌'
                        print(f'   {status} {field}: {value}')
                else:
                    print('⚠️ 该阶段暂无任务')
            else:
                print(f'⚠️ 业务失败: {data.get("message")}')
        elif response.status_code == 500:
            print(f'❌ 服务器内部错误 (500)\n')
            try:
                error_data = response.json()
                print('错误详情:')
                print(json.dumps(error_data, ensure_ascii=False, indent=2))
            except:
                print('错误响应:')
                print(response.text[:1000])
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            print(f'   响应: {response.text[:500]}')
    except Exception as e:
        print(f'❌ 异常: {e}')


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 24 + '评审任务API测试' + ' ' * 24 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    # 登录
    token = login_as_committee()
    if not token:
        print('❌ 无法获取token，终止测试')
        return 1
    
    print('\n' + '🔥' * 40)
    print('测试方案1: /admin/reviews/tasks (当前使用的API)')
    print('🔥' * 40 + '\n')
    
    # 测试书审阶段
    test_admin_review_tasks_api(token, 'BOOK')
    
    print('\n')
    
    # 测试面谈阶段
    test_admin_review_tasks_api(token, 'INTERVIEW')
    
    print('\n' + '🔥' * 40)
    print('测试方案2: /reviews/tasks/stage (备用API)')
    print('🔥' * 40 + '\n')
    
    # 测试备用API - 书审阶段
    test_review_tasks_by_stage_api(token, 'BOOK')
    
    print('\n')
    
    # 测试备用API - 面谈阶段
    test_review_tasks_by_stage_api(token, 'INTERVIEW')
    
    print('\n' + '=' * 80)
    print('✅ 测试完成')
    print('=' * 80)
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
