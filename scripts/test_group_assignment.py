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

def analyze_group_codes(registrations, group_type_name):
    """分析分组编号分布"""
    group_codes = [r.get('groupCode') for r in registrations if r.get('groupCode')]
    if not group_codes:
        print(f"  ⚠️  没有分组编号")
        return
    
    counter = Counter(group_codes)
    print(f"  分组编号分布: {dict(counter)}")
    
    # 检查分组编号前缀
    prefixes = set(code[0] if code else None for code in group_codes)
    print(f"  分组前缀: {prefixes}")
    
    # 按前缀统计
    prefix_count = {}
    for code in group_codes:
        if code:
            prefix = code[0]
            prefix_count[prefix] = prefix_count.get(prefix, 0) + 1
    
    print(f"  前缀统计: {prefix_count}")
    
    # 显示前10个项目的分组
    print(f"  前10个项目的分组编号:")
    for i, r in enumerate(registrations[:10], 1):
        print(f"    {i}. ID={r.get('id')}, 组别={r.get('groupType')}, 分组={r.get('groupCode')}, 项目={r.get('projectName', '')[:30]}")

# 1. 登录
print_section("步骤1: 评委会登录")
login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
    'phone': '13800000127',
    'password': 'committee2026'
})

if login_res.status_code != 200:
    print(f"❌ 登录失败: {login_res.status_code}")
    print(f"响应: {login_res.text}")
    sys.exit(1)

login_data = login_res.json()
if not login_data.get('success'):
    print(f"❌ 登录失败: {login_data.get('message')}")
    sys.exit(1)

token = login_data['data']['token']
competition_id = login_data['data'].get('currentCompetitionId', 1)
print(f"✅ 登录成功")
print(f"   用户ID: {login_data['data']['id']}")
print(f"   姓名: {login_data['data']['name']}")
print(f"   角色: {login_data['data']['role']}")
print(f"   当前赛事ID: {competition_id}")

headers = {'Authorization': f'Bearer {token}'}

# 2. 查询当前所有报名的分组情况
print_section("步骤2: 查询所有报名的当前分组情况")
res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': competition_id,
    'page': 0,
    'size': 100
})

if res.status_code != 200:
    print(f"❌ 查询失败: {res.status_code}, {res.text}")
    sys.exit(1)

data = res.json()
if not data.get('success'):
    print(f"❌ 查询失败: {data.get('message')}")
    sys.exit(1)

# 检查data格式
if isinstance(data['data'], list):
    all_registrations = data['data']
    total_count = len(all_registrations)
else:
    all_registrations = data['data']['content']
    total_count = data['data']['totalElements']

print(f"✅ 总报名数: {total_count}")

# 按组别分类
by_group_type = {
    'BASIC': [],
    'COMPREHENSIVE': [],
    'ADVANCED': []
}

for r in all_registrations:
    gt = r.get('groupType')
    if gt in by_group_type:
        by_group_type[gt].append(r)

print(f"\n组别分布:")
print(f"  基层组(BASIC): {len(by_group_type['BASIC'])} 人")
print(f"  综合组(COMPREHENSIVE): {len(by_group_type['COMPREHENSIVE'])} 人")
print(f"  进阶组(ADVANCED): {len(by_group_type['ADVANCED'])} 人")

print(f"\n当前分组情况分析:")
for group_type, name in [('BASIC', '基层组'), ('COMPREHENSIVE', '综合组'), ('ADVANCED', '进阶组')]:
    if by_group_type[group_type]:
        print(f"\n【{name}】({len(by_group_type[group_type])}人):")
        analyze_group_codes(by_group_type[group_type], name)

# 3. 执行自动分组 - 基层组
print_section("步骤3: 对基层组执行自动分组（应分配到A组）")

auto_group_data = {
    'competitionId': competition_id,
    'groupType': 'BASIC',
    'groupPrefix': 'A',
    'groupSize': 25
}

print(f"请求参数: {json.dumps(auto_group_data, indent=2, ensure_ascii=False)}")

res = requests.post(f'{BASE_URL}/admin/registrations/auto-group', headers=headers, json=auto_group_data)
print(f"状态码: {res.status_code}")
print(f"响应: {res.text}")

if res.status_code == 200:
    result = res.json()
    if result.get('success'):
        print(f"✅ 自动分组成功")
        print(f"   响应数据: {result.get('data')}")
    else:
        print(f"❌ 自动分组失败: {result.get('message')}")
else:
    print(f"❌ 请求失败")

# 4. 查询基层组分组后的结果
print_section("步骤4: 查询基层组分组后的结果")

res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': competition_id,
    'groupType': 'BASIC',
    'page': 0,
    'size': 100
})

if res.status_code == 200:
    data = res.json()
    if data.get('success'):
        basic_regs = data['data'] if isinstance(data['data'], list) else data['data']['content']
        print(f"✅ 基层组报名数: {len(basic_regs)}")
        analyze_group_codes(basic_regs, '基层组')
    else:
        print(f"❌ 查询失败: {data.get('message')}")
