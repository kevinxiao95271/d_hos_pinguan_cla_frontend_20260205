#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试 label 字段"""

import requests
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:6031/api"

# 简化的登录数据
login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "title": "Title",
    "role": "COMMITTEE_ADMIN"
}

try:
    print("🔐 登录中...")
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
    print(f"登录响应: {r.status_code}")
    
    if r.status_code == 200:
        token = r.json()['data']['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n📋 获取列表...")
        r = requests.get(f"{BASE_URL}/registrations?competitionId=21", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()['data']
            if len(data) > 0:
                first_id = data[0]['id']
                
                print(f"\n📄 获取详情 (ID={first_id})...")
                r = requests.get(f"{BASE_URL}/registrations/{first_id}", headers=headers, timeout=5)
                if r.status_code == 200:
                    detail = r.json()['data']
                    activity = detail.get('activityInfo', {})
                    
                    print(f"\n✅ 关键字段检查:")
                    print(f"   - methodCode: {activity.get('methodCode')}")
                    print(f"   - methodLabel: {activity.get('methodLabel')}")
                    print(f"   - subjectTypeCode: {activity.get('subjectTypeCode')}")
                    print(f"   - subjectTypeLabel: {activity.get('subjectTypeLabel')}")
                    
                    if activity.get('methodLabel'):
                        print(f"\n🎉 品管工具中文名已返回！")
                    else:
                        print(f"\n⚠️  品管工具中文名为空，需要前端从字典查找")
                else:
                    print(f"❌ 详情请求失败: {r.status_code}")
        else:
            print(f"❌ 列表请求失败: {r.status_code}")
    else:
        print(f"❌ 登录失败，响应: {r.text[:200]}")
        
except Exception as e:
    print(f"❌ 错误: {e}")
