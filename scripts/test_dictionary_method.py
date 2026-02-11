#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字典API - 检查品管工具是否有重复数据
GET /api/dictionary?type=method
"""

import sys
import codecs
import requests
import json
from collections import Counter

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = 'http://localhost:6031/api'

def login_as_committee():
    """以组委会身份登录"""
    url = f'{BASE_URL}/auth/login'
    data = {
        'phone': '13800000127',
        'name': 'CommitteeAdmin A',
        'role': 'COMMITTEE_ADMIN'
    }
    
    print('🔐 登录组委会账号...')
    response = requests.post(url, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data', {}).get('token'):
            print(f'✅ 登录成功\n')
            return result['data']['token']
    
    print('❌ 登录失败')
    return None

def test_method_dictionary(token):
    """测试品管工具字典API"""
    url = f'{BASE_URL}/dictionaries/method'
    headers = {'Authorization': f'Bearer {token}'}
    
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 20 + '品管工具字典数据重复检查' + ' ' * 21 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    print('=' * 80)
    print('📊 测试品管工具字典API')
    print('=' * 80)
    print(f'API端点: {url}')
    print(f'Method: GET\n')
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f'Status Code: {response.status_code}\n')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API调用成功\n')
            
            if data.get('success'):
                methods = data.get('data', [])
                
                print(f'📈 返回数据总数: {len(methods)} 条\n')
                
                # 显示所有数据
                print('=' * 80)
                print('📋 所有品管工具数据:')
                print('=' * 80)
                print(f'{"序号":<6} {"code":<20} {"label":<30} {"order"}')
                print('-' * 80)
                
                for idx, item in enumerate(methods, 1):
                    code = item.get('code', '')
                    label = item.get('label', '')
                    order = item.get('order', '')
                    print(f'{idx:<6} {code:<20} {label:<30} {order}')
                
                # 检查重复的code
                print('\n' + '=' * 80)
                print('🔍 重复数据检查（按code）:')
                print('=' * 80)
                
                codes = [item.get('code') for item in methods]
                code_counts = Counter(codes)
                duplicates = {code: count for code, count in code_counts.items() if count > 1}
                
                if duplicates:
                    print(f'\n❌ 发现重复的code: {len(duplicates)} 个\n')
                    for code, count in duplicates.items():
                        print(f'   code="{code}" 出现了 {count} 次')
                        matching_items = [item for item in methods if item.get('code') == code]
                        for item in matching_items:
                            print(f'      - label: {item.get("label")}, order: {item.get("order")}')
                else:
                    print('\n✅ 没有重复的code')
                
                # 检查重复的label
                print('\n' + '=' * 80)
                print('🔍 重复数据检查（按label）:')
                print('=' * 80)
                
                labels = [item.get('label') for item in methods]
                label_counts = Counter(labels)
                label_duplicates = {label: count for label, count in label_counts.items() if count > 1}
                
                if label_duplicates:
                    print(f'\n❌ 发现重复的label: {len(label_duplicates)} 个\n')
                    for label, count in label_duplicates.items():
                        print(f'   label="{label}" 出现了 {count} 次')
                        matching_items = [item for item in methods if item.get('label') == label]
                        for item in matching_items:
                            print(f'      - code: {item.get("code")}, order: {item.get("order")}')
                        print()
                else:
                    print('\n✅ 没有重复的label')
                
                # 前端下拉框使用的是什么字段
                print('\n' + '=' * 80)
                print('🎯 前端使用情况分析:')
                print('=' * 80)
                print('\n前端代码（Registration.vue）:')
                print('   <el-option')
                print('     v-for="item in dictionaries.methods"')
                print('     :key="item.code"          ← 用code作为key')
                print('     :label="item.label"        ← 显示label')
                print('     :value="item.label"        ← 值也是label')
                print('   />')
                
                if label_duplicates:
                    print('\n🚨 问题根源:')
                    print('   前端使用 :value="item.label" 和 :key="item.code"')
                    print('   如果label重复，用户会看到重复的选项！')
                    print('\n📝 给后端的反馈:')
                    print(f'   API端点: GET /api/dictionary?type=method')
                    print(f'   问题: label字段有重复数据')
                    print(f'   重复数量: {len(label_duplicates)} 个label重复')
                    print('   影响: 前端下拉框会显示重复选项')
                    print('   建议: 删除重复的字典记录，保证label唯一')
                else:
                    print('\n✅ label没有重复，前端显示应该正常')
                
                # 生成SQL查询重复数据
                if label_duplicates or duplicates:
                    print('\n' + '=' * 80)
                    print('📝 后端排查SQL参考:')
                    print('=' * 80)
                    print('\n-- 查找重复的label')
                    print('SELECT label, COUNT(*) as count')
                    print('FROM dictionaries')
                    print("WHERE type = 'method'")
                    print('GROUP BY label')
                    print('HAVING COUNT(*) > 1;')
                    print('\n-- 查找重复的code')
                    print('SELECT code, COUNT(*) as count')
                    print('FROM dictionaries')
                    print("WHERE type = 'method'")
                    print('GROUP BY code')
                    print('HAVING COUNT(*) > 1;')
                
                return True
            else:
                print(f'⚠️  业务失败: {data.get("message")}')
                return False
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            print(f'   响应: {response.text[:500]}')
            return False
    except Exception as e:
        print(f'❌ 异常: {e}')
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    token = login_as_committee()
    if not token:
        print('❌ 无法获取token，终止测试')
        sys.exit(1)
    
    success = test_method_dictionary(token)
    
    print('\n' + '=' * 80)
    print('📊 检查结果')
    print('=' * 80)
    
    if success:
        print('✅ 数据获取成功，请查看上方的重复数据检查结果')
    else:
        print('❌ 数据获取失败')
    
    print('=' * 80 + '\n')
    
    sys.exit(0 if success else 1)
