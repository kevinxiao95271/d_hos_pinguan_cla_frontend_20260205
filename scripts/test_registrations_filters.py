#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 /api/registrations 接口的筛选参数"""

import requests
import sys

# 设置控制台编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:6031/api"

def test_filters():
    """测试筛选参数"""
    print("\n" + "="*60)
    print("测试 /api/registrations 接口筛选功能")
    print("="*60)
    
    # 1. 登录获取 token
    print("\n1️⃣  登录...")
    login_data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Title",
        "role": "COMMITTEE_ADMIN"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    token = response.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ 登录成功")
    
    # 2. 测试基础查询
    print("\n2️⃣  基础查询 (只传 competitionId=21)")
    response = requests.get(f"{BASE_URL}/registrations", 
                           headers=headers,
                           params={"competitionId": 21})
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✅ 返回 {len(data)} 条数据")
        if len(data) > 0:
            first = data[0]
            print(f"   第一条数据字段: {list(first.keys())}")
            print(f"   groupType: {first.get('groupType')}")
            print(f"   groupCode: {first.get('groupCode')}")
            print(f"   methodCode: {first.get('methodCode')}")
            print(f"   methodLabel: {first.get('methodLabel')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return
    
    # 3. 测试 groupType 筛选
    print("\n3️⃣  测试 groupType 筛选 (groupType=BASIC)")
    response = requests.get(f"{BASE_URL}/registrations",
                           headers=headers,
                           params={"competitionId": 21, "groupType": "BASIC"})
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✅ 返回 {len(data)} 条数据")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    # 4. 测试 groupCode 筛选
    print("\n4️⃣  测试 groupCode 筛选 (groupCode=A1)")
    response = requests.get(f"{BASE_URL}/registrations",
                           headers=headers,
                           params={"competitionId": 21, "groupCode": "A1"})
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✅ 返回 {len(data)} 条数据")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    # 5. 测试 methodCode 筛选
    print("\n5️⃣  测试 methodCode 筛选 (methodCode=qcc_problem)")
    response = requests.get(f"{BASE_URL}/registrations",
                           headers=headers,
                           params={"competitionId": 21, "methodCode": "qcc_problem"})
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✅ 返回 {len(data)} 条数据")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    # 6. 获取所有可用的 groupCode
    print("\n6️⃣  获取所有可用的 groupCode")
    response = requests.get(f"{BASE_URL}/registrations",
                           headers=headers,
                           params={"competitionId": 21})
    if response.status_code == 200:
        data = response.json()['data']
        group_codes = set(item.get('groupCode') for item in data if item.get('groupCode'))
        print(f"✅ 可用的 groupCode: {sorted(group_codes)}")
    
    # 7. 获取所有可用的 methodCode
    print("\n7️⃣  获取所有可用的 methodCode")
    response = requests.get(f"{BASE_URL}/registrations",
                           headers=headers,
                           params={"competitionId": 21})
    if response.status_code == 200:
        data = response.json()['data']
        method_codes = {}
        for item in data:
            code = item.get('methodCode')
            label = item.get('methodLabel', '未知')
            if code and code not in method_codes:
                method_codes[code] = label
        print(f"✅ 可用的 methodCode:")
        for code, label in sorted(method_codes.items()):
            print(f"   - {code}: {label}")

if __name__ == "__main__":
    test_filters()
