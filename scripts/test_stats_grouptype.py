#!/usr/bin/env python3
"""测试统计API的组别统计数据"""
import requests
import json

BASE_URL = "http://localhost:6031/api"
TIMEOUT = 30

def login():
    url = f"{BASE_URL}/auth/login-with-password"
    data = {"phone": "13800000005", "password": "ops2026"}
    response = requests.post(url, json=data, timeout=TIMEOUT)
    result = response.json()
    if result.get('success'):
        return result['data']['token'], result['data'].get('currentCompetitionId', 1)
    return None, None

print("=" * 80)
print("测试统计API - 组别统计数据")
print("=" * 80)

token, competition_id = login()
if not token:
    print("❌ 登录失败")
    exit(1)

print(f"✅ 登录成功 (赛事ID: {competition_id})")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

url = f"{BASE_URL}/admin/stats/summary"
params = {'competitionId': competition_id}

print(f"\n请求: GET {url}")
print(f"参数: {json.dumps(params, ensure_ascii=False)}")

response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)

if response.status_code == 200:
    result = response.json()
    
    if result.get('success'):
        data = result.get('data', {})
        
        print(f"\n✅ API调用成功")
        print(f"\n返回的所有字段:")
        for key in data.keys():
            print(f"  - {key}")
        
        # 重点检查 groupTypeStats
        print(f"\n{'=' * 80}")
        print("组别统计数据 (groupTypeStats)")
        print(f"{'=' * 80}")
        
        if 'groupTypeStats' in data:
            group_stats = data['groupTypeStats']
            print(f"✅ 存在 groupTypeStats 字段")
            print(f"数据类型: {type(group_stats).__name__}")
            print(f"数据量: {len(group_stats) if isinstance(group_stats, list) else 'N/A'}")
            
            if isinstance(group_stats, list):
                if len(group_stats) > 0:
                    print(f"\n示例数据:")
                    for item in group_stats:
                        print(f"\n  {json.dumps(item, ensure_ascii=False, indent=4)}")
                else:
                    print(f"\n⚠️  groupTypeStats 是空数组")
                    print(f"   这就是为什么前端显示'暂无数据'")
            else:
                print(f"\n⚠️  groupTypeStats 不是数组: {group_stats}")
        else:
            print(f"❌ 不存在 groupTypeStats 字段")
            print(f"\n可能的原因:")
            print(f"  1. 后端没有返回这个字段")
            print(f"  2. 字段名称不匹配")
            print(f"  3. 后端优化时移除了这个字段")
        
        # 检查其他统计数据
        print(f"\n{'=' * 80}")
        print("其他统计数据")
        print(f"{'=' * 80}")
        print(f"报名数量: {data.get('registrationCount', 0)}")
        print(f"机构数量: {data.get('institutionCount', 'N/A')}")
        print(f"品管工具种类: {data.get('toolTypeCount', 0)}")
        print(f"评委数量: {data.get('reviewerCount', 0)}")
        
        # 完整数据
        print(f"\n{'=' * 80}")
        print("完整返回数据")
        print(f"{'=' * 80}")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
    else:
        print(f"❌ API返回失败: {result.get('message')}")
else:
    print(f"❌ HTTP {response.status_code}")
    print(response.text[:500])
