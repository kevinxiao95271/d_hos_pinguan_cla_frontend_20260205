#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简单的API - 不需要登录的接口
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

def test_api(url, method='GET', timeout=10, description=''):
    """测试API"""
    print(f'\n📊 测试: {description}')
    print(f'   URL: {url}')
    print(f'   方法: {method}')
    
    try:
        start_time = time.time()
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.request(method, url, timeout=timeout)
        elapsed = time.time() - start_time
        
        print(f'   ⏱️  耗时: {elapsed:.2f}秒')
        print(f'   📊 状态码: {response.status_code}')
        
        if elapsed > 5:
            print(f'   ⚠️  响应较慢（>{elapsed:.1f}秒）')
        
        return {
            'success': response.status_code < 500,
            'time': elapsed,
            'status': response.status_code
        }
    except requests.exceptions.Timeout:
        print(f'   ❌ 超时（{timeout}秒）')
        return {'success': False, 'time': timeout, 'status': 'Timeout'}
    except Exception as e:
        print(f'   ❌ 异常: {e}')
        return {'success': False, 'time': 0, 'status': 'Error'}


def main():
    print('╔' + '═' * 68 + '╗')
    print('║' + ' ' * 24 + 'API响应测试' + ' ' * 24 + '║')
    print('╚' + '═' * 68 + '╝')
    
    # 测试各种API
    tests = [
        (f'{BASE_URL}/competitions', 'GET', '赛事列表'),
        (f'{BASE_URL}/competitions/21', 'GET', '赛事详情'),
        (f'{BASE_URL}/dictionaries/method', 'GET', '字典数据'),
        (f'{BASE_URL}/institutions', 'GET', '机构列表'),
        (f'{BASE_URL}/auth/login', 'POST', '登录接口'),
    ]
    
    results = []
    for url, method, desc in tests:
        result = test_api(url, method, timeout=15, description=desc)
        results.append({'url': url, 'desc': desc, **result})
    
    # 统计
    print('\n' + '=' * 70)
    print('📊 测试结果统计')
    print('=' * 70)
    
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print(f'总测试: {len(results)} 个API')
    print(f'✅ 正常响应: {success_count} 个')
    print(f'❌ 失败/超时: {fail_count} 个')
    
    # 详细信息
    print('\n' + '=' * 70)
    print('📋 详细结果')
    print('=' * 70)
    for r in results:
        status_icon = '✅' if r['success'] else '❌'
        print(f'{status_icon} {r["desc"]:20} - 状态: {r["status"]:10} - 耗时: {r["time"]:.2f}秒')
    
    # 问题分析
    if fail_count > 0:
        print('\n' + '=' * 70)
        print('🔍 问题分析')
        print('=' * 70)
        
        timeout_count = sum(1 for r in results if r['status'] == 'Timeout')
        if timeout_count > 0:
            print(f'⚠️  有 {timeout_count} 个API超时')
            print('   可能原因:')
            print('   1. 数据库查询很慢或连接池耗尽')
            print('   2. 这些API的业务逻辑有性能问题')
            print('   3. 后端代码有死循环或阻塞')
        
        if timeout_count == len(results):
            print('\n🚨 严重问题: 所有API都超时！')
            print('   可能原因:')
            print('   1. 数据库服务未启动或无法连接')
            print('   2. 后端应用启动不完整')
            print('   3. 端口转发或网络配置问题')
    
    print('\n' + '=' * 70)
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