else:
    print(f"❌ 请求失败: {res.status_code}")

# 5. 执行自动分组 - 进阶组
print_section("步骤5: 对进阶组执行自动分组（应分配到C组）")

auto_group_data = {
    'competitionId': competition_id,
    'groupType': 'ADVANCED',
    'groupPrefix': 'C',
    'groupSize': 25
}

print(f"请求参数: {json.dumps(auto_group_data, indent=2, ensure_ascii=False)}")

res = requests.post(f'{BASE_URL}/admin/registrations/auto-group', headers=headers, json=auto_group_data)
print(f"状态码: {res.status_code}")
print(f"响应: {res.text}")

if res.status_code == 200:
    result = res.json()
    if result.get('success'):
        print(f"✅ 自动分组成功")
        print(f"   响应数据: {result.get('data')}")
    else:
        print(f"❌ 自动分组失败: {result.get('message')}")

# 6. 查询进阶组分组后的结果
print_section("步骤6: 查询进阶组分组后的结果")

res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': competition_id,
    'groupType': 'ADVANCED',
    'page': 0,
    'size': 100
})

if res.status_code == 200:
    data = res.json()
    if data.get('success'):
        advanced_regs = data['data'] if isinstance(data['data'], list) else data['data']['content']
        print(f"✅ 进阶组报名数: {len(advanced_regs)}")
        analyze_group_codes(advanced_regs, '进阶组')
    else:
        print(f"❌ 查询失败: {data.get('message')}")

# 7. 查询全部（不带筛选）
print_section("步骤7: 查询全部报名（不带组别筛选）")

res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': competition_id,
    'page': 0,
    'size': 100
})

if res.status_code == 200:
    data = res.json()
    if data.get('success'):
        all_regs = data['data'] if isinstance(data['data'], list) else data['data']['content']
        print(f"✅ 总报名数: {len(all_regs)}")
        
        # 按组别统计分组编号
        print(f"\n各组别的分组编号分布:")
        for group_type, name in [('BASIC', '基层组'), ('COMPREHENSIVE', '综合组'), ('ADVANCED', '进阶组')]:
            regs = [r for r in all_regs if r.get('groupType') == group_type]
            if regs:
                print(f"\n【{name}】({len(regs)}人):")
                analyze_group_codes(regs, name)

# 8. 分析问题
print_section("问题分析")

# 检查是否有组别和分组编号不匹配的情况
print("检查组别与分组编号的匹配情况:")

expected_prefix = {
    'BASIC': 'A',
    'COMPREHENSIVE': 'B',
    'ADVANCED': 'C'
}

mismatches = []
for r in all_regs:
    group_type = r.get('groupType')
    group_code = r.get('groupCode')
    
    if group_type and group_code:
        expected = expected_prefix.get(group_type)
        actual = group_code[0] if group_code else None
        
        if expected != actual:
            mismatches.append({
                'id': r.get('id'),
                'projectName': r.get('projectName', '')[:30],
                'groupType': group_type,
                'groupCode': group_code,
                'expected_prefix': expected,
                'actual_prefix': actual
            })

if mismatches:
    print(f"\n❌ 发现 {len(mismatches)} 个不匹配的项目:")
    for i, m in enumerate(mismatches[:20], 1):  # 只显示前20个
        print(f"  {i}. ID={m['id']}, 组别={m['groupType']}, 分组={m['groupCode']}, 项目={m['projectName']}")
        print(f"      期望前缀: {m['expected_prefix']}, 实际前缀: {m['actual_prefix']}")
else:
    print(f"\n✅ 所有项目的组别与分组编号匹配正确")

# 9. 测试单个项目分组
print_section("步骤8: 测试单个项目分组操作")

if mismatches:
    # 选择第一个不匹配的项目进行测试
    test_reg = mismatches[0]
    test_id = test_reg['id']
    correct_group_code = f"{test_reg['expected_prefix']}1"
    
    print(f"测试项目: ID={test_id}, 当前分组={test_reg['groupCode']}")
    print(f"尝试修改为正确的分组编号: {correct_group_code}")
    
    # 查看是否有单个分组的API
    # 先尝试PATCH方法
    res = requests.patch(f'{BASE_URL}/admin/registrations/{test_id}', headers=headers, json={
        'groupCode': correct_group_code
    })
    print(f"PATCH更新分组 - 状态码: {res.status_code}, 响应: {res.text[:200]}")
    
    # 尝试PUT方法
    res = requests.put(f'{BASE_URL}/admin/registrations/{test_id}', headers=headers, json={
        'groupCode': correct_group_code
    })
    print(f"PUT更新分组 - 状态码: {res.status_code}, 响应: {res.text[:200]}")
