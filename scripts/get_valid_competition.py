# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests

BASE_URL = 'http://localhost:6031/api'

# 先注册一个临时用户获取token
print('注册临时用户获取token...')
import random
phone = f'138{random.randint(10000000, 99999999)}'

try:
    response = requests.post(
        f'{BASE_URL}/auth/register',
        json={
            'phone': phone,
            'password': 'Test1234',
            'confirmPassword': 'Test1234',
            'name': 'Temp User',
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
            print('❌ 注册失败')
            sys.exit(1)
    else:
        print('❌ 请求失败')
        sys.exit(1)
except Exception as e:
    print(f'❌ 异常: {e}')
    sys.exit(1)

# 获取竞赛列表
print('\n获取竞赛列表...')
try:
    response = requests.get(
        f'{BASE_URL}/competitions',
        headers={'Authorization': f'Bearer {token}'},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data'):
            competitions = result['data']
            print(f'✅ 找到{len(competitions)}个竞赛')
            for comp in competitions[:3]:
                print(f'   ID: {comp["id"]} - {comp["name"]} - {comp.get("stage", "N/A")}')
        else:
            print('未找到竞赛')
    else:
        print(f'失败: {response.text}')
except Exception as e:
    print(f'异常: {e}')
