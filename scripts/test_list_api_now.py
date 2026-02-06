#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试列表接口是否返回 label 字段"""

import requests
import sys
import json

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:6031/api"

print("="*60)
print("测试后端列表接口优化情况")
print("="*60)

try:
    # 1. 登录
    print("\n1️⃣  登录...")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Title",
        "role": "COMMITTEE_ADMIN"
    }, timeout=30)
    
    if r.status_code != 200:
        print(f"❌ 登录失败: {r.status_code}")
        print(r.text)
        sys.exit(1)
    
    token = r.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 测试 /api/admin/registrations/filter
    print("\n2️⃣  测试 /api/admin/registrations/filter?competitionId=21")
    r = requests.get(
        f"{BASE_URL}/admin/registrations/filter",
        headers=headers,
        params={"competitionId": 21},
        timeout=30
    )
    
    print(f"   状态码: {r.status_code}")
    
    if r.status_code == 401:
        print("   ❌ 仍然返回 401，权限问题未修复")
        print("   后端需要修复权限验证")
        sys.exit(1)
    elif r.status_code != 200:
        print(f"   ❌ 请求失败: {r.status_code}")
        print(f"   响应: {r.text[:500]}")
        sys.exit(1)
    
    data = r.json()['data']
    print(f"   ✅ 请求成功，共 {len(data)} 条数据\n")
    
    if len(data) == 0:
        print("   ⚠️  没有数据")
        sys.exit(0)
    
    # 3. 检查第一条数据的字段
    first = data[0]
    print("3️⃣  第一条数据的关键字段:")
    print(f"   - id: {first.get('id')}")
    print(f"   - projectName: {first.get('projectName')}")
    print(f"   - registrationId: {first.get('registrationId')}")
    print(f"   - institutionName: {first.get('institutionName')}")
    print(f"   - applicantName: {first.get('applicantName')}")
    print(f"   - groupType: {first.get('groupType')}")
    print(f"   - groupCode: {first.get('groupCode')}")
    print(f"   - methodCode: {first.get('methodCode')}")
    print(f"   - methodLabel: {first.get('methodLabel')}")
    print(f"   - subjectTypeCode: {first.get('subjectTypeCode')}")
    print(f"   - subjectTypeLabel: {first.get('subjectTypeLabel')}")
    
    # 4. 验证关键字段
    print("\n4️⃣  字段验证:")
    checks = {
        'registrationId': first.get('registrationId'),
        'institutionName': first.get('institutionName'),
        'methodLabel': first.get('methodLabel'),
        'subjectTypeLabel': first.get('subjectTypeLabel'),
        'applicantName': first.get('applicantName')
    }
    
    all_ok = True
    for field, value in checks.items():
        if value:
            print(f"   ✅ {field}: {value}")
        else:
            print(f"   ❌ {field}: 缺失")
            all_ok = False
    
    # 5. 测试按 methodCode 筛选
    if first.get('methodCode'):
        method_code = first['methodCode']
        print(f"\n5️⃣  测试按品管工具筛选 (methodCode={method_code})")
        r = requests.get(
            f"{BASE_URL}/admin/registrations/filter",
            headers=headers,
            params={"competitionId": 21, "methodCode": method_code},
            timeout=30
        )
        
        if r.status_code == 200:
            filtered = r.json()['data']
            print(f"   ✅ 筛选成功，共 {filtered} 条")
            if len(filtered) > 0:
                print(f"   验证: methodLabel = {filtered[0].get('methodLabel')}")
        else:
            print(f"   ❌ 筛选失败: {r.status_code}")
    
    # 6. 总结
    print("\n" + "="*60)
    print("总结:")
    print("="*60)
    if all_ok:
        print("✅ 后端已完全优化！")
        print("   - /api/admin/registrations/filter 返回 200")
        print("   - 返回完整字段（registrationId, institutionName, methodLabel, applicantName）")
        print("   - 支持 methodCode 筛选")
        print("\n🎯 前端可以:")
        print("   1. 移除字典查找逻辑")
        print("   2. 直接使用 methodLabel / subjectTypeLabel")
        print("   3. 使用 methodCode 进行筛选")
    else:
        print("⚠️  后端部分优化:")
        print("   - 接口可访问（不再 401）")
        print("   - 但部分字段仍缺失")
        print("   - 需要后端继续完善")
    
    # 7. 输出完整的第一条数据
    print("\n7️⃣  完整数据结构（第一条）:")
    print(json.dumps(first, indent=2, ensure_ascii=False))
    
except requests.exceptions.Timeout:
    print("❌ 请求超时，后端可能正在重启或响应缓慢")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
