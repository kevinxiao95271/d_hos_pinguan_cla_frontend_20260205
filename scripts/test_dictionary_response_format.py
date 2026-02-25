# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json

BASE_URL = 'http://localhost:6031/api'

print('='*80)
print('检查字典API响应格式')
print('='*80)

url = f'{BASE_URL}/dictionaries/subject_type'
print(f'\nURL: {url}')

try:
    response = requests.get(url, timeout=10)
    print(f'状态码: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        
        print(f'\n响应类型: {type(result).__name__}')
        print(f'\n完整响应:')
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 判断格式
        if isinstance(result, list):
            print('\n✅ 响应格式: 直接返回列表')
            print(f'✅ 数据量: {len(result)}')
            if result:
                print(f'✅ 第一条数据: {result[0]}')
        elif isinstance(result, dict):
            if result.get('success'):
                print('\n✅ 响应格式: 标准格式 {success: true, data: [...]}')
                data = result.get('data', [])
                print(f'✅ 数据量: {len(data)}')
                if data:
                    print(f'✅ 第一条数据: {data[0]}')
            else:
                print('\n❌ 响应格式: 字典但无success字段')
                print(f'内容: {result}')
    else:
        print(f'❌ 请求失败: {response.text[:200]}')
except Exception as e:
    print(f'❌ 异常: {e}')
