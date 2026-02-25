# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json
import random

BASE_URL = 'http://localhost:6031/api'

print('╔' + '═' * 78 + '╗')
print('║' + ' ' * 25 + '字典API测试报告' + ' ' * 27 + '║')
print('╚' + '═' * 78 + '╝\n')

print('🎯 测试目标: 验证报名表单中的四个下拉框数据API')
print('   1. 主题类型 - subject_type')
print('   2. 运用手法 - method')
print('   3. 改善就医感受 - experience_improve')
print('   4. 医疗质量安全主题 - quality_topic')
print()

# 先获取token
print('='*80)
print('🔐 准备工作: 获取token')
print('='*80)

phone = f'138{random.randint(10000000, 99999999)}'
try:
    response = requests.post(
        f'{BASE_URL}/auth/register',
        json={
            'phone': phone,
            'password': 'Test1234',
            'confirmPassword': 'Test1234',
            'name': 'Test User',
            'title': 'Test',
            'role': 'CONTESTANT',
            'institutionId': 57548
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            token = result['data']['token']
            print(f'✅ 获取token成功')
        else:
            print('❌ 注册失败，尝试不带token测试')
            token = None
    else:
        print('❌ 请求失败，尝试不带token测试')
        token = None
except Exception as e:
    print(f'⚠️  异常: {e}，尝试不带token测试')
    token = None

# 测试四个字典API
dictionary_types = [
    ('subject_type', '主题类型'),
    ('method', '运用手法'),
    ('experience_improve', '改善就医感受'),
    ('quality_topic', '医疗质量安全主题')
]

results = {}

for dict_type, display_name in dictionary_types:
    print('\n' + '='*80)
    print(f'📊 测试: {display_name} ({dict_type})')
    print('='*80)
    
    url = f'{BASE_URL}/dictionaries/{dict_type}'
    print(f'URL: {url}')
    
    # 测试1: 不带token
    print(f'\n测试1: 不带token')
    try:
        response = requests.get(url, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应类型: {response.headers.get("Content-Type")}')
        
        if response.status_code == 200:
            result = response.json()
            
            # 判断响应格式
            if isinstance(result, list):
                # 直接返回列表
                print(f'✅ 成功! 返回 {len(result)} 条数据（直接列表）')
                
                if result:
                    print(f'\n前3条数据:')
                    for i, item in enumerate(result[:3], 1):
                        print(f'   {i}. code: {item.get("code")}, label: {item.get("label")}')
                
                results[dict_type] = {
                    'status': 'success',
                    'count': len(result),
                    'needsAuth': False
                }
            elif isinstance(result, dict) and result.get('success'):
                # 标准格式 {success: true, data: [...]}
                data = result.get('data', [])
                print(f'✅ 成功! 返回 {len(data)} 条数据（标准格式）')
                
                if data:
                    print(f'\n前3条数据:')
                    for i, item in enumerate(data[:3], 1):
                        print(f'   {i}. code: {item.get("code")}, label: {item.get("label")}')
                
                results[dict_type] = {
                    'status': 'success',
                    'count': len(data),
                    'needsAuth': False
                }
            else:
                print(f'❌ 未知响应格式: {str(result)[:100]}')
                results[dict_type] = {'status': 'failed', 'message': '未知响应格式'}
        elif response.status_code == 401:
            print(f'⚠️  需要认证，尝试带token')
            
            # 测试2: 带token
            if token:
                print(f'\n测试2: 带token')
                response = requests.get(
                    url, 
                    headers={'Authorization': f'Bearer {token}'},
                    timeout=10
                )
                print(f'状态码: {response.status_code}')
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        data = result.get('data', [])
                        print(f'✅ 成功! 返回 {len(data)} 条数据')
                        
                        if data:
                            print(f'\n前3条数据:')
                            for i, item in enumerate(data[:3], 1):
                                print(f'   {i}. code: {item.get("code")}, label: {item.get("label")}')
                        
                        results[dict_type] = {
                            'status': 'success',
                            'count': len(data),
                            'needsAuth': True
                        }
                    else:
                        print(f'❌ 失败: {result.get("message")}')
                        results[dict_type] = {'status': 'failed', 'message': result.get("message")}
                else:
                    print(f'❌ 仍然失败: {response.text[:200]}')
                    results[dict_type] = {'status': 'failed', 'statusCode': response.status_code}
            else:
                results[dict_type] = {'status': 'failed', 'message': '需要token但无法获取'}
        else:
            print(f'❌ 失败: {response.text[:200]}')
            results[dict_type] = {'status': 'failed', 'statusCode': response.status_code}
    except Exception as e:
        print(f'❌ 异常: {e}')
        results[dict_type] = {'status': 'error', 'error': str(e)}

# 总结
print('\n' + '='*80)
print('📊 测试总结')
print('='*80)

print('\n字典API测试结果:')
print()
print('| 字典类型 | 中文名称 | 状态 | 数据量 | 需要认证 |')
print('|----------|----------|------|--------|----------|')

for dict_type, display_name in dictionary_types:
    result = results.get(dict_type, {})
    status = result.get('status', 'unknown')
    count = result.get('count', '-')
    needs_auth = '是' if result.get('needsAuth') else '否'
    
    status_emoji = '✅' if status == 'success' else '❌'
    print(f'| {dict_type} | {display_name} | {status_emoji} {status} | {count} | {needs_auth} |')

print()
print('📝 结论:')
all_success = all(r.get('status') == 'success' for r in results.values())
if all_success:
    print('   ✅ 所有字典API都正常工作')
    print('   ✅ 前端可以正常加载下拉框数据')
else:
    print('   ❌ 部分字典API有问题，需要检查后端')
    failed = [k for k, v in results.items() if v.get('status') != 'success']
    print(f'   ❌ 失败的字典: {", ".join(failed)}')
print()
