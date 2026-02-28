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

# 登录
login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
    'phone': '13800000127',
    'password': 'committee2026'
})
token = login_res.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

print_section("验证后端修复效果 - 完整测试")

# 1. 对进阶组执行自动分组
print_section("步骤1: 对进阶组执行自动分组（groupType=ADVANCED）")

request_data = {
    'competitionId': 1,
    'groupType': 'ADVANCED',
    'groupPrefix': 'C',
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
        
        # 分析组别分布
        type_counter = Counter([item['groupType'] for item in affected])
        print(f"\n📊 响应中的组别分布:")
        for gt, count in type_counter.items():
            print(f"  - {gt}: {count}人")
        
        # 检查是否只包含ADVANCED
        non_advanced = [item for item in affected if item['groupType'] != 'ADVANCED']
        if non_advanced:
            print(f"\n❌ 响应中包含 {len(non_advanced)} 个非进阶组项目！")
            print(f"前3个示例:")
            for i, item in enumerate(non_advanced[:3], 1):
                print(f"  {i}. ID={item['id']}, groupType={item['groupType']}, groupCode={item['groupCode']}")
        else:
            print(f"\n✅ 响应中只包含进阶组项目（符合预期）")
    else:
        print(f"❌ 失败: {result.get('message')}")
else:
    print(f"❌ 请求失败: {res.text}")

# 2. 验证所有组别的分组状态
print_section("步骤2: 验证所有组别的最终分组状态")

res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': 1,
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
    
    name_map = {
        'BASIC': '基层组',
        'COMPREHENSIVE': '综合组',
        'ADVANCED': '进阶组'
    }
    
    print(f"\n各组别的分组状态:")
    
    all_correct = True
    summary = []
    
    for gt in ['BASIC', 'COMPREHENSIVE', 'ADVANCED']:
        if gt not in by_type:
            continue
        
        regs = by_type[gt]
        expected = expected_prefixes[gt]
        name = name_map[gt]
        
        group_codes = [r.get('groupCode') for r in regs if r.get('groupCode')]
        if group_codes:
            prefixes = set(code[0] for code in group_codes if code)
            code_counter = Counter(group_codes)
            
            if prefixes == {expected}:
                print(f"  ✅ {name}({len(regs)}人): 前缀={expected}, 分布={dict(code_counter)}")
                summary.append(f"✅ {name}在{expected}组")
            else:
                print(f"  ❌ {name}({len(regs)}人): 期望前缀={expected}, 实际前缀={prefixes}, 分布={dict(code_counter)}")
                summary.append(f"❌ {name}前缀错误")
                all_correct = False
        else:
            print(f"  ⚠️  {name}({len(regs)}人): 暂无分组")
            summary.append(f"⚠️  {name}无分组")
    
    print(f"\n" + "=" * 80)
    if all_correct:
        print("🎉 验证通过！后端API修复成功！")
        print("=" * 80)
        print("\n✅ 所有组别的分组前缀都正确：")
        for line in summary:
            print(f"   {line}")
        print("\n✅ 自动分组功能现在可以正常使用了！")
    else:
        print("⚠️  部分组别仍有问题（可能是历史遗留数据）")
        print("=" * 80)
        print("\n当前状态：")
        for line in summary:
            print(f"   {line}")
        print("\n💡 建议：对有问题的组别重新执行一次自动分组")
    print("=" * 80)

# 3. 详细验证：测试是否真的不会污染其他组别
print_section("步骤3: 详细验证 - 再次测试基层组，确认不会污染其他组别")

# 记录当前综合组和进阶组的状态
res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': 1,
    'groupType': 'COMPREHENSIVE',
    'page': 0,
    'size': 5
})
comp_before = res.json()['data'] if isinstance(res.json()['data'], list) else res.json()['data']['content']
comp_codes_before = {r['id']: r.get('groupCode') for r in comp_before}

res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': 1,
    'groupType': 'ADVANCED',
    'page': 0,
    'size': 5
})
adv_before = res.json()['data'] if isinstance(res.json()['data'], list) else res.json()['data']['content']
adv_codes_before = {r['id']: r.get('groupCode') for r in adv_before}

print("记录了综合组和进阶组前5个项目的当前分组状态")

# 再次对基层组执行自动分组
print("\n执行基层组自动分组...")
res = requests.post(f'{BASE_URL}/admin/registrations/auto-group', headers=headers, json={
    'competitionId': 1,
    'groupType': 'BASIC',
    'groupPrefix': 'A',
    'groupSize': 25
})

if res.status_code == 200 and res.json().get('success'):
    print(f"✅ 自动分组成功")
    
    # 验证综合组
    res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
        'competitionId': 1,
        'groupType': 'COMPREHENSIVE',
        'page': 0,
        'size': 5
    })
    comp_after = res.json()['data'] if isinstance(res.json()['data'], list) else res.json()['data']['content']
    
    print(f"\n综合组验证:")
    changed = 0
    for r in comp_after:
        before = comp_codes_before.get(r['id'])
        after = r.get('groupCode')
        if before != after:
            changed += 1
            print(f"  ❌ ID={r['id']}: {before} → {after}")
    
    if changed == 0:
        print(f"  ✅ 综合组的分组编号没有改变（不受影响）")
    else:
        print(f"  ❌ 有{changed}个综合组项目的分组被改变了")
    
    # 验证进阶组
    res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
        'competitionId': 1,
        'groupType': 'ADVANCED',
        'page': 0,
        'size': 5
    })
    adv_after = res.json()['data'] if isinstance(res.json()['data'], list) else res.json()['data']['content']
    
    print(f"\n进阶组验证:")
    changed = 0
    for r in adv_after:
        before = adv_codes_before.get(r['id'])
        after = r.get('groupCode')
        if before != after:
            changed += 1
            print(f"  ❌ ID={r['id']}: {before} → {after}")
    
    if changed == 0:
        print(f"  ✅ 进阶组的分组编号没有改变（不受影响）")
    else:
        print(f"  ❌ 有{changed}个进阶组项目的分组被改变了")
