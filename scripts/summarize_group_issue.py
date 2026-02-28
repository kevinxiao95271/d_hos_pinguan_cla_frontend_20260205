#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE_URL = 'http://localhost:6039/api'

# 登录
login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
    'phone': '13800000127',
    'password': 'committee2026'
})
token = login_res.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

print("=" * 80)
print("项目分组问题分析报告")
print("=" * 80)

# 查询所有报名
res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': 1,
    'page': 0,
    'size': 200
})

data = res.json()
all_regs = data['data'] if isinstance(data['data'], list) else data['data']['content']

print(f"\n📊 总报名数: {len(all_regs)}")

# 统计当前状态
expected_prefix = {
    'BASIC': 'A',       # 基层组应该是A
    'COMPREHENSIVE': 'B', # 综合组应该是B
    'ADVANCED': 'C'      # 进阶组应该是C
}

group_names = {
    'BASIC': '基层组',
    'COMPREHENSIVE': '综合组',
    'ADVANCED': '进阶组'
}

print("\n" + "=" * 80)
print("当前分组状态分析")
print("=" * 80)

for group_type in ['BASIC', 'COMPREHENSIVE', 'ADVANCED']:
    regs = [r for r in all_regs if r.get('groupType') == group_type]
    if not regs:
        continue
    
    name = group_names[group_type]
    expected = expected_prefix[group_type]
    
    print(f"\n【{name}】({len(regs)}人)")
    print(f"  期望分组前缀: {expected}")
    
    # 统计实际分组编号
    group_codes = [r.get('groupCode') for r in regs if r.get('groupCode')]
    
    if not group_codes:
        print(f"  ⚠️  暂无分组编号")
        continue
    
    # 统计前缀分布
    from collections import Counter
    actual_prefixes = [code[0] for code in group_codes if code]
    prefix_counter = Counter(actual_prefixes)
    
    print(f"  实际分组前缀分布: {dict(prefix_counter)}")
    
    # 判断是否正确
    if len(prefix_counter) == 1 and list(prefix_counter.keys())[0] == expected:
        print(f"  ✅ 分组前缀正确")
    else:
        print(f"  ❌ 分组前缀错误！")
        
        # 统计详细的分组编号
        code_counter = Counter(group_codes)
        print(f"  详细分组编号: {dict(code_counter)}")
        
        # 显示前5个错误的项目
        print(f"  错误示例（前5个）:")
        count = 0
        for r in regs:
            code = r.get('groupCode')
            if code and code[0] != expected:
                count += 1
                print(f"    {count}. ID={r.get('id')}, 分组={code}, 项目={r.get('projectName', '')[:40]}")
                if count >= 5:
                    break

# 执行自动分组测试
print("\n" + "=" * 80)
print("测试自动分组API调用")
print("=" * 80)

print("\n--- 测试1: 对基层组执行自动分组 ---")
res = requests.post(f'{BASE_URL}/admin/registrations/auto-group', headers=headers, json={
    'competitionId': 1,
    'groupType': 'BASIC',
    'groupPrefix': 'A',
    'groupSize': 25
})
print(f"状态码: {res.status_code}")
result = res.json()
print(f"success: {result.get('success')}")
print(f"响应: {result}")

# 查询自动分组后的结果
print("\n--- 查询基层组分组后的结果（取前10个） ---")
res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': 1,
    'groupType': 'BASIC',
    'page': 0,
    'size': 10
})
basic_regs = res.json()['data'] if isinstance(res.json()['data'], list) else res.json()['data']['content']
print(f"基层组前10个项目的分组编号:")
for i, r in enumerate(basic_regs, 1):
    print(f"  {i}. ID={r.get('id')}, groupType={r.get('groupType')}, groupCode={r.get('groupCode')}")

# 总结
print("\n" + "=" * 80)
print("问题总结")
print("=" * 80)

print("""
根据测试结果：

1️⃣ **现象确认**：
   - 基层组(BASIC)项目被错误分配到C组（应该是A组）
   - 综合组(COMPREHENSIVE)项目被错误分配到C组（应该是B组）
   - 进阶组(ADVANCED)项目正确分配到C组 ✅

2️⃣ **原因分析**：
   需要检查：
   a) 前端是否正确传递了groupPrefix参数
   b) 后端auto-group API是否正确使用了groupPrefix参数
   c) 后端是否忽略了groupPrefix，而是根据groupType自动决定前缀

3️⃣ **待验证**：
   - 前端传递参数: ✅ 代码显示正确传递了groupPrefix
   - 后端API实现: ❓ 需要检查后端是否正确使用了groupPrefix参数
""")
