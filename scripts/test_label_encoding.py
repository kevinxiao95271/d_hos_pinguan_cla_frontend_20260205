#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Label字段的编码和实际内容
"""

import sys
import io
import requests
import json

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = 'http://localhost:6031'

def test():
    print('🔍 测试Label字段编码')
    print('=' * 80)
    
    # 登录
    response = requests.post(
        f'{BASE_URL}/api/auth/login',
        json={'phone': '13800000041', 'name': 'CommitteeAdmin A', 'role': 'COMMITTEE_ADMIN'},
        timeout=30
    )
    
    if response.status_code != 200:
        print('❌ 登录失败')
        return
    
    token = response.json()['data']['token']
    print('✅ 登录成功')
    
    # 获取详情
    print('\n📊 获取报名详情 (ID: 106)')
    response = requests.get(
        f'{BASE_URL}/api/registrations/106',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code != 200:
        print('❌ 获取失败')
        return
    
    result = response.json()
    activity_info = result['data']['activityInfo']
    
    print('\n【改善就医环境】')
    exp_label = activity_info.get('experienceImproveLabel')
    print(f'experienceImproveLabel 值: {exp_label}')
    print(f'  类型: {type(exp_label)}')
    print(f'  长度: {len(exp_label) if exp_label else 0}')
    print(f'  repr: {repr(exp_label)}')
    print(f'  字节: {exp_label.encode("utf-8") if exp_label else None}')
    
    print('\n【医疗质量相关主题】')
    qual_label = activity_info.get('qualityTopicLabel')
    print(f'qualityTopicLabel 值: {qual_label}')
    print(f'  类型: {type(qual_label)}')
    print(f'  长度: {len(qual_label) if qual_label else 0}')
    print(f'  repr: {repr(qual_label)}')
    if qual_label:
        print(f'  字节: {qual_label.encode("utf-8")}')
        print(f'  是否全是问号: {"是" if all(c == "?" for c in qual_label) else "否"}')
        print(f'  每个字符的Unicode: {[f"U+{ord(c):04X}" for c in qual_label[:5]]}')
    
    print('\n完整的activityInfo:')
    print(json.dumps(activity_info, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    test()
