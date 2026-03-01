#!/usr/bin/env python3
"""测试后端优化后的API性能"""
import subprocess
import time
import json

BASE_URL = "http://localhost:6031/api"
TIMEOUT = 60

def run_git(args):
    """运行git命令"""
    cmd = ['git'] + args
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return result

def login():
    """登录获取token"""
    import requests
    
    print("=" * 80)
    print("登录")
    print("=" * 80)
    
    url = f"{BASE_URL}/auth/login-with-password"
    data = {
        "phone": "13800000005",
        "password": "ops2026"
    }
    
    try:
        response = requests.post(url, json=data, timeout=TIMEOUT)
        result = response.json()
        
        if result.get('success'):
            token = result['data']['token']
            competition_id = result['data'].get('currentCompetitionId', 1)
            print(f"✅ 登录成功")
            print(f"   赛事ID: {competition_id}")
            return token, competition_id
        else:
            print(f"❌ 登录失败: {result.get('message')}")
            return None, None
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return None, None

def test_api(name, url, params, headers, priority="P1"):
    """测试单个API"""
    import requests
    
    print(f"\n{'=' * 80}")
    print(f"[{priority}] {name}")
    print(f"{'=' * 80}")
    print(f"URL: GET {url}")
    print(f"参数: {json.dumps(params, ensure_ascii=False)}")
    print(f"⏱️  开始计时...")
    
    start_time = time.time()
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
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
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                data = result.get('data')
                
                # 分析数据结构
                if isinstance(data, list):
                    data_count = len(data)
                    print(f"✅ 成功 - 返回 {data_count} 条数据")
                elif isinstance(data, dict):
                    if 'content' in data:
                        data_count = len(data['content'])
                        total = data.get('totalElements', 'N/A')
                        print(f"✅ 成功 - 返回 {data_count} 条数据 (总计: {total})")
                    else:
                        print(f"✅ 成功 - 返回对象数据")
                        print(f"   数据键: {list(data.keys())[:5]}...")
                else:
                    print(f"✅ 成功")
                
                return {
                    'name': name,
                    'priority': priority,
                    'elapsed_time': elapsed_time,
                    'status_code': response.status_code,
                    'success': True
                }
            else:
                print(f"❌ 失败: {result.get('message')}")
                return {
                    'name': name,
                    'priority': priority,
                    'elapsed_time': elapsed_time,
                    'status_code': response.status_code,
                    'success': False,
                    'error': result.get('message')
                }
        else:
            print(f"❌ HTTP错误")
            print(f"响应: {response.text[:200]}")
            return {
                'name': name,
                'priority': priority,
                'elapsed_time': elapsed_time,
                'status_code': response.status_code,
                'success': False
            }
            
    except requests.Timeout:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"⏱️  超时: {elapsed_time:.3f} 秒")
        print(f"❌ 请求超时 (超过 {TIMEOUT} 秒)")
        return {
            'name': name,
            'priority': priority,
            'elapsed_time': elapsed_time,
            'success': False,
            'timeout': True
        }
        
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"⏱️  耗时: {elapsed_time:.3f} 秒")
        print(f"❌ 异常: {str(e)}")
        return {
            'name': name,
            'priority': priority,
            'elapsed_time': elapsed_time,
            'success': False,
            'error': str(e)
        }

