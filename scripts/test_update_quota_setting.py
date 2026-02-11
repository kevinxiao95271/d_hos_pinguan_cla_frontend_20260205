#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改机构报名配额限制
POST /api/admin/settings
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

def login_as_ops():
    """以运维身份登录"""
    url = f'{BASE_URL}/auth/login'
    data = {
        'phone': '13800000005',
        'name': 'OPS User 1',
        'role': 'OPS'
    }
    
    print('🔐 登录运维账号 (OPS)...')
    response = requests.post(url, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data', {}).get('token'):
            print(f'✅ 登录成功: {data["name"]}\n')
            return result['data']['token']
    
    print('❌ 登录失败')
    return None


def login_as_committee():
    """以组委会身份登录"""
    url = f'{BASE_URL}/auth/login'
    data = {
        'phone': '13800000127',
        'name': 'CommitteeAdmin A',
        'role': 'COMMITTEE_ADMIN'
    }
    
    print('🔐 登录组委会账号...')
    response = requests.post(url, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data', {}).get('token'):
            print(f'✅ 登录成功: {data["name"]}\n')
            return result['data']['token']
    
    print('❌ 登录失败')
    return None


def get_current_setting(token):
    """查询当前配置"""
    url = f'{BASE_URL}/admin/settings'
    headers = {'Authorization': f'Bearer {token}'}
    params = {'key': 'maxRegistrationsPerInstitution'}
    
    print('📖 查询当前配置...')
    print(f'   API: {url}?key={params["key"]}\n')
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                setting = data.get('data', {})
                current_value = setting.get('settingValue')
                print(f'✅ 当前配额限制: {current_value} 个项目/机构\n')
                return current_value
            else:
                print(f'⚠️  {data.get("message")}\n')
        else:
            print(f'❌ HTTP {response.status_code}\n')
    except Exception as e:
        print(f'❌ 异常: {e}\n')
    
    return None


def test_update_setting(token, new_value, role_name):
    """测试修改配置"""
    url = f'{BASE_URL}/admin/settings'
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f'📝 测试修改配置 (角色: {role_name})')
    print(f'   API: POST {url}')
    
    data = {
        'key': 'maxRegistrationsPerInstitution',
        'value': str(new_value)
    }
    
    print(f'   请求数据: {data}\n')
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f'   Status Code: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'   响应: {json.dumps(result, ensure_ascii=False, indent=2)}')
            
            if result.get('success'):
                print(f'\n   ✅ 修改成功: 配额限制已更新为 {new_value}\n')
                return True
            else:
                print(f'\n   ⚠️  修改失败: {result.get("message")}\n')
                return False
        elif response.status_code == 403:
            print(f'   响应: {response.text[:200]}')
            print(f'\n   ❌ 权限不足: {role_name}无权修改配置\n')
            return False
        else:
            print(f'   响应: {response.text[:200]}')
            print(f'\n   ❌ HTTP错误\n')
            return False
    except Exception as e:
        print(f'   ❌ 异常: {e}\n')
        return False


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 20 + '测试修改机构报名配额限制' + ' ' * 21 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    # 测试1: OPS查询当前配置
    print('=' * 80)
    print('【测试1】OPS角色 - 查询当前配置')
    print('=' * 80 + '\n')
    
    ops_token = login_as_ops()
    if not ops_token:
        print('❌ 无法获取OPS token，终止测试')
        return 1
    
    original_value = get_current_setting(ops_token)
    if not original_value:
        print('❌ 无法获取当前配置，终止测试')
        return 1
    
    # 测试2: OPS修改配置（改为10）
    print('=' * 80)
    print('【测试2】OPS角色 - 修改配置（8 -> 10）')
    print('=' * 80 + '\n')
    
    success = test_update_setting(ops_token, 10, 'OPS')
    
    if success:
        # 验证修改是否生效
        print('🔍 验证修改是否生效...')
        new_value = get_current_setting(ops_token)
        if new_value == '10':
            print('✅ 验证通过: 配置已成功修改为 10\n')
        else:
            print(f'⚠️  验证失败: 期望10, 实际{new_value}\n')
    
    # 测试3: 组委会尝试修改（应该失败）
    print('=' * 80)
    print('【测试3】组委会角色 - 尝试修改配置（应该失败）')
    print('=' * 80 + '\n')
    
    committee_token = login_as_committee()
    if committee_token:
        committee_success = test_update_setting(committee_token, 12, 'COMMITTEE_ADMIN')
        if not committee_success:
            print('✅ 权限控制正确: 组委会无法修改配置\n')
        else:
            print('❌ 权限控制失败: 组委会不应该能修改配置\n')
    
    # 恢复原始值
    if success:
        print('=' * 80)
        print('【清理】恢复原始配置')
        print('=' * 80 + '\n')
        
        print(f'🔄 恢复配额限制: 10 -> {original_value}')
        restore_success = test_update_setting(ops_token, int(original_value), 'OPS')
        
        if restore_success:
            print('✅ 已恢复原始配置\n')
        else:
            print('⚠️  恢复失败，请手动恢复\n')
    
    # 总结
    print('=' * 80)
    print('📊 测试总结')
    print('=' * 80)
    
    print('\n✅ API测试结果:')
    print('   查询API: GET /api/admin/settings?key=maxRegistrationsPerInstitution')
    print('   修改API: POST /api/admin/settings')
    print(f'   OPS权限: {"✅ 可以修改" if success else "❌ 无法修改"}')
    print(f'   组委会权限: {"❌ 不应该能修改" if committee_token and not committee_success else "✅ 正确拒绝"}')
    
    print('\n🎯 前端开发需求:')
    print('   1. 创建OPS专用的系统配置页面')
    print('   2. 只有OPS角色可以访问')
    print('   3. 显示当前配额限制')
    print('   4. 提供输入框修改配额限制')
    print('   5. 修改后实时更新显示')
    print('   6. 添加操作日志/审计记录（建议）')
    
    print('\n📋 配置项信息:')
    print('   配置键: maxRegistrationsPerInstitution')
    print('   数据类型: 字符串（需转整数）')
    print(f'   当前值: {original_value}')
    print('   建议范围: 5-20')
    
    print('=' * 80 + '\n')
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
