#!/usr/bin/env python3
"""步骤2: 测试书审分组API - 无筛选条件"""
import requests
import json
import time

BASE_URL = "http://localhost:6031/api"
TIMEOUT = 60  # 60秒超时

print("=" * 80)
print("步骤2: 测试书审分组API - 无筛选条件")
print("=" * 80)

# 先登录
print("\n1. 登录...")
login_url = f"{BASE_URL}/auth/login-with-password"
login_data = {
    "phone": "13800000005",
    "password": "ops2026"
}

try:
    response = requests.post(login_url, json=login_data, timeout=TIMEOUT)
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 登录失败: {result.get('message')}")
        exit(1)
    
    token = result['data']['token']
    competition_id = result['data'].get('currentCompetitionId', 1)
    print(f"✅ 登录成功")
    print(f"   赛事ID: {competition_id}")
    
except Exception as e:
    print(f"❌ 登录异常: {str(e)}")
    exit(1)

# 测试书审分组API - 无筛选条件
print("\n2. 测试书审分组API (无筛选条件)...")
print("-" * 80)

api_url = f"{BASE_URL}/admin/registrations/filter"
params = {
    'competitionId': competition_id,
    'page': 0,
    'size': 50
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print(f"请求URL: GET {api_url}")
print(f"参数: {json.dumps(params, ensure_ascii=False, indent=2)}")
print(f"\n⏱️  开始计时...")

start_time = time.time()

try:
    response = requests.get(api_url, params=params, headers=headers, timeout=TIMEOUT)
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"⏱️  响应时间: {elapsed_time:.3f} 秒 ({elapsed_time * 1000:.0f} 毫秒)")
    
    # 性能评级
    if elapsed_time < 0.5:
        rating = "🟢 优秀"
    elif elapsed_time < 1.0:
        rating = "🟡 良好"
    elif elapsed_time < 2.0:
        rating = "🟠 一般"
    elif elapsed_time < 5.0:
        rating = "🔴 较慢"
    else:
        rating = "⚫ 很慢"
    
    print(f"性能评级: {rating}")
    print(f"\n状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('success'):
            data = result.get('data')
            
            print(f"✅ 请求成功")
            
            # 分析数据结构
            if isinstance(data, list):
                print(f"\n数据格式: 数组")
                print(f"数据量: {len(data)} 条记录")
                
                if len(data) > 0:
                    sample = data[0]
                    print(f"\n数据字段 ({len(sample.keys())} 个):")
                    for key in sample.keys():
                        print(f"  - {key}")
                    
                    print(f"\n示例数据:")
                    print(f"  项目编号: {sample.get('registrationId', 'N/A')}")
                    print(f"  项目名称: {sample.get('projectName', 'N/A')}")
                    print(f"  机构名称: {sample.get('institutionName', 'N/A')}")
                    print(f"  竞赛组别: {sample.get('groupType', 'N/A')}")
                    print(f"  分组: {sample.get('groupCode', 'N/A')}")
                    
            elif isinstance(data, dict) and 'content' in data:
                print(f"\n数据格式: 分页对象")
                print(f"当前页数据: {len(data['content'])} 条")
                print(f"总记录数: {data.get('totalElements', 'N/A')}")
                print(f"总页数: {data.get('totalPages', 'N/A')}")
                print(f"当前页码: {data.get('number', 'N/A')}")
                print(f"每页大小: {data.get('size', 'N/A')}")
                
                if len(data['content']) > 0:
                    sample = data['content'][0]
                    print(f"\n数据字段 ({len(sample.keys())} 个):")
                    for key in sample.keys():
                        print(f"  - {key}")
                    
                    print(f"\n示例数据:")
                    print(f"  项目编号: {sample.get('registrationId', 'N/A')}")
                    print(f"  项目名称: {sample.get('projectName', 'N/A')}")
                    print(f"  机构名称: {sample.get('institutionName', 'N/A')}")
                    print(f"  竞赛组别: {sample.get('groupType', 'N/A')}")
                    print(f"  分组: {sample.get('groupCode', 'N/A')}")
            
            # 性能分析
            print(f"\n" + "=" * 80)
            print("性能分析:")
            print("=" * 80)
            
            if elapsed_time > 5.0:
                print(f"⚠️  响应时间超过5秒，严重影响用户体验")
                print(f"\n建议:")
                print(f"  1. 🔍 检查数据库查询是否有全表扫描")
                print(f"  2. 📊 为 competitionId 字段添加索引")
                print(f"  3. 💾 考虑使用Redis缓存热点数据")
                print(f"  4. 🔄 检查是否有N+1查询问题")
                print(f"  5. 📦 减少返回字段，只返回必要数据")
            elif elapsed_time > 2.0:
                print(f"⚠️  响应时间超过2秒，用户体验一般")
                print(f"\n建议:")
                print(f"  1. 优化数据库查询")
                print(f"  2. 添加必要的索引")
                print(f"  3. 考虑分页优化")
            elif elapsed_time > 1.0:
                print(f"✅ 响应时间可接受，但仍有优化空间")
            else:
                print(f"✅ 响应时间优秀，性能良好")
                
        else:
            print(f"❌ 请求失败: {result.get('message')}")
    else:
        print(f"❌ HTTP错误")
        print(f"响应: {response.text[:500]}")
        
except requests.Timeout:
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"⏱️  超时时间: {elapsed_time:.3f} 秒")
    print(f"❌ 请求超时 (超过 {TIMEOUT} 秒)")
    print(f"\n这表明API响应非常慢，严重影响用户体验")
    print(f"必须进行性能优化！")
    
except Exception as e:
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"⏱️  耗时: {elapsed_time:.3f} 秒")
    print(f"❌ 异常: {str(e)}")
