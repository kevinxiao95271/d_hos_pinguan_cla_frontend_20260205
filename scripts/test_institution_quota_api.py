#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试机构报名配额API
GET /api/registrations/institution-quota
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
        'phone': '13966000890',
        'name': '参赛者1',
        'role': 'CONTESTANT'
    }
    
    print('🔐 登录参赛者账号...')
    response = requests.post(url, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data', {}).get('token'):
            token = result['data']['token']
            user_info = result['data']
            print(f'✅ 登录成功: {data["name"]}')
            print(f'   机构ID: {user_info.get("institutionId")}')
            print(f'   机构名: {user_info.get("institutionName")}\n')
            return token, user_info
    
    print('❌ 登录失败')
    return None, None


def test_quota_api(token, institution_id):
    """测试机构配额API"""
    url = f'{BASE_URL}/registrations/institution-quota'
    headers = {'Authorization': f'Bearer {token}'}
    
    print('=' * 80)
    print('📊 测试机构报名配额API')
    print('=' * 80)
    print(f'API端点: {url}')
    print(f'Method: GET\n')
    
    # 测试1: 查询当前机构的配额（竞赛21）
    print('【测试1】查询当前机构配额（竞赛21）')
    print('-' * 80)
    params = {
        'competitionId': 21,
        'institutionId': institution_id
    }
    print(f'请求参数: {params}\n')
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f'Status Code: {response.status_code}\n')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API调用成功\n')
            print('📦 响应数据:')
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            if data.get('success'):
                quota_info = data.get('data', {})
                
                print('\n' + '=' * 80)
                print('📋 配额信息详情:')
                print('=' * 80)
                
                # 检查必需字段
                required_fields = [
                    'institutionId',
                    'institutionName', 
                    'competitionId',
                    'competitionName',
                    'currentCount',
                    'maxCount',
                    'remainingCount',
                    'canRegister'
                ]
                
                print('\n🔍 字段完整性检查:')
                missing_fields = []
                for field in required_fields:
                    if field in quota_info:
                        value = quota_info[field]
                        value_type = type(value).__name__
                        print(f'   ✅ {field}: {value_type} = {value}')
                    else:
                        print(f'   ❌ {field}: 缺失')
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f'\n   🚨 警告: 缺少字段 {missing_fields}')
                    return False
                
                # 验证业务逻辑
                print('\n' + '=' * 80)
                print('🧮 业务逻辑验证:')
                print('=' * 80)
                
                current = quota_info.get('currentCount', 0)
                max_count = quota_info.get('maxCount', 0)
                remaining = quota_info.get('remainingCount', 0)
                can_register = quota_info.get('canRegister', False)
                
                # 验证1: remaining = max - current
                expected_remaining = max_count - current
                if remaining == expected_remaining:
                    print(f'   ✅ 剩余数量计算正确: {max_count} - {current} = {remaining}')
                else:
                    print(f'   ❌ 剩余数量计算错误: 期望 {expected_remaining}, 实际 {remaining}')
                
                # 验证2: canRegister 逻辑
                expected_can_register = remaining > 0
                if can_register == expected_can_register:
                    print(f'   ✅ 可报名状态正确: {can_register}')
                else:
                    print(f'   ❌ 可报名状态错误: 期望 {expected_can_register}, 实际 {can_register}')
                
                # 显示配额使用情况
                print('\n' + '=' * 80)
                print('📈 配额使用情况:')
                print('=' * 80)
                usage_percent = (current / max_count * 100) if max_count > 0 else 0
                print(f'   已使用: {current}/{max_count} ({usage_percent:.1f}%)')
                print(f'   剩余: {remaining} 个名额')
                print(f'   状态: {"✅ 可报名" if can_register else "❌ 已满额"}')
                
                if current >= max_count:
                    print('\n   ⚠️  注意: 该机构已达到报名上限！')
                elif remaining <= 2:
                    print(f'\n   ⚠️  注意: 剩余名额不足（仅剩 {remaining} 个）')
                
                return True
            else:
                print(f'⚠️  业务失败: {data.get("message")}')
                return False
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            print(f'   响应: {response.text[:500]}')
            return False
    except Exception as e:
        print(f'❌ 异常: {e}')
        return False


