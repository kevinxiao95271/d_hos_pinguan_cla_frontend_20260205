# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json
import random

BASE_URL = 'http://localhost:6031/api'

print('='*80)
print('验证报名是否包含机构信息')
print('='*80)

# 注册用户
phone = f'138{random.randint(10000000, 99999999)}'
institution_id = 57548

print('\n步骤1: 注册用户')
try:
    response = requests.post(
        f'{BASE_URL}/auth/register',
        json={
            'phone': phone,
            'password': 'Test1234',
            'confirmPassword': 'Test1234',
            'name': 'Test User',
            'title': 'Doctor',
            'role': 'CONTESTANT',
            'institutionId': institution_id
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            token = result['data']['token']
            user_institution_id = result['data']['institutionId']
            print(f'✅ 注册成功，用户机构ID: {user_institution_id}')
        else:
            print('❌ 注册失败')
            sys.exit(1)
    else:
        print('❌ 请求失败')
        sys.exit(1)
except Exception as e:
    print(f'❌ 异常: {e}')
    sys.exit(1)

# 创建报名（不传institutionId）
print('\n步骤2: 创建报名（不传institutionId）')
try:
    response = requests.post(
        f'{BASE_URL}/registrations',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'competitionId': 1,
            'projectName': f'验证测试-{random.randint(1000, 9999)}',
            'groupType': 'BASIC'
        },
        timeout=10
    )
    
    print(f'响应状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            registration_id = result['data']['id']
            print(f'✅ 创建成功，报名ID: {registration_id}')
            print(f'创建响应: {json.dumps(result["data"], indent=2, ensure_ascii=False)}')
        else:
            print(f'❌ 创建失败: {result.get("message")}')
            sys.exit(1)
    else:
        print('❌ 请求失败')
        sys.exit(1)
except Exception as e:
    print(f'❌ 异常: {e}')
    sys.exit(1)

# 获取报名详情
print('\n步骤3: 获取报名详情（查看是否有institutionId）')
try:
    response = requests.get(
        f'{BASE_URL}/registrations/{registration_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=10
    )
    
    print(f'响应状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            registration = result['data']
            print(f'✅ 获取成功')
            print(f'详情响应: {json.dumps(registration, indent=2, ensure_ascii=False)}')
            
            # 检查关键字段
            print(f'\n📊 关键字段验证:')
            print(f'   报名ID: {registration.get("id")}')
            print(f'   项目名称: {registration.get("projectName")}')
            print(f'   报名机构ID: {registration.get("institutionId")}')
            print(f'   报名机构名称: {registration.get("institutionName")}')
            print(f'   用户机构ID: {user_institution_id}')
            
            if registration.get('institutionId') == user_institution_id:
                print(f'\n   ✅✅✅ 验证通过: 后端自动使用了用户的机构ID!')
            elif registration.get('institutionId') is None:
                print(f'\n   ❌ institutionId字段为空，后端可能未设置')
            else:
                print(f'\n   ❌ institutionId不匹配')
        else:
            print(f'❌ 获取失败: {result.get("message")}')
    else:
        print(f'❌ 请求失败: {response.text}')
except Exception as e:
    print(f'❌ 异常: {e}')

print('\n' + '='*80)
print('测试完成')
print('='*80)
