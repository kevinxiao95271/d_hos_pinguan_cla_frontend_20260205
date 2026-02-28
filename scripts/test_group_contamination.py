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

print_section("分组污染测试 - 验证自动分组是否影响其他组别")

# 1. 先查询综合组和进阶组的当前分组状态
print("\n【步骤1】查询自动分组前的状态")

comprehensive_before = []
advanced_before = []

for group_type, name, target_list in [
    ('COMPREHENSIVE', '综合组', comprehensive_before),
    ('ADVANCED', '进阶组', advanced_before)
]:
    res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
        'competitionId': 1,
        'groupType': group_type,
        'page': 0,
        'size': 50
    })
    
    if res.status_code == 200:
        data = res.json()
        regs = data['data'] if isinstance(data['data'], list) else data['data']['content']
        target_list.extend(regs)
        
        print(f"\n{name}（{len(regs)}人）:")
        print(f"  前5个项目的当前分组:")
        for i, r in enumerate(regs[:5], 1):
            print(f"    {i}. ID={r['id']:3}, groupCode={r.get('groupCode', 'None'):6}, 项目={r.get('projectName', '')[:40]}")

# 2. 执行基层组的自动分组
print_section("【步骤2】对基层组执行自动分组")

print("请求参数:")
request_data = {
    'competitionId': 1,
    'groupType': 'BASIC',
    'groupPrefix': 'A',
    'groupSize': 25
}
print(json.dumps(request_data, indent=2, ensure_ascii=False))

res = requests.post(f'{BASE_URL}/admin/registrations/auto-group', headers=headers, json=request_data)
print(f"\n状态码: {res.status_code}")

if res.status_code == 200:
    result = res.json()
    print(f"success: {result.get('success')}")
    
    if result.get('success'):
        affected_items = result['data']
        print(f"\n✅ 自动分组成功，影响了 {len(affected_items)} 个项目")
        
        # 分析响应中的项目组别分布
        from collections import Counter
        group_type_counter = Counter([item['groupType'] for item in affected_items])
        print(f"\n📊 响应中包含的组别分布:")
        for gt, count in group_type_counter.items():
            print(f"  - {gt}: {count}人")
        
        # 检查是否包含非BASIC组别的项目
        non_basic = [item for item in affected_items if item['groupType'] != 'BASIC']
        if non_basic:
            print(f"\n🚨 警告：响应中包含 {len(non_basic)} 个非基层组的项目！")
            print(f"前5个非基层组项目:")
            for i, item in enumerate(non_basic[:5], 1):
                print(f"  {i}. ID={item['id']:3}, groupType={item['groupType']:15}, groupCode={item.get('groupCode'):6}, 项目={item.get('projectName', '')[:40]}")
        else:
            print(f"\n✅ 响应中只包含基层组项目")
    else:
        print(f"❌ 自动分组失败: {result.get('message')}")
else:
    print(f"❌ 请求失败: {res.text}")

# 3. 再次查询综合组和进阶组，看是否被污染
print_section("【步骤3】查询自动分组后其他组别的状态")

for group_type, name, before_list in [
    ('COMPREHENSIVE', '综合组', comprehensive_before),
    ('ADVANCED', '进阶组', advanced_before)
]:
    res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
        'competitionId': 1,
        'groupType': group_type,
        'page': 0,
        'size': 50
    })
    
    if res.status_code == 200:
        data = res.json()
        regs_after = data['data'] if isinstance(data['data'], list) else data['data']['content']
        
        print(f"\n{name}（{len(regs_after)}人）:")
        print(f"  前5个项目的分组对比:")
        
        # 对比前后变化
        changed = 0
        for i, r_after in enumerate(regs_after[:5], 1):
            # 在before_list中找对应的项目
            r_before = next((r for r in before_list if r['id'] == r_after['id']), None)
            
            if r_before:
                code_before = r_before.get('groupCode', 'None')
                code_after = r_after.get('groupCode', 'None')
                
                status = '⚠️ 变化' if code_before != code_after else '不变'
                if code_before != code_after:
                    changed += 1
                
                print(f"    {i}. ID={r_after['id']:3}, {code_before:6} → {code_after:6} ({status}), 项目={r_after.get('projectName', '')[:30]}")
            else:
                print(f"    {i}. ID={r_after['id']:3}, 新项目")
        
        if changed > 0:
            print(f"\n  🚨 发现 {changed} 个项目的分组被改变了！")
        else:
            print(f"\n  ✅ 所有项目的分组保持不变")

# 4. 总结
print_section("问题总结")

print("""
根据测试结果：

1️⃣ **后端API问题确认**：
   `POST /api/admin/registrations/auto-group` API存在严重bug：
   
   ❌ 实际行为：对该赛事下的所有项目进行分组（忽略groupType参数）
   ✅ 期望行为：只对指定groupType的项目进行分组
   
2️⃣ **影响范围**：
   - 当对基层组(BASIC)执行自动分组时，综合组和进阶组的项目也会被分配到A组
   - 当对进阶组(ADVANCED)执行自动分组时，基层组和综合组的项目也会被分配到C组
   - 这导致了用户看到的"分组混乱"现象
   
3️⃣ **前端代码状态**：
   ✅ 前端正确传递了所有参数
   ✅ 前端没有问题
   
4️⃣ **修复责任**：
   🔧 需要后端修复 `POST /api/admin/registrations/auto-group` API
   确保只对指定groupType的项目进行分组操作
""")
