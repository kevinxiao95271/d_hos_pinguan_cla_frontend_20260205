#!/usr/bin/env python3
"""
测试书审分组和面谈分组页面的API性能
测量不同筛选条件下的响应时间
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:6031/api"

# 设置更长的超时时间
TIMEOUT = 30  # 30秒超时

def login():
    """使用委员会账号登录"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "phone": "13800000003",
        "password": "committee2026"
    }
    
    print("=" * 80)
    print("登录委员会账号")
    print("=" * 80)
    
    response = requests.post(url, json=data, timeout=TIMEOUT)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            token = result['data']['token']
            print(f"✅ 登录成功")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print(f"❌ 登录失败: {result.get('message')}")
            return None
    else:
        print(f"❌ 请求失败: {response.text}")
        return None

def test_api_performance(token, test_name, url, params, description):
    """测试API性能"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n" + "=" * 80)
    print(f"测试: {test_name}")
    print("=" * 80)
    print(f"描述: {description}")
    print(f"URL: GET {url}")
    print(f"参数: {json.dumps(params, ensure_ascii=False, indent=2)}")
    
    # 记录开始时间
    start_time = time.time()
    start_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        
        # 记录结束时间
        end_time = time.time()
        end_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        elapsed_time = end_time - start_time
        
        print(f"\n⏱️  性能指标:")
        print(f"  开始时间: {start_datetime}")
        print(f"  结束时间: {end_datetime}")
        print(f"  响应时间: {elapsed_time:.3f} 秒 ({elapsed_time * 1000:.0f} 毫秒)")
        
        # 性能评级
        if elapsed_time < 0.5:
            rating = "🟢 优秀"
        elif elapsed_time < 1.0:
            rating = "🟡 良好"
        elif elapsed_time < 2.0:
            rating = "🟠 一般"
        else:
            rating = "🔴 较慢"
        
        print(f"  性能评级: {rating}")
        
        print(f"\n📊 响应信息:")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                data = result.get('data')
                
                # 分析数据结构
                if isinstance(data, list):
                    print(f"  ✅ 请求成功")
                    print(f"  数据类型: 数组")
                    print(f"  数据量: {len(data)} 条记录")
                    
                    if len(data) > 0:
                        sample = data[0]
                        print(f"  数据字段: {list(sample.keys())}")
                        
                elif isinstance(data, dict):
                    print(f"  ✅ 请求成功")
                    print(f"  数据类型: 对象")
                    
                    if 'content' in data:
                        # 分页格式
                        print(f"  分页格式: 是")
                        print(f"  当前页数据: {len(data['content'])} 条")
                        print(f"  总记录数: {data.get('totalElements', 'N/A')}")
                        print(f"  总页数: {data.get('totalPages', 'N/A')}")
                        print(f"  当前页码: {data.get('number', 'N/A')}")
                        print(f"  每页大小: {data.get('size', 'N/A')}")
                        
                        if len(data['content']) > 0:
                            sample = data['content'][0]
                            print(f"  数据字段: {list(sample.keys())}")
                    else:
                        print(f"  对象键: {list(data.keys())}")
                else:
                    print(f"  数据类型: {type(data)}")
                    print(f"  数据: {data}")
                
                # 性能建议
                print(f"\n💡 性能建议:")
                if elapsed_time > 2.0:
                    print(f"  ⚠️  响应时间超过2秒，建议优化:")
                    print(f"     1. 检查是否需要添加数据库索引")
                    print(f"     2. 考虑减少返回字段")
                    print(f"     3. 使用分页减少单次数据量")
                    print(f"     4. 检查是否有N+1查询问题")
                elif elapsed_time > 1.0:
                    print(f"  ⚠️  响应时间超过1秒，可以进一步优化")
                else:
                    print(f"  ✅ 响应时间良好")
                
                return {
                    'success': True,
                    'elapsed_time': elapsed_time,
                    'status_code': response.status_code,
                    'data_count': len(data) if isinstance(data, list) else (len(data.get('content', [])) if isinstance(data, dict) and 'content' in data else 0),
                    'total_elements': data.get('totalElements') if isinstance(data, dict) else None
                }
            else:
                print(f"  ❌ 请求失败: {result.get('message')}")
                return {
                    'success': False,
                    'elapsed_time': elapsed_time,
                    'status_code': response.status_code,
                    'error': result.get('message')
                }
        else:
            print(f"  ❌ HTTP错误")
            print(f"  响应: {response.text[:500]}")
            return {
                'success': False,
                'elapsed_time': elapsed_time,
                'status_code': response.status_code,
                'error': response.text[:200]
            }
            
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"  ❌ 异常: {str(e)}")
        print(f"  耗时: {elapsed_time:.3f} 秒")
        return {
            'success': False,
            'elapsed_time': elapsed_time,
            'error': str(e)
        }

def main():
    print("书审分组和面谈分组页面 - API性能测试")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 登录
    token = login()
    if not token:
        print("\n❌ 登录失败，无法继续测试")
        return
    
    # 获取当前赛事ID（假设为1，实际应该从API获取）
    competition_id = 1
    
    url = f"{BASE_URL}/admin/registrations/filter"
    
    results = []
    
    # ========================================
    # 书审分组页面测试
    # ========================================
    print("\n" + "=" * 80)
    print("📋 书审分组页面 (src/views/committee/book/Registration.vue)")
    print("=" * 80)
    
    # 测试1: 无筛选条件（最慢场景）
    result1 = test_api_performance(
        token=token,
        test_name="书审分组 - 无筛选条件",
        url=url,
        params={
            'competitionId': competition_id,
            'page': 0,
            'size': 50
        },
        description="加载所有报名数据，无任何筛选条件（最常见场景）"
    )
    results.append(('书审分组-无筛选', result1))
    
    # 测试2: 按竞赛组别筛选
    result2 = test_api_performance(
        token=token,
        test_name="书审分组 - 按竞赛组别筛选",
        url=url,
        params={
            'competitionId': competition_id,
            'groupType': 'BASIC',
            'page': 0,
            'size': 50
        },
        description="筛选基层组数据"
    )
    results.append(('书审分组-组别筛选', result2))
    
    # 测试3: 按分组筛选
    result3 = test_api_performance(
        token=token,
        test_name="书审分组 - 按分组筛选",
        url=url,
        params={
            'competitionId': competition_id,
            'groupType': 'BASIC',
            'groupCode': 'A1',
            'page': 0,
            'size': 50
        },
        description="筛选基层组A1分组数据"
    )
    results.append(('书审分组-分组筛选', result3))
    
    # 测试4: 按机构名称筛选
    result4 = test_api_performance(
        token=token,
        test_name="书审分组 - 按机构名称筛选",
        url=url,
        params={
            'competitionId': competition_id,
            'institutionName': '医院',
            'page': 0,
            'size': 50
        },
        description="模糊搜索机构名称包含'医院'的数据"
    )
    results.append(('书审分组-机构筛选', result4))
    
    # 测试5: 多条件组合筛选
    result5 = test_api_performance(
        token=token,
        test_name="书审分组 - 多条件组合筛选",
        url=url,
        params={
            'competitionId': competition_id,
            'groupType': 'BASIC',
            'groupCode': 'A1',
            'institutionName': '医院',
            'page': 0,
            'size': 50
        },
        description="组合筛选：基层组 + A1分组 + 机构名称"
    )
    results.append(('书审分组-组合筛选', result5))
    
    # ========================================
    # 面谈分组页面测试
    # ========================================
    print("\n" + "=" * 80)
    print("📋 面谈分组页面 (src/views/committee/interview/Group.vue)")
    print("=" * 80)
    
    # 测试6: 进阶组无筛选
    result6 = test_api_performance(
        token=token,
        test_name="面谈分组 - 进阶组无筛选",
        url=url,
        params={
            'competitionId': competition_id,
            'groupType': 'ADVANCED',
            'page': 0,
            'size': 50
        },
        description="加载所有进阶组数据（面谈分组固定为进阶组）"
    )
    results.append(('面谈分组-无筛选', result6))
    
    # 测试7: 进阶组按分组筛选
    result7 = test_api_performance(
        token=token,
        test_name="面谈分组 - 按分组筛选",
        url=url,
        params={
            'competitionId': competition_id,
            'groupType': 'ADVANCED',
            'groupCode': 'C1',
            'page': 0,
            'size': 50
        },
        description="筛选进阶组C1分组数据"
    )
    results.append(('面谈分组-分组筛选', result7))
    
    # 测试8: 进阶组按品管工具筛选
    result8 = test_api_performance(
        token=token,
        test_name="面谈分组 - 按品管工具筛选",
        url=url,
        params={
            'competitionId': competition_id,
            'groupType': 'ADVANCED',
            'methodCode': 'QCC',
            'page': 0,
            'size': 50
        },
        description="筛选进阶组使用QCC品管工具的数据"
    )
    results.append(('面谈分组-工具筛选', result8))
    
    # 测试9: 进阶组多条件筛选
    result9 = test_api_performance(
        token=token,
        test_name="面谈分组 - 多条件筛选",
        url=url,
        params={
            'competitionId': competition_id,
            'groupType': 'ADVANCED',
            'groupCode': 'C1',
            'institutionName': '医院',
            'methodCode': 'QCC',
            'page': 0,
            'size': 50
        },
        description="组合筛选：进阶组 + C1分组 + 机构名称 + 品管工具"
    )
    results.append(('面谈分组-组合筛选', result9))
    
    # ========================================
    # 性能汇总
    # ========================================
    print("\n" + "=" * 80)
    print("📊 性能测试汇总")
    print("=" * 80)
    
    print(f"\n{'测试场景':<25} {'响应时间':<15} {'状态':<10} {'数据量':<10}")
    print("-" * 80)
    
    for name, result in results:
        if result['success']:
            elapsed = result['elapsed_time']
            status = "✅ 成功"
            data_count = result.get('data_count', 'N/A')
            
            # 性能标记
            if elapsed < 0.5:
                perf_mark = "🟢"
            elif elapsed < 1.0:
                perf_mark = "🟡"
            elif elapsed < 2.0:
                perf_mark = "🟠"
            else:
                perf_mark = "🔴"
            
            print(f"{name:<25} {perf_mark} {elapsed:>6.3f}秒 ({elapsed*1000:>5.0f}ms)  {status:<10} {data_count:<10}")
        else:
            print(f"{name:<25} {'❌ 失败':<15} {'失败':<10} {'-':<10}")
    
    # 统计分析
    successful_results = [r for _, r in results if r['success']]
    if successful_results:
        times = [r['elapsed_time'] for r in successful_results]
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print("\n" + "=" * 80)
        print("📈 统计分析")
        print("=" * 80)
        print(f"总测试数: {len(results)}")
        print(f"成功数: {len(successful_results)}")
        print(f"失败数: {len(results) - len(successful_results)}")
        print(f"\n响应时间统计:")
        print(f"  平均: {avg_time:.3f} 秒 ({avg_time * 1000:.0f} 毫秒)")
        print(f"  最快: {min_time:.3f} 秒 ({min_time * 1000:.0f} 毫秒)")
        print(f"  最慢: {max_time:.3f} 秒 ({max_time * 1000:.0f} 毫秒)")
        
        # 性能评估
        print(f"\n💡 性能评估:")
        if avg_time < 0.5:
            print(f"  ✅ 整体性能优秀，用户体验良好")
        elif avg_time < 1.0:
            print(f"  🟡 整体性能良好，可接受")
        elif avg_time < 2.0:
            print(f"  🟠 整体性能一般，建议优化")
        else:
            print(f"  🔴 整体性能较慢，需要优化")
        
        # 优化建议
        slow_tests = [(name, r) for name, r in results if r['success'] and r['elapsed_time'] > 1.0]
        if slow_tests:
            print(f"\n⚠️  慢查询场景 (>1秒):")
            for name, result in slow_tests:
                print(f"  - {name}: {result['elapsed_time']:.3f}秒")
            
            print(f"\n🔧 优化建议:")
            print(f"  1. 为常用筛选字段添加数据库索引 (competitionId, groupType, groupCode)")
            print(f"  2. 考虑使用Redis缓存热点数据")
            print(f"  3. 优化SQL查询，避免全表扫描")
            print(f"  4. 检查是否有N+1查询问题")
            print(f"  5. 考虑使用分页查询减少单次数据量")
            print(f"  6. 前端添加加载状态提示，改善用户体验")

if __name__ == "__main__":
    main()
