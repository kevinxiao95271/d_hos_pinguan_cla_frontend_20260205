#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试不同的 token header 格式"""

import requests
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:6031/api"

print("="*60)
print("测试不同的 Token Header 格式")
print("="*60)

try:
    # 1. 登录
    print("\n1️⃣  登录获取 token...")
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
    print(f"✅ 登录成功")
    print(f"   Token (前20字符): {token[:20]}...")
    
    # 2. 测试三种 header 格式
    test_cases = [
        {
            "name": "格式1: Authorization: Bearer {token}",
            "headers": {"Authorization": f"Bearer {token}"}
        },
        {
            "name": "格式2: Authorization: {token}",
            "headers": {"Authorization": token}
        },
        {
            "name": "格式3: token: {token}",
            "headers": {"token": token}
        }
    ]
    
    for i, test in enumerate(test_cases, 2):
        print(f"\n{i}️⃣  {test['name']}")
        print(f"   Headers: {test['headers']}")
        
        try:
            r = requests.get(
                f"{BASE_URL}/admin/registrations/filter",
                headers=test['headers'],
                params={"competitionId": 21},
                timeout=30
            )
            
            print(f"   状态码: {r.status_code}")
            
            if r.status_code == 200:
                data = r.json()['data']
                print(f"   ✅ 成功！返回 {len(data)} 条数据")
                
                # 检查第一条数据的关键字段
                if len(data) > 0:
                    first = data[0]
                    print(f"\n   第一条数据验证:")
                    print(f"      - methodLabel: {first.get('methodLabel')}")
                    print(f"      - subjectTypeLabel: {first.get('subjectTypeLabel')}")
                    print(f"      - institutionName: {first.get('institutionName')}")
                    print(f"      - applicantName: {first.get('applicantName')}")
                
                print(f"\n   🎉 这种格式可用！")
                break  # 找到可用的格式就停止
            elif r.status_code == 401:
                print(f"   ❌ 401 未授权")
            else:
                print(f"   ❌ 失败: {r.text[:200]}")
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
    
    print("\n" + "="*60)
    print("测试结论:")
    print("="*60)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
