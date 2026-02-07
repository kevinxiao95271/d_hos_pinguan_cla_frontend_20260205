#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动分组API - 诊断400错误
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_auto_group():
    """测试自动分组API"""
    print("=" * 80)
    print("测试自动分组API - 诊断400错误")
    print("=" * 80)
    
    # 1. 登录
    print("\n[1] 登录组委会账号...")
    login_data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Admin",
        "role": "COMMITTEE_ADMIN"
    }
    
    try:
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=10
        )
        login_resp.raise_for_status()
        login_result = login_resp.json()
        
        if not login_result.get('success'):
            print(f"[ERROR] 登录失败")
            return
        
        token = login_result['data']['token']
        print(f"[OK] 登录成功！")
        
    except Exception as e:
        print(f"[ERROR] 登录异常: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. 测试不同的参数组合
    print("\n[2] 测试自动分组API...")
    
    test_cases = [
        {
            "name": "只有 competitionId",
            "data": {"competitionId": 21}
        },
        {
            "name": "competitionId + groupPrefix",
            "data": {"competitionId": 21, "groupPrefix": "A"}
        },
        {
            "name": "competitionId + groupSize",
            "data": {"competitionId": 21, "groupSize": 10}
        },
        {
            "name": "完整参数",
            "data": {"competitionId": 21, "groupPrefix": "A", "groupSize": 10}
        }
    ]
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n测试 #{idx}: {test_case['name']}")
        print(f"  参数: {json.dumps(test_case['data'], ensure_ascii=False)}")
        
        try:
            resp = requests.post(
                f"{BASE_URL}/api/admin/registrations/auto-group",
                headers=headers,
                json=test_case['data'],
                timeout=10
            )
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"  [OK] 成功！状态码: {resp.status_code}")
                print(f"  响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                break  # 找到成功的参数组合就停止
            else:
                print(f"  [FAIL] 失败！状态码: {resp.status_code}")
                try:
                    error_msg = resp.json()
                    print(f"  错误信息: {json.dumps(error_msg, ensure_ascii=False)}")
                except:
                    print(f"  错误信息: {resp.text}")
                    
        except Exception as e:
            print(f"  [ERROR] 异常: {e}")
    
    # 3. 查看Swagger文档建议
    print("\n" + "=" * 80)
    print("[3] 修复建议")
    print("=" * 80)
    print("""
请检查后端Swagger文档：
http://localhost:6031/swagger-ui/index.html

搜索: POST /admin/registrations/auto-group

查看必需参数：
- competitionId: 赛事ID (必需)
- groupPrefix: 分组前缀，如 "A", "B" (可能必需)
- groupSize: 每组人数 (可能必需)

常见错误原因：
1. 缺少必需参数
2. 参数类型错误
3. competitionId 不存在
4. 没有可分组的报名数据
""")

if __name__ == '__main__':
    test_auto_group()
