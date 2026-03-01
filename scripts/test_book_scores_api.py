#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试书审得分API
检查 GET /api/admin/reviews/book-scores 是否存在
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

def login_committee():
    """登录组委会账号"""
    url = f"{BASE_URL}/auth/login-with-password"
    data = {
        "phone": "13800000127",
        "password": "committee2026"
    }
    
    print(f"\n{'='*60}")
    print("🔐 登录组委会账号...")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        
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
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_book_scores_api(token):
    """测试书审得分API"""
    url = f"{BASE_URL}/admin/reviews/book-scores"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "competitionId": 1
    }
    
    print(f"\n{'='*60}")
    print("📊 测试书审得分API")
    print(f"{'='*60}")
    print(f"URL: GET {url}")
    print(f"参数: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n响应数据:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success'):
                data = result.get('data', [])
                print(f"\n✅ API调用成功")
                print(f"返回记录数: {len(data)}")
                
                if len(data) > 0:
                    print(f"\n第一条记录示例:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
            else:
                print(f"\n❌ API返回失败: {result.get('message')}")
        elif response.status_code == 404:
            print(f"\n❌ API不存在 (404)")
            print(f"响应内容: {response.text}")
        else:
            print(f"\n❌ 请求失败")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")

def check_alternative_apis(token):
    """检查可能的替代API"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"\n{'='*60}")
    print("🔍 检查可能的替代API")
    print(f"{'='*60}")
    
    # 可能的API端点
    endpoints = [
        "/admin/reviews/scores",
        "/admin/reviews/summary",
        "/reviews/scores",
        "/admin/reviews/tasks"
    ]
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        params = {"competitionId": 1, "stage": "BOOK"}
        
        print(f"\n尝试: GET {url}")
        print(f"参数: {params}")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    data = result.get('data')
                    if isinstance(data, list):
                        print(f"✅ 成功 - 返回 {len(data)} 条记录")
                    elif isinstance(data, dict):
                        print(f"✅ 成功 - 返回对象，keys: {list(data.keys())}")
                    else:
                        print(f"✅ 成功 - 数据类型: {type(data)}")
                    
                    # 显示部分数据
                    print(f"数据预览:")
                    print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
                else:
                    print(f"⚠️ 返回失败: {result.get('message')}")
            elif response.status_code == 404:
                print(f"❌ 不存在 (404)")
            else:
                print(f"⚠️ 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def main():
    print("="*60)
    print("书审得分API测试")
    print("="*60)
    
    # 登录
    token = login_committee()
    if not token:
        print("\n❌ 无法获取token，测试终止")
        return
    
    # 测试目标API
    test_book_scores_api(token)
    
    # 检查替代API
    check_alternative_apis(token)
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
