#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试字典接口"""

import requests
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
    
    token = r.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功\n")
    
    # 2. 获取品管工具字典
    print("2️⃣  获取品管工具字典 /api/dictionaries/method")
    r = requests.get(f"{BASE_URL}/dictionaries/method", headers=headers, timeout=10)
    
    if r.status_code == 200:
        methods = r.json()['data']
        print(f"✅ 获取成功，共 {len(methods)} 项\n")
        print("品管工具列表:")
        for item in methods[:5]:  # 只显示前5项
            print(f"   - code: {item['code']:<20} label: {item['label']}")
        
        # 查找 qc_topic
        found = next((m for m in methods if m['code'] == 'qc_topic'), None)
        if found:
            print(f"\n✅ 找到 qc_topic: {found['label']}")
        else:
            print(f"\n❌ 未找到 qc_topic")
    else:
        print(f"❌ 获取失败: {r.status_code}")
    
    # 3. 获取主题类型字典
    print("\n3️⃣  获取主题类型字典 /api/dictionaries/subject_type")
    r = requests.get(f"{BASE_URL}/dictionaries/subject_type", headers=headers, timeout=10)
    
    if r.status_code == 200:
        subjects = r.json()['data']
        print(f"✅ 获取成功，共 {len(subjects)} 项\n")
        print("主题类型列表:")
        for item in subjects[:5]:  # 只显示前5项
            print(f"   - code: {item['code']:<20} label: {item['label']}")
        
        # 查找 education
        found = next((s for s in subjects if s['code'] == 'education'), None)
        if found:
            print(f"\n✅ 找到 education: {found['label']}")
        else:
            print(f"\n❌ 未找到 education")
    else:
        print(f"❌ 获取失败: {r.status_code}")
        
except Exception as e:
    print(f"❌ 错误: {e}")
