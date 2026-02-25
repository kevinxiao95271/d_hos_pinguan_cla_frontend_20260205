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
print('测试报名详情API和更新功能')
print('='*80)

# 1. 注册用户并获取token
phone = f'138{random.randint(10000000, 99999999)}'
print(f'\n步骤1: 注册用户 ({phone})')
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
            'institutionId': 57548
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            token = result['data']['token']
            print(f'✅ 注册成功，获得token')
        else:
            print('❌ 注册失败')
            sys.exit(1)
    else:
        print('❌ 请求失败')
        sys.exit(1)
except Exception as e:
    print(f'❌ 异常: {e}')
    sys.exit(1)

# 2. 创建报名（只填基本信息）
print(f'\n步骤2: 创建报名（只填赛事）')
try:
    response = requests.post(
        f'{BASE_URL}/registrations',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'competitionId': 1,
            'projectName': f'测试项目-{random.randint(1000, 9999)}',
            'groupType': 'BASIC'
        },
        timeout=10
    )
    
    print(f'状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            registration_id = result['data']['id']
            print(f'✅ 创建成功，报名ID: {registration_id}')
            print(f'响应: {json.dumps(result["data"], indent=2, ensure_ascii=False)}')
        else:
            print(f'❌ 创建失败: {result.get("message")}')
            sys.exit(1)
    else:
        print('❌ 请求失败')
        sys.exit(1)
except Exception as e:
    print(f'❌ 异常: {e}')
    sys.exit(1)

# 3. 获取报名详情
print(f'\n步骤3: 获取报名详情 (ID: {registration_id})')
try:
    response = requests.get(
        f'{BASE_URL}/registrations/{registration_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=10
    )
    
    print(f'状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f'✅ 获取成功')
            print(f'详情: {json.dumps(result["data"], indent=2, ensure_ascii=False)}')
            
            # 检查关键字段
            registration = result['data'].get('registration') or result['data']
            print(f'\n关键字段验证:')
            print(f'  competitionId: {registration.get("competitionId")}')
            print(f'  projectName: {registration.get("projectName")}')
            print(f'  groupType: {registration.get("groupType")}')
        else:
            print(f'❌ 获取失败: {result.get("message")}')
    else:
        print('❌ 请求失败')
except Exception as e:
    print(f'❌ 异常: {e}')

# 4. 更新报名（模拟"下一步"后再编辑的场景）
print(f'\n步骤4: 更新报名基本信息')
try:
    response = requests.put(
        f'{BASE_URL}/registrations/{registration_id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'competitionId': 1,
            'projectName': f'修改后的项目名-{random.randint(1000, 9999)}',
            'groupType': 'COMPREHENSIVE'  # 改成综合组
        },
        timeout=10
    )
    
    print(f'状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f'✅ 更新成功')
            print(f'响应: {json.dumps(result.get("data"), indent=2, ensure_ascii=False)}')
        else:
            print(f'❌ 更新失败: {result.get("message")}')
    else:
        print(f'❌ 请求失败: {response.text[:200]}')
except Exception as e:
    print(f'❌ 异常: {e}')

# 5. 再次获取报名详情，验证更新是否生效
print(f'\n步骤5: 再次获取报名详情（验证更新）')
try:
    response = requests.get(
        f'{BASE_URL}/registrations/{registration_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            registration = result['data'].get('registration') or result['data']
            print(f'✅ 获取成功')
            print(f'  组别: {registration.get("groupType")} (应该是 COMPREHENSIVE)')
            
            if registration.get('groupType') == 'COMPREHENSIVE':
                print(f'\n  ✅✅✅ 更新成功！数据已保存！')
            else:
                print(f'\n  ❌ 更新失败，数据未保存')
        else:
            print(f'❌ 获取失败')
    else:
        print('❌ 请求失败')
except Exception as e:
    print(f'❌ 异常: {e}')

print('\n' + '='*80)
print('测试完成')
print('='*80)
