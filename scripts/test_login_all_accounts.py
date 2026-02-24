#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有快捷登录账号
"""

import sys
import codecs
import requests
import time

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = 'http://localhost:6031/api'

# 所有测试账号
TEST_ACCOUNTS = [
    # 参赛者
    {'phone': '13799999112', 'name': '王建国', 'role': 'CONTESTANT'},
    {'phone': '13966000890', 'name': '参赛者1', 'role': 'CONTESTANT'},
    {'phone': '13965999231', 'name': '参赛者2', 'role': 'CONTESTANT'},
    
    # 评委
    {'phone': '13800002569', 'name': '孙丽娟', 'role': 'REVIEWER'},
    {'phone': '13900000001', 'name': '王建国', 'role': 'REVIEWER'},
    
    # 组委会
    {'phone': '13800000127', 'name': 'CommitteeAdmin A', 'role': 'COMMITTEE_ADMIN'},
    {'phone': '13799999971', 'name': 'CommitteeAdmin B', 'role': 'COMMITTEE_ADMIN'},
    
    # 运维
    {'phone': '13800000005', 'name': 'OPS User 1', 'role': 'OPS'},
    {'phone': '13800000027', 'name': 'OPS User 2', 'role': 'OPS'},
]

def test_login(account, timeout=10):
    """测试单个账号登录"""
    url = f'{BASE_URL}/auth/login'
    
    try:
        start_time = time.time()
        response = requests.post(url, json=account, timeout=timeout)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return {
                    'success': True,
                    'time': elapsed,
                    'message': 'OK'
                }
            else:
                return {
                    'success': False,
                    'time': elapsed,
                    'message': data.get('message', 'Unknown error')
                }
        else:
            return {
                'success': False,
                'time': elapsed,
                'message': f'HTTP {response.status_code}'
            }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'time': timeout,
            'message': f'超时（{timeout}秒）'
        }
    except Exception as e:
        return {
            'success': False,
            'time': 0,
            'message': str(e)
        }


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 26 + '登录测试报告' + ' ' * 26 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    results = []
    success_count = 0
    fail_count = 0
    
    for i, account in enumerate(TEST_ACCOUNTS, 1):
        print(f'{i}. 测试账号: {account["name"]} ({account["role"]})')
        print(f'   手机号: {account["phone"]}')
        
        result = test_login(account, timeout=15)
        results.append({
            'account': account,
            'result': result
        })
        
        if result['success']:
            print(f'   ✅ 登录成功 - 耗时: {result["time"]:.2f}秒')
            success_count += 1
        else:
            print(f'   ❌ 登录失败 - {result["message"]}')
            if result['time'] > 0:
                print(f'      耗时: {result["time"]:.2f}秒')
            fail_count += 1
        
        print()
        time.sleep(0.5)  # 避免请求太快
    
    # 统计报告
    print('=' * 80)
    print('📊 测试统计')
    print('=' * 80)
    print(f'总测试账号: {len(TEST_ACCOUNTS)} 个')
    print(f'✅ 成功: {success_count} 个')
    print(f'❌ 失败: {fail_count} 个')
    print(f'成功率: {success_count / len(TEST_ACCOUNTS) * 100:.1f}%')
    
    # 失败详情
    if fail_count > 0:
        print('\n' + '=' * 80)
        print('❌ 失败账号详情')
        print('=' * 80)
        for item in results:
            if not item['result']['success']:
                acc = item['account']
                res = item['result']
                print(f'- {acc["name"]} ({acc["phone"]})')
                print(f'  角色: {acc["role"]}')
                print(f'  原因: {res["message"]}')
                print()
    
    # 慢响应提醒
    slow_accounts = [item for item in results if item['result']['success'] and item['result']['time'] > 5]
    if slow_accounts:
        print('=' * 80)
        print('⚠️  慢响应账号（>5秒）')
        print('=' * 80)
        for item in slow_accounts:
            acc = item['account']
            res = item['result']
            print(f'- {acc["name"]}: {res["time"]:.2f}秒')
        print()
    
    print('=' * 80)
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
