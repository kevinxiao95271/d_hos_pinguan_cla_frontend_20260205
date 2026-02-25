# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json
import time
import random

BASE_URL = 'http://localhost:6031/api'

def test_register():
    """测试注册API"""
    url = f'{BASE_URL}/auth/register'
    
    # 生成随机手机号（避免重复）
    phone = f'138{random.randint(10000000, 99999999)}'
    
    data = {
        'phone': phone,
        'password': 'test123456',
        'confirmPassword': 'test123456',
        'name': '测试用户',
        'title': '主任医师',
        'role': 'CONTESTANT',
        'institutionId': 123  # 使用测试发现的机构ID
    }
    
    print(f'\n{"="*80}')
    print(f'📝 测试1: 参赛者注册')
    print(f'{"="*80}')
    print(f'URL: {url}')
    print(f'请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}')
    
    try:
        start = time.time()
        response = requests.post(url, json=data, timeout=30)
        elapsed = time.time() - start
        
        print(f'\n⏱️  响应时间: {elapsed:.3f}秒')
        print(f'📊 状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f'✅ 注册成功!')
                print(f'📦 返回字段: {list(result.get("data", {}).keys())}')
                
                token = result['data'].get('token')
                if token:
                    print(f'🔑 Token: {token[:50]}...')
                    return token, phone
                else:
                    print(f'⚠️  未返回Token')
            else:
                print(f'⚠️  注册失败: {result.get("message")}')
        else:
            print(f'❌ HTTP错误')
            print(f'错误信息: {response.text[:500]}')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    return None, None


def test_login_with_password(phone, password):
    """测试密码登录API"""
    url = f'{BASE_URL}/auth/login-with-password'
    
    data = {
        'phone': phone,
        'password': password
    }
    
    print(f'\n{"="*80}')
    print(f'🔐 测试2: 密码登录（使用刚注册的账号）')
    print(f'{"="*80}')
    print(f'URL: {url}')
    print(f'请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}')
    
    try:
        start = time.time()
        response = requests.post(url, json=data, timeout=30)
        elapsed = time.time() - start
        
        print(f'\n⏱️  响应时间: {elapsed:.3f}秒')
        print(f'📊 状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f'✅ 登录成功!')
                print(f'📦 返回字段: {list(result.get("data", {}).keys())}')
                
                # 显示用户信息
                user = result['data']
                print(f'\n👤 用户信息:')
                print(f'   - ID: {user.get("id")}')
                print(f'   - 姓名: {user.get("name")}')
                print(f'   - 角色: {user.get("role")}')
                print(f'   - 机构ID: {user.get("institutionId")}')
                print(f'   - 机构名称: {user.get("institutionName")}')
                
                token = user.get('token')
                if token:
                    print(f'🔑 Token: {token[:50]}...')
                    return token
                else:
                    print(f'⚠️  未返回Token')
            else:
                print(f'⚠️  登录失败: {result.get("message")}')
        else:
            print(f'❌ HTTP错误')
            print(f'错误信息: {response.text[:500]}')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    return None


def test_user_query(token):
    """测试用户查询API（需要Token）"""
    url = f'{BASE_URL}/admin/users/query'
    
    data = {
        'page': 0,
        'size': 10
    }
    
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f'\n{"="*80}')
    print(f'📋 测试3: 用户查询（测试Token是否有效）')
    print(f'{"="*80}')
    print(f'URL: {url}')
    print(f'请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}')
    print(f'Token: {token[:30]}...')
    
    try:
        start = time.time()
        response = requests.post(url, json=data, headers=headers, timeout=30)
        elapsed = time.time() - start
        
        print(f'\n⏱️  响应时间: {elapsed:.3f}秒')
        print(f'📊 状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f'✅ 查询成功!')
                page_data = result.get('data', {})
                print(f'📦 总用户数: {page_data.get("totalElements", 0)}')
                print(f'📦 当前页用户数: {len(page_data.get("content", []))}')
            else:
                print(f'⚠️  查询失败: {result.get("message")}')
        elif response.status_code == 403:
            print(f'⚠️  权限不足（403）- 参赛者账号无权访问管理接口')
        else:
            print(f'❌ HTTP错误')
            print(f'错误信息: {response.text[:500]}')
    except Exception as e:
        print(f'❌ 异常: {e}')


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 25 + '新认证API测试（注册+登录）' + ' ' * 25 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    print('🎯 测试目标:')
    print('   1. 测试参赛者注册API（POST /api/auth/register）')
    print('   2. 测试密码登录API（POST /api/auth/login-with-password）')
    print('   3. 测试Token是否有效（访问需要认证的接口）')
    print('   4. 验证完整的注册-登录流程')
    
    # 测试1: 注册
    token, phone = test_register()
    
    if not token or not phone:
        print('\n❌ 注册失败，无法继续测试')
        return 1
    
    # 等待一下
    time.sleep(1)
    
    # 测试2: 使用刚注册的账号登录
    login_token = test_login_with_password(phone, 'test123456')
    
    if not login_token:
        print('\n⚠️  登录失败，但注册成功了')
    
    # 测试3: 使用Token访问需要认证的接口
    if login_token:
        test_user_query(login_token)
    
    print('\n' + '='*80)
    print('✅ 测试完成')
    print('='*80)
    print('\n📝 结论:')
    print('   1. 注册API是否工作正常')
    print('   2. 登录API是否工作正常')
    print('   3. Token是否有效')
    print('   4. 完整流程是否通畅')
    print()
    
    return 0


if __name__ == '__main__':
    exit(main())
