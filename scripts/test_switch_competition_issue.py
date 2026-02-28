#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试切换赛事页面问题
"""

import requests
import json
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def main():
    print("\n" + "="*80)
    print("  切换赛事页面问题诊断")
    print("="*80)
    
    # 1. 登录
    print("\n[步骤1] 登录...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login-with-password",
            json={"phone": "13300005566", "password": "test005566"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['token']
                role = data['data'].get('role')
                print(f"✅ 登录成功 (角色: {role})")
            else:
                print(f"❌ 登录失败: {data.get('message')}")
                return
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 获取赛事列表
    print("\n[步骤2] 获取赛事列表...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/competitions",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            print(f"响应格式检查:")
            print(f"  - success字段: {data.get('success')}")
            print(f"  - data类型: {type(data.get('data'))}")
            
            if data.get('success') and data.get('data'):
                competitions = data['data']
                print(f"\n赛事数量: {len(competitions)}")
                
                if len(competitions) > 0:
                    print(f"\n第一个赛事信息:")
                    comp = competitions[0]
                    print(f"  ID: {comp.get('id')}")
                    print(f"  名称: {comp.get('name')}")
                    print(f"  阶段: {comp.get('stage')}")
                    print(f"  报名开始: {comp.get('registerStart')}")
                    print(f"  报名结束: {comp.get('registerEnd')}")
                    print(f"\n完整字段列表:")
                    for key in comp.keys():
                        print(f"    {key}: {comp[key]}")
                else:
                    print("⚠️ 赛事列表为空")
            else:
                print(f"⚠️ 响应失败或无数据")
        else:
            print(f"❌ 请求失败: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 获取赛事列表异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 获取当前赛事ID
    print("\n[步骤3] 获取当前赛事ID...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/current-competition",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            print(f"响应: {json.dumps(data, ensure_ascii=False)}")
            
            if data.get('code') == 0:
                print(f"\n当前赛事ID: {data.get('data')}")
            else:
                print(f"⚠️ 响应code={data.get('code')}: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 获取当前赛事异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("  诊断完成")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
