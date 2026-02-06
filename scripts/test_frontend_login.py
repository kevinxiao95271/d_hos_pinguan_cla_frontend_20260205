#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端登录 - 验证真实评审专家账号
"""

import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031/api"

def test_login(phone, name, title="评委", role="REVIEWER"):
    """测试登录"""
    print(f"\n{'='*60}")
    print(f"测试登录: {name} ({phone})")
    print(f"{'='*60}")
    
    # 模拟前端登录请求
    login_data = {
        "phone": phone,
        "name": name,
        "title": title,
        "role": role,
        "reviewerGroupCode": "A1",
        "interviewGroupCode": "A1",
        "expertBackground": "MEDICAL"
    }
    
    print(f"请求参数:")
    print(json.dumps(login_data, ensure_ascii=False, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            timeout=30
        )
        
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('data', {}).get('token')
                user_id = result.get('data', {}).get('userId')
                user_role = result.get('data', {}).get('role')
                print(f"✅ 登录成功")
                print(f"   userId: {user_id}")
                print(f"   role: {user_role}")
                print(f"   token: {token[:50]}...")
                return True, token, user_id
            else:
                print(f"❌ 登录失败: {result.get('message')}")
                return False, None, None
        else:
            print(f"❌ 请求失败: {response.text}")
            return False, None, None
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False, None, None

def main():
    print("\n" + "="*60)
    print("  前端登录测试 - 评审专家账号")
    print("="*60)
    
    # 测试用户提供的两个评审专家账号
    accounts = [
        {"phone": "13800000021", "name": "李明华", "title": "主任医师"},
        {"phone": "13800002004", "name": "孙丽娟", "title": "副主任护师"},
        {"phone": "13800000021", "name": "Reviewer A", "title": "评委"},  # 原测试账号
        {"phone": "13800000022", "name": "Reviewer B", "title": "评委"},
    ]
    
    results = []
    
    for acc in accounts:
        success, token, user_id = test_login(
            acc["phone"], 
            acc["name"], 
            acc.get("title", "评委")
        )
        results.append({
            "phone": acc["phone"],
            "name": acc["name"],
            "success": success,
            "token": token,
            "userId": user_id
        })
    
    # 总结
    print("\n\n" + "="*60)
    print("  📊 测试结果总结")
    print("="*60)
    
    success_count = sum(1 for r in results if r["success"])
    print(f"\n成功: {success_count}/{len(results)}\n")
    
    print("详细结果:")
    print("-" * 60)
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"{status} {r['name']:<12} ({r['phone']})")
        if r["success"]:
            print(f"   userId: {r['userId']}")
    
    # 给出前端配置建议
    if success_count > 0:
        print("\n" + "="*60)
        print("  🔧 前端配置建议")
        print("="*60)
        print("\n需要在 src/views/Login.vue 的 testAccounts 中添加:\n")
        
        for r in results:
            if r["success"]:
                print(f"""  {{ 
    phone: '{r['phone']}', 
    name: '{r['name']}', 
    label: '{r['name']}', 
    role: 'REVIEWER', 
    institutionId: null 
  }},""")

if __name__ == "__main__":
    main()
