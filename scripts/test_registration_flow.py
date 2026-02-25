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
print('║' + ' ' * 25 + '报名流程完整测试' + ' ' * 26 + '║')
print('╚' + '═' * 78 + '╝\n')

print('🎯 测试目标:')
print('   1. 路径A: 注册 → 自动登录(返回token) → 创建报名(不传institutionId)')
print('   2. 路径B: 账密登录 → 创建报名(不传institutionId)')
print('   3. 验证两条路径是否都能正确使用用户的所属机构')
print()

# ============================================================================
# 准备工作: 使用一个已知的机构ID（避免搜索超时）
# ============================================================================
print('='*80)
print('📍 准备工作: 使用测试机构')
print('='*80)

# 直接使用一个已知的机构ID
institution_id = 57548  # 金华婺城傅伟德中医骨伤科诊所
institution_name = '金华婺城傅伟德中医骨伤科诊所'
print(f'✅ 使用机构: {institution_name} (ID: {institution_id})')

# ============================================================================
# 路径A: 注册 → 自动登录 → 创建报名
# ============================================================================
print('\n' + '='*80)
print('🔵 路径A: 注册 → 自动登录 → 创建报名')
print('='*80)

# 生成随机手机号
phone_a = f'138{random.randint(10000000, 99999999)}'
password_a = 'Test1234'

print(f'\n步骤1: 注册新用户')
print(f'手机号: {phone_a}')
print(f'密码: {password_a}')
print(f'机构ID: {institution_id}')

