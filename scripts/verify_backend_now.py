#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""立即验证后端返回的数据"""

import requests
import json
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:6031/api"

try:
    # 1. 登录
    print("1️⃣  登录...")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Title",
        "role": "COMMITTEE_ADMIN"
    }, timeout=10)
    
    if r.status_code != 200:
        print(f"❌ 登录失败: {r.status_code}")
        print(r.text)
        sys.exit(1)
    
    token = r.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ 登录成功\n")
    
    # 2. 测试列表接口
    print("2️⃣  测试列表接口 /api/registrations")
    r = requests.get(f"{BASE_URL}/registrations?competitionId=21", headers=headers, timeout=10)
    
    if r.status_code == 200:
        data = r.json()['data']
        print(f"✅ 列表请求成功，共 {len(data)} 条")
        if len(data) > 0:
            first = data[0]
            print("\n第一条数据的字段:")
            for key in sorted(first.keys()):
                print(f"   - {key}: {first[key]}")
            
            first_id = first['id']
            
            # 3. 测试详情接口
            print(f"\n3️⃣  测试详情接口 /api/registrations/{first_id}")
            r = requests.get(f"{BASE_URL}/registrations/{first_id}", headers=headers, timeout=10)
            
            if r.status_code == 200:
                detail = r.json()['data']
                print("✅ 详情请求成功\n")
                print("=" * 60)
                print("详情数据结构:")
                print("=" * 60)
                print(json.dumps(detail, indent=2, ensure_ascii=False))
                print("\n" + "=" * 60)
                
                # 检查关键字段
                print("\n4️⃣  检查关键字段:")
                if 'activityInfo' in detail:
                    activity = detail['activityInfo']
                    print(f"   ✅ activityInfo 存在")
                    print(f"      - methodCode: {activity.get('methodCode')}")
                    print(f"      - methodLabel: {activity.get('methodLabel')}")
                    print(f"      - subjectTypeCode: {activity.get('subjectTypeCode')}")
                    print(f"      - subjectTypeLabel: {activity.get('subjectTypeLabel')}")
                else:
                    print(f"   ❌ activityInfo 不存在")
            else:
                print(f"❌ 详情请求失败: {r.status_code}")
                print(r.text)
    else:
        print(f"❌ 列表请求失败: {r.status_code}")
        print(r.text)
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