def test_quota_without_params(token):
    """测试不带参数的情况"""
    url = f'{BASE_URL}/registrations/institution-quota'
    headers = {'Authorization': f'Bearer {token}'}
    
    print('\n\n【测试2】不带参数查询（应该从token获取）')
    print('-' * 80)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f'Status Code: {response.status_code}\n')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print('✅ 不带参数也能查询（从token自动获取）')
                quota_info = data.get('data', {})
                print(f'   机构: {quota_info.get("institutionName")}')
                print(f'   配额: {quota_info.get("currentCount")}/{quota_info.get("maxCount")}')
            else:
                print(f'⚠️  {data.get("message")}')
        else:
            print(f'❌ HTTP {response.status_code}')
            if response.status_code == 400:
                print('   说明: 必须提供参数')
    except Exception as e:
        print(f'❌ 异常: {e}')


def test_admin_settings_api(admin_token):
    """测试运维配置API"""
    print('\n\n' + '=' * 80)
    print('⚙️  测试运维配置API（查询配额限制）')
    print('=' * 80)
    
    url = f'{BASE_URL}/admin/settings'
    headers = {'Authorization': f'Bearer {admin_token}'}
    params = {'key': 'maxRegistrationsPerInstitution'}
    
    print(f'API端点: {url}')
    print(f'参数: {params}\n')
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f'Status Code: {response.status_code}\n')
        
        if response.status_code == 200:
            data = response.json()
            print('响应数据:')
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            if data.get('success'):
                setting = data.get('data', {})
                print(f'\n✅ 当前配额限制: {setting.get("value")} 个项目/机构')
            else:
                print(f'\n⚠️  {data.get("message")}')
        else:
            print(f'❌ HTTP {response.status_code}')
            if response.status_code == 403:
                print('   说明: 需要OPS权限')
    except Exception as e:
        print(f'❌ 异常: {e}')


def login_as_ops():
    """以运维身份登录"""
    url = f'{BASE_URL}/auth/login'
    data = {
        'phone': '13800000005',
        'name': 'OPS User 1',
        'role': 'OPS'
    }
    
    print('\n🔐 登录运维账号...')
    response = requests.post(url, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data', {}).get('token'):
            print(f'✅ 登录成功: {data["name"]}\n')
            return result['data']['token']
    
    print('❌ 登录失败')
    return None


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 23 + '机构报名配额API探测' + ' ' * 24 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    # 测试1: 参赛者查询配额
    token, user_info = login_as_contestant()
    if not token:
        print('❌ 无法获取token，终止测试')
        return 1
    
    institution_id = user_info.get('institutionId')
    if not institution_id:
        print('❌ 无法获取机构ID，终止测试')
        return 1
    
    success = test_quota_api(token, institution_id)
    
    # 测试2: 不带参数查询
    test_quota_without_params(token)
    
    # 测试3: 运维查询配置
    ops_token = login_as_ops()
    if ops_token:
        test_admin_settings_api(ops_token)
    
    # 总结
    print('\n' + '=' * 80)
    print('📊 测试总结')
    print('=' * 80)
    
    if success:
        print('✅ 机构报名配额API测试通过')
        print('\n📝 API信息:')
        print('   端点: GET /api/registrations/institution-quota')
        print('   参数: competitionId, institutionId')
        print('   返回: 配额信息（8个字段）')
        print('\n🎯 前端开发建议:')
        print('   1. 在报名页面显示配额提示')
        print('   2. 剩余名额<=2时显示警告')
        print('   3. 已满额时禁用"创建报名"按钮')
        print('   4. 实时刷新配额状态')
    else:
        print('❌ 测试失败，请检查后端API')
    
    print('=' * 80 + '\n')
    
    return 0 if success else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
