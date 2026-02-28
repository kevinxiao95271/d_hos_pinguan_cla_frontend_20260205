#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
from collections import Counter

BASE_URL = 'http://localhost:6039/api'

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def analyze_group_distribution(registrations, title):
    """分析分组分布"""
    print(f"\n{title}")
    
    # 按组别分类
    by_type = {}
    for r in registrations:
        gt = r.get('groupType')
        if gt not in by_type:
            by_type[gt] = []
        by_type[gt].append(r)
    
    for gt, regs in by_type.items():
        group_codes = [r.get('groupCode') for r in regs if r.get('groupCode')]
        if group_codes:
            prefixes = Counter([code[0] for code in group_codes])
            print(f"  {gt}: {len(regs)}人, 前缀分布={dict(prefixes)}")
        else:
            print(f"  {gt}: {len(regs)}人, 暂无分组")

# 登录
print_section("步骤1: 评委会登录")
login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
    'phone': '13800000127',
    'password': 'committee2026'
})
token = login_res.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}
competition_id = 1

print(f"✅ 登录成功，当前赛事ID: {competition_id}")

# 测试1: 对基层组执行自动分组
print_section("测试1: 对基层组执行自动分组（groupType=BASIC）")

print("📤 请求参数:")
request_data = {
    'competitionId': competition_id,
    'groupType': 'BASIC',
    'groupPrefix': 'A',
    'groupSize': 25
}
print(json.dumps(request_data, indent=2, ensure_ascii=False))

res = requests.post(f'{BASE_URL}/admin/registrations/auto-group', headers=headers, json=request_data)
print(f"\n📥 状态码: {res.status_code}")

if res.status_code == 200:
    result = res.json()
    if result.get('success'):
        affected = result['data']
        print(f"✅ 成功，影响了 {len(affected)} 个项目")
        
        # 分析响应中的组别分布
        type_counter = Counter([item['groupType'] for item in affected])
        print(f"\n📊 响应中的组别分布:")
        for gt, count in type_counter.items():
            print(f"  - {gt}: {count}人")
        
        # 检查是否只包含BASIC
        non_basic = [item for item in affected if item['groupType'] != 'BASIC']
        if non_basic:
            print(f"\n❌ 响应中包含 {len(non_basic)} 个非基层组项目！")
            print(f"前3个示例:")
            for i, item in enumerate(non_basic[:3], 1):
                print(f"  {i}. ID={item['id']}, groupType={item['groupType']}, groupCode={item['groupCode']}")
        else:
            print(f"\n✅ 响应中只包含基层组项目（符合预期）")
    else:
        print(f"❌ 失败: {result.get('message')}")
else:
    print(f"❌ 请求失败: {res.text}")

# 查询综合组和进阶组，验证是否被污染
print_section("测试2: 验证其他组别是否被污染")

for group_type, name in [('COMPREHENSIVE', '综合组'), ('ADVANCED', '进阶组')]:
    res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
        'competitionId': competition_id,
        'groupType': group_type,
        'page': 0,
        'size': 10
    })
    
    if res.status_code == 200:
        data = res.json()
        regs = data['data'] if isinstance(data['data'], list) else data['data']['content']
        
        print(f"\n{name}（查询前10个）:")
        
        # 检查前缀
        group_codes = [r.get('groupCode') for r in regs if r.get('groupCode')]
        if group_codes:
            prefixes = set(code[0] for code in group_codes if code)
            print(f"  分组前缀: {prefixes}")
            
            # 显示前5个
            print(f"  前5个项目:")
            for i, r in enumerate(regs[:5], 1):
                code = r.get('groupCode', 'None')
                status = '✅' if (group_type == 'COMPREHENSIVE' and code and code[0] == 'B') or \
                                (group_type == 'ADVANCED' and code and code[0] == 'C') else '❌'
                print(f"    {i}. ID={r['id']:3}, groupCode={code:6} {status}")
            
            # 判断
            if group_type == 'COMPREHENSIVE':
                expected = 'B'
                if prefixes == {expected} or prefixes == set():
                    print(f"  ✅ {name}的分组前缀正确（应为{expected}）或无分组")
                else:
                    print(f"  ❌ {name}的分组前缀错误！期望{expected}，实际{prefixes}")
            elif group_type == 'ADVANCED':
                expected = 'C'
                if prefixes == {expected} or prefixes == set():
                    print(f"  ✅ {name}的分组前缀正确（应为{expected}）或无分组")
                else:
                    print(f"  ❌ {name}的分组前缀错误！期望{expected}，实际{prefixes}")
        else:
            print(f"  ⚠️  暂无分组")

