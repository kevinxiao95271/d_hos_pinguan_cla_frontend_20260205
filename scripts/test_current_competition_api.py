#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端全局当前赛事API
"""

import requests
import json
import io
import sys

# 解决Windows控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def test_as_role(role_name, phone, password):
    """测试指定角色的API访问"""
    print(f"\n{'='*80}")
    print(f"  测试角色: {role_name}")
    print(f"{'='*80}")
    
    # 1. 登录
    print(f"\n[步骤1] 登录...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login-with-password",
            json={"phone": phone, "password": password},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['token']
                actual_role = data['data'].get('role', 'N/A')
                print(f"✅ 登录成功 (角色: {actual_role})")
            else:
                print(f"❌ 登录失败: {data.get('message')}")
                return
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 获取当前赛事
    print(f"\n[步骤2] 获取当前赛事...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/current-competition",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            print(f"响应结构: {json.dumps(data, ensure_ascii=False)}")
            
            if data.get('code') == 0:
                current_id = data.get('data')
                print(f"\n当前赛事ID: {current_id}")
                print(f"数据类型: {type(current_id).__name__}")
            else:
                print(f"⚠️ 响应code != 0: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 获取当前赛事异常: {e}")
    
    # 3. 设置当前赛事（仅管理员角色）
    if actual_role in ['COMMITTEE_ADMIN', 'COMMITTEE', 'OPS']:
        print(f"\n[步骤3] 设置当前赛事 (测试ID=1)...")
        try:
            response = requests.post(
                f"{BASE_URL}/api/admin/current-competition",
                params={"competitionId": 1},
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 请求成功")
                print(f"响应: {json.dumps(data, ensure_ascii=False)}")
                
                if data.get('code') == 0:
                    print(f"✅ 设置成功: {data.get('data')}")
                else:
                    print(f"⚠️ 设置失败: {data.get('message')}")
            else:
                print(f"❌ 请求失败: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 设置当前赛事异常: {e}")
    else:
        print(f"\n[步骤3] 跳过设置测试（角色 {actual_role} 无权限）")

def main():
    print("\n" + "="*80)
    print("  全局当前赛事API测试")
    print("="*80)
    print("\nAPI信息:")
    print("  GET  /api/admin/current-competition     - 获取当前赛事ID (所有用户)")
    print("  POST /api/admin/current-competition     - 设置当前赛事ID (管理员)")
    print("="*80)
    
    # 测试不同角色
    test_cases = [
        ("OPS运维管理员", "13300005566", "test005566"),
        ("参赛者", "13966000011", "participant123"),
        ("组委会管理员", "13800000041", "committee123"),
    ]
    
    for role_name, phone, password in test_cases:
        test_as_role(role_name, phone, password)
    
    print(f"\n{'='*80}")
    print("  测试完成")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
