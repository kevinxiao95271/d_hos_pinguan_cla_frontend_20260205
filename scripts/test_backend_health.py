#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端服务健康状态
"""

import sys
import codecs
import requests
import time

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = 'http://localhost:6031'

def test_backend_health():
    """测试后端服务是否运行"""
    print('🔍 检查后端服务状态...\n')
    
    # 测试1: 检查端口是否可访问
    print('1️⃣ 测试端口可访问性')
    print(f'   URL: {BASE_URL}')
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f'   ✅ 端口可访问 - Status: {response.status_code}')
    except requests.exceptions.ConnectionError:
        print(f'   ❌ 无法连接到 {BASE_URL}')
        print(f'   💡 可能原因: 后端服务未启动')
        return False
    except requests.exceptions.Timeout:
        print(f'   ❌ 连接超时')
        return False
    except Exception as e:
        print(f'   ❌ 错误: {e}')
        return False
    
    print()
    
    # 测试2: 检查登录API
    print('2️⃣ 测试登录API')
    login_url = f'{BASE_URL}/api/auth/login'
    print(f'   URL: {login_url}')
    
    test_data = {
        'phone': '13800000127',
        'name': 'CommitteeAdmin A',
        'role': 'COMMITTEE_ADMIN'
    }
    
    try:
        start_time = time.time()
        response = requests.post(login_url, json=test_data, timeout=30)
        elapsed = time.time() - start_time
        
        print(f'   ⏱️  响应时间: {elapsed:.2f}秒')
        print(f'   📊 状态码: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f'   ✅ 登录API正常工作')
                return True
            else:
                print(f'   ⚠️  登录失败: {data.get("message")}')
                return False
        else:
            print(f'   ❌ HTTP错误: {response.status_code}')
            return False
            
    except requests.exceptions.Timeout:
        print(f'   ❌ 登录请求超时（30秒）')
        print(f'   💡 后端可能正在处理大量请求或响应很慢')
        return False
    except requests.exceptions.ConnectionError:
        print(f'   ❌ 连接失败')
        return False
    except Exception as e:
        print(f'   ❌ 异常: {e}')
        return False


def main():
    print('╔' + '═' * 58 + '╗')
    print('║' + ' ' * 18 + '后端服务健康检查' + ' ' * 18 + '║')
    print('╚' + '═' * 58 + '╝\n')
    
    is_healthy = test_backend_health()
    
    print('\n' + '=' * 60)
    if is_healthy:
        print('✅ 后端服务正常')
    else:
        print('❌ 后端服务异常')
        print('\n💡 解决建议:')
        print('   1. 检查后端服务是否已启动')
        print('   2. 检查端口 6031 是否被占用')
        print('   3. 查看后端日志是否有错误')
        print('   4. 尝试重启后端服务')
    print('=' * 60)
    
    return 0 if is_healthy else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
