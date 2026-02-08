import requests

# 1. 登录组委会管理员
login_url = "http://localhost:8080/api/auth/login"
login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}

print("=" * 60)
print("1. 登录组委会管理员...")
login_res = requests.post(login_url, json=login_data)
print(f"   登录状态码: {login_res.status_code}")

if login_res.status_code == 200:
    token = login_res.json()['data']['token']
    print(f"   ✅ 登录成功，Token: {token[:30]}...")
    
    # 2. 获取统计数据
    stats_url = "http://localhost:8080/api/admin/stats/summary"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 使用默认赛事ID 29
    params = {"competitionId": 29}
    
    print("\n2. 获取统计数据...")
    print(f"   URL: {stats_url}")
    print(f"   参数: {params}")
    
    stats_res = requests.get(stats_url, headers=headers, params=params)
    print(f"   状态码: {stats_res.status_code}")
    
    if stats_res.status_code == 200:
        data = stats_res.json()
        print("\n✅ API返回的数据:")
        print(f"   success: {data.get('success')}")
        
        if data.get('success') and data.get('data'):
            summary = data['data']
            print(f"\n   竞赛名称: {summary.get('competitionName')}")
            print(f"   报名总数: {summary.get('registrationCount')}")
            
            print("\n   === 现有统计数据 ===")
            print(f"   地区分布 (regionCounts): {summary.get('regionCounts')}")
            print(f"   主题类型分布 (subjectTypeCounts): {summary.get('subjectTypeCounts')}")
            
            print("\n   === 新增数据检查 ===")
            # 检查可能的品管工具字段名
            for key in summary.keys():
                if 'method' in key.lower() or 'tool' in key.lower() or 'circle' in key.lower():
                    print(f"   🆕 {key}: {summary.get(key)}")
            
            print("\n   === 所有字段 ===")
            for key in sorted(summary.keys()):
                print(f"   - {key}: {type(summary.get(key)).__name__}")
        else:
            print("   ❌ 数据为空")
    else:
        print(f"   ❌ 请求失败: {stats_res.text}")
else:
    print(f"   ❌ 登录失败: {login_res.text}")

print("=" * 60)