# 测试2: 对综合组执行自动分组
print_section("测试3: 对综合组执行自动分组（groupType=COMPREHENSIVE）")

request_data = {
    'competitionId': competition_id,
    'groupType': 'COMPREHENSIVE',
    'groupPrefix': 'B',
    'groupSize': 25
}
print("📤 请求参数:")
print(json.dumps(request_data, indent=2, ensure_ascii=False))

res = requests.post(f'{BASE_URL}/admin/registrations/auto-group', headers=headers, json=request_data)
print(f"\n📥 状态码: {res.status_code}")

if res.status_code == 200:
    result = res.json()
    if result.get('success'):
        affected = result['data']
        print(f"✅ 成功，影响了 {len(affected)} 个项目")
        
        type_counter = Counter([item['groupType'] for item in affected])
        print(f"\n📊 响应中的组别分布:")
        for gt, count in type_counter.items():
            print(f"  - {gt}: {count}人")
        
        non_comprehensive = [item for item in affected if item['groupType'] != 'COMPREHENSIVE']
        if non_comprehensive:
            print(f"\n❌ 响应中包含 {len(non_comprehensive)} 个非综合组项目！")
        else:
            print(f"\n✅ 响应中只包含综合组项目（符合预期）")

# 验证基层组是否被污染
print_section("测试4: 验证基层组是否仍在A组")

res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': competition_id,
    'groupType': 'BASIC',
    'page': 0,
    'size': 10
})

if res.status_code == 200:
    data = res.json()
    regs = data['data'] if isinstance(data['data'], list) else data['data']['content']
    
    print(f"\n基层组（查询前10个）:")
    group_codes = [r.get('groupCode') for r in regs if r.get('groupCode')]
    if group_codes:
        prefixes = set(code[0] for code in group_codes if code)
        print(f"  分组前缀: {prefixes}")
        
        if prefixes == {'A'}:
            print(f"  ✅ 基层组的分组前缀仍然正确（A组）")
        else:
            print(f"  ❌ 基层组的分组前缀被污染了！实际: {prefixes}")

# 最终验证
print_section("最终验证：查询所有组别的分组状态")

res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': competition_id,
    'page': 0,
    'size': 200
})

if res.status_code == 200:
    data = res.json()
    all_regs = data['data'] if isinstance(data['data'], list) else data['data']['content']
    
    print(f"\n📊 总报名数: {len(all_regs)}")
    
    # 按组别统计
    by_type = {}
    for r in all_regs:
        gt = r.get('groupType')
        if gt not in by_type:
            by_type[gt] = []
        by_type[gt].append(r)
    
    expected_prefixes = {
        'BASIC': 'A',
        'COMPREHENSIVE': 'B',
        'ADVANCED': 'C'
    }
    
    print(f"\n各组别的分组状态:")
    
    all_correct = True
    for gt in ['BASIC', 'COMPREHENSIVE', 'ADVANCED']:
        if gt not in by_type:
            continue
        
        regs = by_type[gt]
        expected = expected_prefixes[gt]
        
        group_codes = [r.get('groupCode') for r in regs if r.get('groupCode')]
        if group_codes:
            prefixes = set(code[0] for code in group_codes if code)
            prefix_counter = Counter([code[0] for code in group_codes if code])
            
            name_map = {'BASIC': '基层组', 'COMPREHENSIVE': '综合组', 'ADVANCED': '进阶组'}
            name = name_map[gt]
            
            if prefixes == {expected}:
                print(f"  ✅ {name}({len(regs)}人): 前缀={expected}, 分布={dict(Counter(group_codes))}")
            else:
                print(f"  ❌ {name}({len(regs)}人): 期望前缀={expected}, 实际前缀={prefixes}")
                all_correct = False
        else:
            print(f"  ⚠️  {gt}({len(regs)}人): 暂无分组")
    
    print(f"\n" + "=" * 80)
    if all_correct:
        print("🎉 验证通过！所有组别的分组前缀都正确！")
        print("   - 基层组在A组 ✅")
        print("   - 综合组在B组 ✅")
        print("   - 进阶组在C组 ✅")
    else:
        print("❌ 仍存在分组混乱问题")
    print("=" * 80)
