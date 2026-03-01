#!/usr/bin/env python3
"""步骤4: 测试面谈分组API (进阶组)"""
import requests
import json
import time

BASE_URL = "http://localhost:6031/api"
TIMEOUT = 60

print("=" * 80)
print("步骤4: 测试面谈分组API (进阶组)")
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
    
except Exception as e:
    print(f"❌ 登录异常: {str(e)}")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

api_url = f"{BASE_URL}/admin/registrations/filter"

# 测试场景列表 - 面谈分组固定为进阶组
test_cases = [
    {
        "name": "进阶组无筛选",
        "params": {
            'competitionId': competition_id,
            'groupType': 'ADVANCED',
            'page': 0,
            'size': 50
        }
    },
    {
        "name": "进阶组按分组筛选 (C1)",
        "params": {
            'competitionId': competition_id,
            'groupType': 'ADVANCED',
            'groupCode': 'C1',
            'page': 0,
            'size': 50
        }
    },
    {
        "name": "进阶组按机构筛选",
        "params": {
            'competitionId': competition_id,
            'groupType': 'ADVANCED',
            'institutionName': '医院',
            'page': 0,
            'size': 50
        }
    },
    {
        "name": "进阶组多条件筛选",
        "params": {
            'competitionId': competition_id,
            'groupType': 'ADVANCED',
            'groupCode': 'C1',
            'institutionName': '医院',
            'page': 0,
            'size': 50
        }
    }
]

results = []

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{i}. {test_case['name']}")
    print("-" * 80)
    print(f"参数: {json.dumps(test_case['params'], ensure_ascii=False)}")
    print(f"⏱️  开始计时...")
    
    start_time = time.time()
    
    try:
        response = requests.get(api_url, params=test_case['params'], headers=headers, timeout=TIMEOUT)
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
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                data = result.get('data')
                
                if isinstance(data, list):
                    data_count = len(data)
                    print(f"数据量: {data_count} 条")
                elif isinstance(data, dict) and 'content' in data:
                    data_count = len(data['content'])
                    total = data.get('totalElements', 'N/A')
                    print(f"数据量: {data_count} 条 (总计: {total})")
                else:
                    data_count = 0
                
                print(f"✅ 成功")
                
                results.append({
                    'name': test_case['name'],
                    'elapsed_time': elapsed_time,
                    'data_count': data_count,
                    'success': True
                })
            else:
                print(f"❌ 失败: {result.get('message')}")
                results.append({
                    'name': test_case['name'],
                    'elapsed_time': elapsed_time,
                    'success': False
                })
        else:
            print(f"❌ HTTP {response.status_code}")
            results.append({
                'name': test_case['name'],
                'elapsed_time': elapsed_time,
                'success': False
            })
            
    except requests.Timeout:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"⏱️  超时: {elapsed_time:.3f} 秒")
        print(f"❌ 请求超时")
        results.append({
            'name': test_case['name'],
            'elapsed_time': elapsed_time,
            'success': False,
            'timeout': True
        })
        
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"⏱️  耗时: {elapsed_time:.3f} 秒")
        print(f"❌ 异常: {str(e)}")
        results.append({
            'name': test_case['name'],
            'elapsed_time': elapsed_time,
            'success': False
        })

# 汇总
print(f"\n" + "=" * 80)
print("测试汇总")
print("=" * 80)

print(f"\n{'测试场景':<30} {'响应时间':<20} {'状态':<10}")
print("-" * 80)

for result in results:
    elapsed = result['elapsed_time']
    status = "✅ 成功" if result['success'] else "❌ 失败"
    
    # 性能标记
    if elapsed < 0.5:
        perf_mark = "🟢"
    elif elapsed < 1.0:
        perf_mark = "🟡"
    elif elapsed < 2.0:
        perf_mark = "🟠"
    elif elapsed < 5.0:
        perf_mark = "🔴"
    else:
        perf_mark = "⚫"
    
    print(f"{result['name']:<30} {perf_mark} {elapsed:>6.3f}秒 ({elapsed*1000:>5.0f}ms)  {status:<10}")

# 统计
successful = [r for r in results if r['success']]
if successful:
    times = [r['elapsed_time'] for r in successful]
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    
    print(f"\n统计:")
    print(f"  平均响应时间: {avg_time:.3f} 秒")
    print(f"  最快: {min_time:.3f} 秒")
    print(f"  最慢: {max_time:.3f} 秒")
