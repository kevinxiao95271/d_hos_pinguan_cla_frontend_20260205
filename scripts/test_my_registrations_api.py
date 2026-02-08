#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试"我的报名"接口返回的数据结构
"""

import sys
import io
import requests
import json

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = 'http://localhost:6031'

# 测试用户（参赛者）
TEST_USER = {
    'phone': '13900000064',
    'password': '123456',
    'name': '张四',
    'title': '副主任护师',
    'role': 'CONTESTANT',
    'institutionId': 64
}

def login():
    """登录并获取token"""
    print('🔐 正在登录参赛者账号...')
    print(f'   手机号: {TEST_USER["phone"]}')
    
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

def test_my_registrations(token):
    """测试 /api/registrations/my"""
    print(f'\n📊 测试: GET /api/registrations/my')
    print('=' * 80)
    
    response = requests.get(
        f'{BASE_URL}/api/registrations/my',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    print(f'状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result.get('data', [])
            print(f'✅ 获取成功: {len(data)} 条报名记录')
            
            if data:
                print(f'\n第一条数据结构:')
                first = data[0]
                print(json.dumps(first, indent=2, ensure_ascii=False))
                
                print(f'\n📝 字段检查:')
                print('-' * 80)
                
                fields_to_check = [
                    ('id', 'ID'),
                    ('projectName', '项目名称'),
                    ('institutionName', '医疗机构名称'),
                    ('institutionLevel', '机构等级'),
                    ('groupType', '竞赛组别'),
                    ('status', '状态'),
                    ('createdAt', '创建时间'),
                    ('submittedAt', '提交时间'),
                    ('institution', '机构对象'),
                ]
                
                for field, desc in fields_to_check:
                    value = first.get(field)
                    has_value = value is not None and value != ''
                    status = '✅' if has_value else '❌'
                    print(f'{status} {desc:<15} ({field}): {value}')
                
                # 特别检查 institution 对象
                if first.get('institution'):
                    print(f'\n📦 institution 对象内容:')
                    print(json.dumps(first.get('institution'), indent=2, ensure_ascii=False))
                
            return True
        else:
            print(f'❌ 请求失败: {result.get("message")}')
            return False
    else:
        print(f'❌ HTTP {response.status_code} 错误')
        print(f'响应: {response.text[:500]}')
        return False

def test_registration_detail(token, registration_id):
    """测试 /api/registrations/{id} 详情接口"""
    print(f'\n📊 测试: GET /api/registrations/{registration_id}')
    print('=' * 80)
    
    response = requests.get(
        f'{BASE_URL}/api/registrations/{registration_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    print(f'状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result.get('data')
            print(f'✅ 获取成功')
            
            print(f'\n📝 机构相关字段:')
            print('-' * 80)
            print(f'institutionId: {data.get("institutionId")}')
            print(f'institutionName: {data.get("institutionName")}')
            
            if data.get('institution'):
                inst = data.get('institution')
                print(f'\ninstitution 对象:')
                print(f'  id: {inst.get("id")}')
                print(f'  name: {inst.get("name")}')
                print(f'  level: {inst.get("level")} {"✅" if inst.get("level") else "❌"}')
                print(f'  region: {inst.get("region")}')
            
            return True
        else:
            print(f'❌ 请求失败: {result.get("message")}')
            return False
    else:
        print(f'❌ HTTP {response.status_code} 错误')
        return False

def main():
    print('🧪 测试"我的报名"页面API')
    print('=' * 80)
    
    # 登录
    token = login()
    if not token:
        return
    
    # 测试列表接口
    success = test_my_registrations(token)
    
    if success:
        # 测试详情接口对比
        print('\n' + '=' * 80)
        print('📋 对比列表和详情接口返回的数据:')
        print('=' * 80)
        
        # 假设有报名ID，测试详情
        test_registration_detail(token, 164)
    
    print('\n' + '=' * 80)
    print('📝 问题诊断:')
    print('   1. 检查列表接口是否返回 institutionName 和 institutionLevel')
    print('   2. 如果没有，检查是否返回 institution 对象')
    print('   3. 如果有 institution 对象，前端需要从中提取 name 和 level')

if __name__ == '__main__':
    main()
