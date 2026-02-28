#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

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

print_section("测试自动分组API是否支持registrationIds参数")

# 1. 查询一些基层组的项目
print("\n步骤1: 查询基层组项目")
res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
    'competitionId': 1,
    'groupType': 'BASIC',
    'page': 0,
    'size': 5
})

data = res.json()
basic_regs = data['data'] if isinstance(data['data'], list) else data['data']['content']
basic_ids = [r['id'] for r in basic_regs]

print(f"✅ 获取到{len(basic_ids)}个基层组项目ID: {basic_ids}")

# 2. 测试: 传递registrationIds参数
print_section("测试1: 自动分组API + registrationIds参数")

request_data = {
    'competitionId': 1,
    'groupType': 'BASIC',
    'groupPrefix': 'A',
    'groupSize': 25,
    'registrationIds': basic_ids  # 添加项目ID列表
}

print("📤 请求参数:")
print(json.dumps(request_data, indent=2, ensure_ascii=False))

res = requests.post(f'{BASE_URL}/admin/registrations/auto-group', headers=headers, json=request_data)
print(f"\n📥 状态码: {res.status_code}")
print(f"响应: {res.text[:500]}")

if res.status_code == 200:
    result = res.json()
    if result.get('success'):
        affected = result['data']
        print(f"\n✅ 成功，影响了 {len(affected)} 个项目")
        
        # 检查是否只影响了指定的项目
        affected_ids = [item['id'] for item in affected]
        print(f"受影响的项目ID: {affected_ids[:10]}...")
        
        # 对比
        if set(affected_ids) == set(basic_ids):
            print(f"✅ 只影响了指定的{len(basic_ids)}个项目")
        elif len(affected_ids) == len(basic_ids):
            print(f"⚠️  影响了{len(affected_ids)}个项目，数量一致但ID可能不同")
        else:
            print(f"❌ 影响了{len(affected_ids)}个项目，但请求中只指定了{len(basic_ids)}个")

# 3. 测试: 只传递groupType，不传registrationIds
print_section("测试2: 自动分组API，只传groupType")

request_data = {
    'competitionId': 1,
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
        
        from collections import Counter
        type_counter = Counter([item['groupType'] for item in affected])
        print(f"\n📊 响应中的组别分布:")
        for gt, count in type_counter.items():
            print(f"  - {gt}: {count}人")

# 4. 测试: 查看批量分类API的参数格式
print_section("测试3: 批量分类API参数格式")

request_data = {
    'registrationIds': basic_ids[:3],  # 只选3个项目
    'groupCode': 'TEST1'
}

print("📤 批量分类请求参数:")
print(json.dumps(request_data, indent=2, ensure_ascii=False))

res = requests.post(f'{BASE_URL}/admin/registrations/batch-classify', headers=headers, json=request_data)
print(f"\n📥 状态码: {res.status_code}")
print(f"响应: {res.text[:300]}")

# 5. 对比两个API的设计
print_section("API设计对比")

print("""
📌 当前两个API的设计：

1️⃣ 批量分类（batch-classify）：
   - 用户勾选项目
   - 前端传递: registrationIds=[1,2,3] + groupCode
   - 后端处理: 只对指定ID的项目进行分类
   
2️⃣ 自动分组（auto-group）：
   - 用户选择筛选条件（组别）
   - 前端传递: groupType + groupPrefix + groupSize
   - 后端处理: 对符合条件的所有项目自动分组
   
💡 用户建议：
   自动分组也应该基于勾选的项目，而不是筛选条件
   
🤔 分析：
   如果采用用户建议：
   - 优点: 更精确控制，不会误伤其他项目
   - 缺点: "自动"的意义减弱，需要手动勾选所有项目
   
   如果保持当前设计但修复后端：
   - 优点: 真正的"自动"，按规则批量处理
   - 缺点: 需要后端正确使用groupType参数筛选
""")

# 6. 建议的修改方案
print_section("修改方案建议")

print("""
方案A: 修改前端，自动分组改为基于勾选（用户建议）
------------------------------------------------------
前端修改:
  1. autoGroup函数检查 selectedRegistrations.value
  2. 传递参数改为: {registrationIds, groupPrefix, groupSize}
  3. 后端相应修改API实现

方案B: 保持前端不变，修复后端groupType筛选（当前计划）
------------------------------------------------------
后端修改:
  1. 确保auto-group API正确使用groupType参数
  2. 只对指定groupType的项目进行分组
  3. 前端无需改动

推荐: 需要确认产品设计意图
  - 如果"自动分组"=批量处理符合条件的所有项目 → 方案B
  - 如果"自动分组"=对勾选的项目自动分配编号 → 方案A
""")
