#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试详情接口是否返回品管工具字段"""

import requests
import sys
import json

# 设置控制台编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:6031/api"

def test_detail():
    """测试详情接口"""
    print("\n" + "="*60)
    print("测试 /api/registrations/{id} 详情接口")
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
    
    # 2. 获取列表（获取第一个ID）
    print("\n2️⃣  获取报名列表...")
    response = requests.get(f"{BASE_URL}/registrations", 
                           headers=headers,
                           params={"competitionId": 21})
    if response.status_code != 200:
        print(f"❌ 获取列表失败: {response.status_code}")
        return
    
    data = response.json()['data']
    if len(data) == 0:
        print("❌ 没有报名数据")
        return
    
    first_id = data[0]['id']
    print(f"✅ 获取到列表，第一条 ID: {first_id}")
    
    # 3. 获取详情
    print(f"\n3️⃣  获取详情 (ID={first_id})...")
    response = requests.get(f"{BASE_URL}/registrations/{first_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取详情失败: {response.status_code}")
        print(f"   响应: {response.text}")
        return
    
    detail = response.json()['data']
    print(f"✅ 详情获取成功")
    
    # 4. 检查关键字段
    print("\n4️⃣  检查关键字段:")
    print(f"   - projectName: {detail.get('projectName')}")
    print(f"   - groupType: {detail.get('groupType')}")
    print(f"   - groupCode: {detail.get('groupCode')}")
    print(f"   - status: {detail.get('status')}")
    
    # 检查 activity 字段
    activity = detail.get('activity')
    if activity:
        print(f"\n   ✅ activity 字段存在:")
        print(f"      - methodCode: {activity.get('methodCode')}")
        print(f"      - methodLabel: {activity.get('methodLabel')}")
        print(f"      - subjectTypeCode: {activity.get('subjectTypeCode')}")
        print(f"      - subjectTypeLabel: {activity.get('subjectTypeLabel')}")
        print(f"      - theme: {activity.get('theme')}")
        print(f"      - keywords: {activity.get('keywords')}")
        print(f"      - avgWorkYears: {activity.get('avgWorkYears')}")
        print(f"      - avgAge: {activity.get('avgAge')}")
    else:
        print(f"\n   ❌ activity 字段不存在")
    
    # 检查 members 字段
    members = detail.get('members')
    if members:
        participants = [m for m in members if m.get('role') == 'PARTICIPANT']
        mentors = [m for m in members if m.get('role') == 'MENTOR']
        print(f"\n   ✅ members 字段存在:")
        print(f"      - 参与人员: {len(participants)} 人")
        print(f"      - 辅导员: {len(mentors)} 人")
        if participants:
            print(f"      - 第一个参与人员: {participants[0].get('name')} / {participants[0].get('title')}")
        if mentors:
            print(f"      - 第一个辅导员: {mentors[0].get('name')} / {mentors[0].get('title')}")
    else:
        print(f"\n   ❌ members 字段不存在")
    
    # 5. 输出完整 JSON（用于调试）
    print("\n5️⃣  完整 JSON 结构:")
    print(json.dumps(detail, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_detail()