try:
    response = requests.post(
        f'{BASE_URL}/auth/register',
        json={
            'phone': phone_a,
            'password': password_a,
            'confirmPassword': password_a,
            'name': 'Test User A',
            'title': 'Doctor',
            'role': 'CONTESTANT',
            'institutionId': institution_id
        },
        timeout=10
    )
    
    print(f'响应状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print(f'响应: {json.dumps(result, indent=2, ensure_ascii=False)}')
        
        if result.get('success'):
            token_a = result.get('data', {}).get('token')
            user_id_a = result.get('data', {}).get('userId')
            user_institution_id = result.get('data', {}).get('institutionId')
            
            print(f'✅ 注册成功')
            print(f'   Token: {token_a[:50]}...')
            print(f'   用户ID: {user_id_a}')
            print(f'   用户机构ID: {user_institution_id}')
            
            if not token_a:
                print('❌ 未返回token，无法继续测试')
                sys.exit(1)
        else:
            print(f'❌ 注册失败: {result.get("message")}')
            sys.exit(1)
    else:
        print(f'❌ 请求失败: {response.text[:200]}')
        sys.exit(1)
except Exception as e:
    print(f'❌ 异常: {e}')
    sys.exit(1)

# 使用已知的竞赛ID
competition_id = 1
competition_name = '2026浙江省品管大赛'
print(f'\n步骤2: 使用竞赛: {competition_name} (ID: {competition_id})')

# 创建报名（不传institutionId）
print(f'\n步骤3: 创建报名（不传institutionId，期望后端自动使用用户机构）')
try:
    registration_data = {
        'competitionId': competition_id,
        # 'institutionId': institution_id,  # 故意不传
        'projectName': f'测试项目A-{random.randint(1000, 9999)}',
        'groupType': 'BASIC'
    }
    
    print(f'请求数据: {json.dumps(registration_data, indent=2, ensure_ascii=False)}')
    
    response = requests.post(
        f'{BASE_URL}/registrations',
        headers={'Authorization': f'Bearer {token_a}'},
        json=registration_data,
        timeout=10
    )
    
    print(f'响应状态码: {response.status_code}')
    print(f'响应: {response.text[:500]}')
    
    if response.status_code in [200, 201]:
        result = response.json()
        if result.get('success'):
            registration_id_a = result.get('data', {}).get('id')
            registration_institution_id = result.get('data', {}).get('institutionId')
            
            print(f'✅ 路径A - 创建报名成功')
            print(f'   报名ID: {registration_id_a}')
            print(f'   报名的机构ID: {registration_institution_id}')
            print(f'   用户的机构ID: {user_institution_id}')
            
            if registration_institution_id == user_institution_id:
                print(f'   ✅ 验证通过: 报名使用了用户的所属机构')
            else:
                print(f'   ❌ 验证失败: 报名机构ID与用户机构ID不一致')
        else:
            print(f'❌ 创建报名失败: {result.get("message")}')
    else:
        print(f'❌ 请求失败')
except Exception as e:
    print(f'❌ 异常: {e}')

# ============================================================================
# 路径B: 账密登录 → 创建报名
# ============================================================================
print('\n' + '='*80)
print('🟢 路径B: 账密登录 → 创建报名')
print('='*80)

# 生成新用户
phone_b = f'138{random.randint(10000000, 99999999)}'
password_b = 'Test5678'

print(f'\n步骤1: 先注册用户B（为了后续登录测试）')
print(f'手机号: {phone_b}')
print(f'密码: {password_b}')

try:
    response = requests.post(
        f'{BASE_URL}/auth/register',
        json={
            'phone': phone_b,
            'password': password_b,
            'confirmPassword': password_b,
            'name': 'Test User B',
            'title': 'Nurse',
            'role': 'CONTESTANT',
            'institutionId': institution_id
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            user_id_b = result.get('data', {}).get('userId')
            user_institution_id_b = result.get('data', {}).get('institutionId')
            print(f'✅ 用户B注册成功')
            print(f'   用户ID: {user_id_b}')
            print(f'   用户机构ID: {user_institution_id_b}')
        else:
            print(f'❌ 注册失败: {result.get("message")}')
            sys.exit(1)
    else:
        print(f'❌ 请求失败: {response.text[:200]}')
        sys.exit(1)
except Exception as e:
    print(f'❌ 异常: {e}')
    sys.exit(1)

print(f'\n步骤2: 使用账号密码登录')
try:
    response = requests.post(
        f'{BASE_URL}/auth/login-with-password',
        json={
            'phone': phone_b,
            'password': password_b
        },
        timeout=10
    )
    
    print(f'响应状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print(f'响应: {json.dumps(result, indent=2, ensure_ascii=False)}')
        
        if result.get('success'):
            token_b = result.get('data', {}).get('token')
            login_institution_id = result.get('data', {}).get('institutionId')
            
            print(f'✅ 登录成功')
            print(f'   Token: {token_b[:50]}...')
            print(f'   登录返回的机构ID: {login_institution_id}')
            
            if not token_b:
                print('❌ 未返回token，无法继续测试')
                sys.exit(1)
        else:
            print(f'❌ 登录失败: {result.get("message")}')
            sys.exit(1)
    else:
        print(f'❌ 请求失败: {response.text[:200]}')
        sys.exit(1)
except Exception as e:
    print(f'❌ 异常: {e}')
    sys.exit(1)

print(f'\n步骤3: 创建报名（不传institutionId，期望后端自动使用用户机构）')
try:
    registration_data = {
        'competitionId': competition_id,
        # 'institutionId': institution_id,  # 故意不传
        'projectName': f'测试项目B-{random.randint(1000, 9999)}',
        'groupType': 'COMPREHENSIVE'
    }
    
    print(f'请求数据: {json.dumps(registration_data, indent=2, ensure_ascii=False)}')
    
    response = requests.post(
        f'{BASE_URL}/registrations',
        headers={'Authorization': f'Bearer {token_b}'},
        json=registration_data,
        timeout=10
    )
    
    print(f'响应状态码: {response.status_code}')
    print(f'响应: {response.text[:500]}')
    
    if response.status_code in [200, 201]:
        result = response.json()
        if result.get('success'):
            registration_id_b = result.get('data', {}).get('id')
            registration_institution_id_b = result.get('data', {}).get('institutionId')
            
            print(f'✅ 路径B - 创建报名成功')
            print(f'   报名ID: {registration_id_b}')
            print(f'   报名的机构ID: {registration_institution_id_b}')
            print(f'   用户的机构ID: {user_institution_id_b}')
            
            if registration_institution_id_b == user_institution_id_b:
                print(f'   ✅ 验证通过: 报名使用了用户的所属机构')
            else:
                print(f'   ❌ 验证失败: 报名机构ID与用户机构ID不一致')
        else:
            print(f'❌ 创建报名失败: {result.get("message")}')
    else:
        print(f'❌ 请求失败')
except Exception as e:
    print(f'❌ 异常: {e}')

# ============================================================================
# 总结
# ============================================================================
print('\n' + '='*80)
print('📊 测试总结')
print('='*80)
print()
print('✅ 路径A测试完成 (注册 → 自动登录 → 创建报名)')
print('✅ 路径B测试完成 (注册 → 账密登录 → 创建报名)')
print()
print('📝 结论:')
print('   如果两条路径都显示"验证通过"，说明后端已完全支持：')
print('   - 注册时绑定机构')
print('   - 登录返回机构信息')
print('   - 创建报名时不传institutionId，自动使用用户机构')
print()