def main():
    import requests
    
    print("=" * 80)
    print("后端优化API性能测试")
    print("=" * 80)
    print("测试时间:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 80)
    
    # 登录
    token, competition_id = login()
    if not token:
        print("\n❌ 登录失败，无法继续测试")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = []
    
    # P1 优先级测试
    print("\n" + "=" * 80)
    print("P1 优先级 - 用户已反馈慢的接口")
    print("=" * 80)
    
    # 1. GET /api/admin/reviews/tasks（评委分配）
    result1 = test_api(
        name="评委分配 - 评审任务列表",
        url=f"{BASE_URL}/admin/reviews/tasks",
        params={
            'competitionId': competition_id,
            'stage': 'BOOK'
        },
        headers=headers,
        priority="P1"
    )
    results.append(result1)
    
    # 2. GET /api/admin/stats/summary（统计汇总）
    result2 = test_api(
        name="统计汇总 - Dashboard数据",
        url=f"{BASE_URL}/admin/stats/summary",
        params={
            'competitionId': competition_id
        },
        headers=headers,
        priority="P1"
    )
    results.append(result2)
    
    # P2 优先级测试
    print("\n" + "=" * 80)
    print("P2 优先级 - 中等影响的接口")
    print("=" * 80)
    
    # 3. GET /api/reviews/summary（评审汇总）
    result3 = test_api(
        name="评审汇总 - 评委端",
        url=f"{BASE_URL}/reviews/summary",
        params={
            'competitionId': competition_id,
            'stage': 'BOOK'
        },
        headers=headers,
        priority="P2"
    )
    results.append(result3)
    
    # 4. GET /api/admin/reviews/summary（评审汇总 - 管理端）
    result4 = test_api(
        name="评审汇总 - 管理端",
        url=f"{BASE_URL}/admin/reviews/summary",
        params={
            'competitionId': competition_id,
            'stage': 'BOOK'
        },
        headers=headers,
        priority="P2"
    )
    results.append(result4)
    
    # 5. GET /api/admin/reviews/feedback（专家意见）
    result5 = test_api(
        name="专家意见反馈",
        url=f"{BASE_URL}/admin/reviews/feedback",
        params={
            'competitionId': competition_id,
            'stage': 'BOOK'
        },
        headers=headers,
        priority="P2"
    )
    results.append(result5)
    
    # P3 优先级测试
    print("\n" + "=" * 80)
    print("P3 优先级 - 影响较小的接口")
    print("=" * 80)
    
    # 6. GET /api/registrations/my（我的报名）
    result6 = test_api(
        name="我的报名列表",
        url=f"{BASE_URL}/registrations/my",
        params={
            'competitionId': competition_id
        },
        headers=headers,
        priority="P3"
    )
    results.append(result6)
    
    # 汇总报告
    print("\n" + "=" * 80)
    print("测试汇总")
    print("=" * 80)
    
    print(f"\n{'优先级':<8} {'接口名称':<30} {'响应时间':<20} {'状态':<10}")
    print("-" * 80)
    
    for result in results:
        elapsed = result['elapsed_time']
        status = "✅ 成功" if result['success'] else "❌ 失败"
        priority = result['priority']
        
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
        
        print(f"{priority:<8} {result['name']:<30} {perf_mark} {elapsed:>6.3f}秒 ({elapsed*1000:>5.0f}ms)  {status:<10}")
    
    # 按优先级统计
    print("\n" + "=" * 80)
    print("按优先级统计")
    print("=" * 80)
    
    for priority in ['P1', 'P2', 'P3']:
        priority_results = [r for r in results if r['priority'] == priority and r['success']]
        if priority_results:
            times = [r['elapsed_time'] for r in priority_results]
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            print(f"\n{priority} 优先级:")
            print(f"  测试数量: {len(priority_results)}")
            print(f"  平均响应时间: {avg_time:.3f} 秒")
            print(f"  最快: {min_time:.3f} 秒")
            print(f"  最慢: {max_time:.3f} 秒")
            
            # 评估
            if avg_time < 0.5:
                print(f"  评估: ✅ 优秀")
            elif avg_time < 1.0:
                print(f"  评估: 🟡 良好")
            elif avg_time < 2.0:
                print(f"  评估: 🟠 一般")
            else:
                print(f"  评估: 🔴 需要优化")
    
    # 总体评估
    successful = [r for r in results if r['success']]
    if successful:
        times = [r['elapsed_time'] for r in successful]
        avg_time = sum(times) / len(times)
        
        print("\n" + "=" * 80)
        print("总体评估")
        print("=" * 80)
        print(f"总测试数: {len(results)}")
        print(f"成功数: {len(successful)}")
        print(f"失败数: {len(results) - len(successful)}")
        print(f"平均响应时间: {avg_time:.3f} 秒")
        
        # 性能分布
        excellent = len([t for t in times if t < 0.5])
        good = len([t for t in times if 0.5 <= t < 1.0])
        ok = len([t for t in times if 1.0 <= t < 2.0])
        slow = len([t for t in times if t >= 2.0])
        
        print(f"\n性能分布:")
        print(f"  🟢 优秀 (< 0.5秒): {excellent} 个 ({excellent/len(successful)*100:.1f}%)")
        print(f"  🟡 良好 (0.5-1.0秒): {good} 个 ({good/len(successful)*100:.1f}%)")
        print(f"  🟠 一般 (1.0-2.0秒): {ok} 个 ({ok/len(successful)*100:.1f}%)")
        print(f"  🔴 较慢 (>= 2.0秒): {slow} 个 ({slow/len(successful)*100:.1f}%)")
        
        if avg_time < 0.5:
            print(f"\n✅ 整体性能优秀！")
        elif avg_time < 1.0:
            print(f"\n🟡 整体性能良好")
        elif avg_time < 2.0:
            print(f"\n🟠 整体性能一般，建议继续优化")
        else:
            print(f"\n🔴 整体性能较慢，需要优化")

if __name__ == "__main__":
    main()
