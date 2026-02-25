# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json
import time

BASE_URL = 'http://localhost:6031/api'

def test_login(account_info):
    """测试登录"""
    url = f'{BASE_URL}/auth/login'
    
    # 构造登录数据（按前端格式）
    data = {
        'phone': account_info['phone'],
        'name': account_info['name'],
        'title': 'Test Title',
        'role': account_info['role'],
        'institutionId': account_info.get('institutionId')
    }
    
    # 如果是评委，添加评委相关字段（尽管后端说要删除，但前端还在用）
    if account_info['role'] == 'REVIEWER':
        data['reviewerGroupCode'] = 'A1'
        data['interviewGroupCode'] = 'A1'
        data['expertBackground'] = 'MEDICAL'
    
    print(f'\n{"="*80}')
    print(f'📱 测试账号: {account_info["label"]}')
    print(f'{"="*80}')
    print(f'请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}')
    
    try:
        start = time.time()
        response = requests.post(url, json=data, timeout=60)
        elapsed = time.time() - start
        
        print(f'\n⏱️  响应时间: {elapsed:.2f}秒')
        print(f'📊 状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'✅ 登录成功!')
            if result.get('success') and result.get('data', {}).get('token'):
                token = result['data']['token']
                print(f'🔑 Token: {token[:50]}...')
                print(f'📦 返回数据字段: {list(result.get("data", {}).keys())}')
                return token
            else:
                print(f'⚠️  响应格式异常: {json.dumps(result, indent=2, ensure_ascii=False)}')
        else:
            print(f'❌ 登录失败')
            print(f'错误信息: {response.text[:500]}')
    except requests.exceptions.Timeout:
        print(f'❌ 登录超时（60秒）')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    return None


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 28 + '登录API测试' + ' ' * 28 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    print('🎯 测试目标: 找到一个能够登录成功的账号')
    
    # 测试多个账号
    test_accounts = [
        # OPS账号
        { 'phone': '13800000005', 'name': 'OPS User 1', 'label': '运维1', 'role': 'OPS', 'institutionId': None },
        { 'phone': '13800000027', 'name': 'OPS User 2', 'label': '运维2', 'role': 'OPS', 'institutionId': None },
        
        # 组委会管理员
        { 'phone': '13800000127', 'name': 'CommitteeAdmin A', 'label': '组委会A', 'role': 'COMMITTEE_ADMIN', 'institutionId': None },
        
        # 参赛者
        { 'phone': '13799999112', 'name': '王建国', 'label': '参赛-王建国', 'role': 'CONTESTANT', 'institutionId': None },
        
        # 评委
        { 'phone': '13800002569', 'name': '孙丽娟', 'label': '评委-孙丽娟', 'role': 'REVIEWER', 'institutionId': None }
    ]
    
    successful_token = None
    
    for account in test_accounts:
        token = test_login(account)
        if token:
            successful_token = token
            print(f'\n✅✅✅ 找到可用账号: {account["label"]} ✅✅✅\n')
            break
    
    if not successful_token:
        print('\n' + '='*80)
        print('❌ 所有测试账号均登录失败')
        print('💡 可能原因:')
        print('   1. 后端登录API有bug')
        print('   2. 登录参数格式已变更（需查看swagger）')
        print('   3. 后端数据库未初始化测试账号')
        print('='*80)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
