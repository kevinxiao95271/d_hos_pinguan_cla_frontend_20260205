#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试"我的报名"接口
"""

import sys
import io
import requests
import json

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = 'http://localhost:6031'

def main():
    print('🧪 测试"我的报名"API')
    print('=' * 80)
    
    # 方式1: 使用前端的 token（从浏览器中获取）
    print('\n请从浏览器的 localStorage 中复制 token:')
    print('1. 打开浏览器开发者工具 (F12)')
    print('2. 切换到 Console 标签')
    print('3. 输入: localStorage.getItem("token")')
    print('4. 复制输出的 token 值\n')
    
    token = input('请粘贴 token (不含引号): ').strip()
    
    if not token:
        print('❌ 未提供 token')
        return
    
    print(f'\n📊 测试: GET /api/registrations/my')
    print('=' * 80)
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/registrations/my',
            headers={'Authorization': f'Bearer {token}'},
            timeout=30
        )
        
        print(f'状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            
            # 打印原始响应
            print(f'\n📦 完整响应:')
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success'):
                data = result.get('data', [])
                print(f'\n✅ 获取成功: {len(data)} 条报名记录')
                
                if data:
                    print(f'\n📝 第一条数据的完整结构:')
                    print('-' * 80)
                    first = data[0]
                    
                    # 打印所有顶层字段
                    print('\n顶层字段:')
                    for key in first.keys():
                        print(f'  - {key}: {type(first[key]).__name__}')
                    
                    # 详细打印数据
                    print(f'\n详细数据:')
                    print(json.dumps(first, indent=2, ensure_ascii=False))
                    
                    # 检查关键字段
                    print(f'\n🔍 关键字段检查:')
                    print('-' * 80)
                    
                    fields = [
                        'id',
                        'projectName',
                        'institutionId',
                        'institutionName',
                        'institutionLevel',
                        'institution',
                        'groupType',
                        'status'
                    ]
                    
                    for field in fields:
                        value = first.get(field)
                        exists = '✅' if field in first else '❌'
                        
                        if isinstance(value, dict):
                            print(f'{exists} {field}: (对象)')
                            for k, v in value.items():
                                print(f'     - {k}: {v}')
                        elif isinstance(value, list):
                            print(f'{exists} {field}: (数组，{len(value)} 项)')
                        else:
                            print(f'{exists} {field}: {value}')
                else:
                    print('⚠️  没有报名记录')
            else:
                print(f'❌ 请求失败: {result.get("message")}')
        elif response.status_code == 401:
            print('❌ 认证失败: token 无效或已过期')
            print('   请重新登录并获取新的 token')
        else:
            print(f'❌ HTTP {response.status_code} 错误')
            print(f'响应: {response.text[:500]}')
            
    except requests.exceptions.RequestException as e:
        print(f'❌ 请求异常: {e}')
    except Exception as e:
        print(f'❌ 发生错误: {e}')

if __name__ == '__main__':
    main()
