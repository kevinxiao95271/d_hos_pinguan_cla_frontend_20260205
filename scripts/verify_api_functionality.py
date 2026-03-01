#!/usr/bin/env python3
"""验证优化后的API功能是否符合前端预期"""
import requests
import json

BASE_URL = "http://localhost:6031/api"
TIMEOUT = 30

def login():
    """登录"""
    url = f"{BASE_URL}/auth/login-with-password"
    data = {"phone": "13800000005", "password": "ops2026"}
    
    response = requests.post(url, json=data, timeout=TIMEOUT)
    result = response.json()
    
    if result.get('success'):
        return result['data']['token'], result['data'].get('currentCompetitionId', 1)
    return None, None

def verify_api(name, url, params, headers, expected_structure):
    """验证API返回的数据结构"""
    print(f"\n{'=' * 80}")
    print(f"验证: {name}")
    print(f"{'=' * 80}")
    print(f"URL: {url}")
    print(f"参数: {json.dumps(params, ensure_ascii=False)}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            return False
        
        result = response.json()
        
        if not result.get('success'):
            print(f"❌ API返回失败: {result.get('message')}")
            return False
        
        data = result.get('data')
        print(f"✅ API调用成功")
        print(f"\n返回数据类型: {type(data).__name__}")
        
        # 检查数据结构
        issues = []
        
        if isinstance(data, list):
            print(f"数据量: {len(data)} 条")
            if len(data) > 0:
                sample = data[0]
                print(f"\n示例数据字段:")
                for key in sample.keys():
                    print(f"  - {key}: {type(sample[key]).__name__}")
                
                # 检查必需字段
                for field in expected_structure.get('required_fields', []):
                    if field not in sample:
                        issues.append(f"缺少必需字段: {field}")
                
        elif isinstance(data, dict):
            print(f"数据字段:")
            for key, value in data.items():
                print(f"  - {key}: {type(value).__name__}")
            
            # 检查必需字段
            for field in expected_structure.get('required_fields', []):
                if field not in data:
                    issues.append(f"缺少必需字段: {field}")
        
        # 报告问题
        if issues:
            print(f"\n⚠️  发现问题:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"\n✅ 数据结构符合预期")
            return True
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def main():
    print("=" * 80)
    print("API功能验证 - 检查数据结构是否符合前端预期")
    print("=" * 80)
    
    # 登录
    token, competition_id = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print(f"✅ 登录成功 (赛事ID: {competition_id})")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = []
    
    # 1. 评审任务列表
    # 前端期望: 数组，每个元素包含 registrationId, reviewerId
    result1 = verify_api(
        name="评审任务列表 (getAdminReviewTasks)",
        url=f"{BASE_URL}/admin/reviews/tasks",
        params={'competitionId': competition_id, 'stage': 'BOOK'},
        headers=headers,
        expected_structure={
            'required_fields': ['registrationId', 'reviewerId']
        }
    )
    results.append(('评审任务列表', result1))
    
    # 2. 统计汇总
    # 前端期望: 对象，包含 totalRegistrations, pendingReviews, completedReviews 等
    result2 = verify_api(
        name="统计汇总 (getStatsSummary)",
        url=f"{BASE_URL}/admin/stats/summary",
        params={'competitionId': competition_id},
        headers=headers,
        expected_structure={
            'required_fields': ['competitionId', 'registrationCount']
        }
    )
    results.append(('统计汇总', result2))
    
    # 3. 评审汇总 - 评委端
    result3 = verify_api(
        name="评审汇总 - 评委端 (reviews/summary)",
        url=f"{BASE_URL}/reviews/summary",
        params={'competitionId': competition_id, 'stage': 'BOOK'},
        headers=headers,
        expected_structure={
            'required_fields': []
        }
    )
    results.append(('评审汇总-评委端', result3))
    
    # 4. 评审汇总 - 管理端
    result4 = verify_api(
        name="评审汇总 - 管理端 (admin/reviews/summary)",
        url=f"{BASE_URL}/admin/reviews/summary",
        params={'competitionId': competition_id, 'stage': 'BOOK'},
        headers=headers,
        expected_structure={
            'required_fields': []
        }
    )
    results.append(('评审汇总-管理端', result4))
    
    # 5. 专家意见反馈
    result5 = verify_api(
        name="专家意见反馈 (admin/reviews/feedback)",
        url=f"{BASE_URL}/admin/reviews/feedback",
        params={'competitionId': competition_id, 'stage': 'BOOK'},
        headers=headers,
        expected_structure={
            'required_fields': []
        }
    )
    results.append(('专家意见反馈', result5))
    
    # 6. 我的报名
    result6 = verify_api(
        name="我的报名列表 (registrations/my)",
        url=f"{BASE_URL}/registrations/my",
        params={'competitionId': competition_id},
        headers=headers,
        expected_structure={
            'required_fields': []
        }
    )
    results.append(('我的报名', result6))
    
    # 汇总
    print(f"\n{'=' * 80}")
    print("验证汇总")
    print(f"{'=' * 80}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {total} 个API")
    print(f"通过: {passed} 个")
    print(f"失败: {total - passed} 个")
    
    print(f"\n详细结果:")
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name:<25} {status}")
    
    if passed == total:
        print(f"\n✅ 所有API功能验证通过！")
    else:
        print(f"\n⚠️  部分API需要调整")

if __name__ == "__main__":
    main()
