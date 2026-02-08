#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试入围管理页面使用的API
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
        else:
            print(f'❌ 登录失败: {result.get("message")}')
            return None
    else:
        print(f'❌ 登录请求失败: {response.status_code}')
        return None

def test_rankings_api(token):
    """测试 /api/admin/reviews/rankings"""
    print(f'\n📊 测试 1: /api/admin/reviews/rankings (书审)')
    print('=' * 80)
    
    response = requests.get(
        f'{BASE_URL}/api/admin/reviews/rankings',
        params={'competitionId': 21, 'stage': 'BOOK'},
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    print(f'状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result.get('data', [])
            print(f'✅ 获取成功: {len(data)} 条记录')
            if data:
                print(f'\n第一条数据示例:')
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
            return True
        else:
            print(f'❌ 请求失败: {result.get("message")}')
            return False
    else:
        print(f'❌ HTTP 错误')
        print(f'响应内容: {response.text[:500]}')
        return False

def test_review_details_api(token, registration_id):
    """测试 /api/registrations/{id}/review-details"""
    print(f'\n📊 测试 2: /api/registrations/{registration_id}/review-details')
    print('=' * 80)
    
    response = requests.get(
        f'{BASE_URL}/api/registrations/{registration_id}/review-details',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    print(f'状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result.get('data', [])
            print(f'✅ 获取成功: {len(data)} 条记录')
            if data:
                print(f'\n返回数据:')
                print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f'❌ 请求失败: {result.get("message")}')
            print(f'完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}')
            return False
    else:
        print(f'❌ HTTP {response.status_code} 错误')
        print(f'响应内容: {response.text[:500]}')
        return False

def test_reviewer_scores_api(token, registration_id, stage):
    """测试 /api/registrations/{id}/reviewer-scores"""
    print(f'\n📊 测试 3: /api/registrations/{registration_id}/reviewer-scores?stage={stage}')
    print('=' * 80)
    
    response = requests.get(
        f'{BASE_URL}/api/registrations/{registration_id}/reviewer-scores',
        params={'stage': stage},
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    print(f'状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result.get('data', [])
            print(f'✅ 获取成功: {len(data)} 条记录')
            if data:
                print(f'\n第一条数据示例:')
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
            return True
        else:
            print(f'❌ 请求失败: {result.get("message")}')
            print(f'完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}')
            return False
    else:
        print(f'❌ HTTP {response.status_code} 错误')
        print(f'响应内容: {response.text[:500]}')
        return False

def main():
    print('🧪 测试入围管理页面使用的API')
    print('=' * 80)
    
    # 登录
    token = login()
    if not token:
        return
    
    # 测试1: rankings API (书审)
    success1 = test_rankings_api(token)
    
    # 测试2: review-details API
    # 使用项目ID 106（护理交接班规范化-1）
    registration_id = 106
    success2 = test_review_details_api(token, registration_id)
    
    # 测试3: reviewer-scores API (书审)
    success3 = test_reviewer_scores_api(token, registration_id, 'BOOK')
    
    # 测试4: reviewer-scores API (面谈)
    success4 = test_reviewer_scores_api(token, registration_id, 'INTERVIEW')
    
    print('\n' + '=' * 80)
    print('📝 测试结果总结:')
    print(f'   rankings API (书审): {"✅ 成功" if success1 else "❌ 失败"}')
    print(f'   review-details API: {"✅ 成功" if success2 else "❌ 失败"}')
    print(f'   reviewer-scores API (书审): {"✅ 成功" if success3 else "❌ 失败"}')
    print(f'   reviewer-scores API (面谈): {"✅ 成功" if success4 else "❌ 失败"}')
    
    if not success2:
        print('\n⚠️  review-details API 有问题！')
        print('   这是入围管理页面点击详情时调用的API')
        print('   请检查后端接口是否正确实现')

if __name__ == '__main__':
    main()
