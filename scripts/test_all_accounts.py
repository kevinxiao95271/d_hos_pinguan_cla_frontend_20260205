#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端登录测试 - PostgreSQL数据库
测试所有角色账号的登录功能
"""

import sys
import codecs
import requests
import json
from typing import List, Dict

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# API基础URL
BASE_URL = 'http://localhost:6031/api'

# 测试账号列表（PostgreSQL数据）
TEST_ACCOUNTS = {
    '参赛者': [
        {'phone': '13799999112', 'name': '王建国', 'role': 'CONTESTANT'},
        {'phone': '13966000890', 'name': '参赛者1', 'role': 'CONTESTANT'},
        {'phone': '13965999231', 'name': '参赛者2', 'role': 'CONTESTANT'},
        {'phone': '13966000430', 'name': '参赛者3', 'role': 'CONTESTANT'},
        {'phone': '13965999424', 'name': '参赛者4', 'role': 'CONTESTANT'},
    ],
    '评委': [
        {'phone': '13800002569', 'name': '孙丽娟', 'role': 'REVIEWER'},
        {'phone': '13900000001', 'name': '王建国', 'role': 'REVIEWER'},
        {'phone': '13800000084', 'name': '李明华', 'role': 'REVIEWER'},
    ],
    '组委会管理员': [
        {'phone': '13800000127', 'name': 'CommitteeAdmin A', 'role': 'COMMITTEE_ADMIN'},
        {'phone': '13799999971', 'name': 'CommitteeAdmin B', 'role': 'COMMITTEE_ADMIN'},
    ],
    '系统维护员': [
        {'phone': '13800000005', 'name': 'OPS User 1', 'role': 'OPS'},
        {'phone': '13800000027', 'name': 'OPS User 2', 'role': 'OPS'},
    ]
}


def test_login(account: Dict) -> Dict:
    """
    测试账号登录
    """
    url = f'{BASE_URL}/auth/login'
    
    # 构建登录请求数据
    login_data = {
        'phone': account['phone'],
        'name': account['name'],
        'role': account['role']
    }
    
    # 评委角色需要额外字段
    if account['role'] == 'REVIEWER':
        login_data['reviewerGroupCode'] = 'A1'
        login_data['interviewGroupCode'] = 'A1'
        login_data['expertBackground'] = 'MEDICAL'
    
    try:
        response = requests.post(url, json=login_data, timeout=10)
        
        result = {
            'account': account,
            'status_code': response.status_code,
            'success': False,
            'token': None,
            'error': None
        }
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data', {}).get('token'):
                result['success'] = True
                result['token'] = data['data']['token'][:20] + '...'  # 只显示前20个字符
                result['user_info'] = {
                    'id': data['data'].get('id'),
                    'name': data['data'].get('name'),
                    'role': data['data'].get('role')
                }
            else:
                result['error'] = data.get('message', '登录失败')
        else:
            try:
                error_data = response.json()
                result['error'] = error_data.get('message', f'HTTP {response.status_code}')
            except:
                result['error'] = f'HTTP {response.status_code}'
        
        return result
        
    except requests.exceptions.ConnectionError:
        return {
            'account': account,
            'status_code': 0,
            'success': False,
            'token': None,
            'error': '连接失败：后端服务未启动 (localhost:6031)'
        }
    except Exception as e:
        return {
            'account': account,
            'status_code': 0,
            'success': False,
            'token': None,
            'error': f'异常: {str(e)}'
        }


def print_section_header(title: str):
    """打印分组标题"""
    print('\n' + '=' * 80)
    print(f'  {title}')
    print('=' * 80)


def print_test_result(result: Dict, index: int):
    """打印测试结果"""
    account = result['account']
    status = '✅ 成功' if result['success'] else '❌ 失败'
    
    print(f"\n[{index}] {status}")
    print(f"    姓名: {account['name']}")
    print(f"    手机: {account['phone']}")
    print(f"    角色: {account['role']}")
    
    if result['success']:
        print(f"    Token: {result['token']}")
        if result.get('user_info'):
            user_info = result['user_info']
            print(f"    用户ID: {user_info.get('id')}")
    else:
        print(f"    错误: {result['error']}")


def main():
    """主函数"""
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 20 + '品管大赛 - 端到端登录测试（PostgreSQL）' + ' ' * 19 + '║')
    print('╚' + '═' * 78 + '╝')
    print(f'\n📡 后端API: {BASE_URL}')
    print(f'📊 测试账号总数: {sum(len(accounts) for accounts in TEST_ACCOUNTS.values())}')
    
    all_results = {}
    total_success = 0
    total_failed = 0
    
    # 按角色分组测试
    for role_name, accounts in TEST_ACCOUNTS.items():
        print_section_header(f'{role_name} ({len(accounts)}个)')
        
        role_results = []
        for i, account in enumerate(accounts, 1):
            result = test_login(account)
            role_results.append(result)
            print_test_result(result, i)
            
            if result['success']:
                total_success += 1
            else:
                total_failed += 1
        
        all_results[role_name] = role_results
    
    # 打印汇总
    print('\n' + '=' * 80)
    print('  测试汇总')
    print('=' * 80)
    
    for role_name, results in all_results.items():
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        status_icon = '✅' if success_count == total_count else '⚠️'
        print(f'{status_icon} {role_name}: {success_count}/{total_count} 成功')
    
    print('\n' + '-' * 80)
    total_count = total_success + total_failed
    success_rate = (total_success / total_count * 100) if total_count > 0 else 0
    
    print(f'总计: {total_success}/{total_count} 成功 ({success_rate:.1f}%)')
    
    if total_failed > 0:
        print(f'\n⚠️  {total_failed} 个账号登录失败，请检查：')
        print('   1. 后端服务是否在 localhost:6031 运行')
        print('   2. PostgreSQL数据库是否已初始化测试数据')
        print('   3. 账号信息是否正确')
    else:
        print('\n🎉 所有账号登录测试通过！')
    
    print('=' * 80 + '\n')
    
    # 返回退出码
    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
