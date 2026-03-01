#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查书审评分数据
查看系统中是否有书审评分数据，以及数据结构
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"
TIMEOUT = 10

def login():
    """登录组委会账号"""
    url = f"{BASE_URL}/auth/login-with-password"
    data = {"phone": "13800000127", "password": "committee2026"}
    
    print("🔐 登录组委会账号...")
    try:
        response = requests.post(url, json=data, timeout=TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 登录成功\n")
                return result['data']['token']
    except Exception as e:
        print(f"❌ 登录失败: {e}\n")
    return None

def check_review_summary(token):
    """检查评审汇总API"""
    url = f"{BASE_URL}/admin/reviews/summary"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("="*60)
    print("1. 检查评审汇总 (不带stage参数)")
    print("="*60)
    
    params = {"competitionId": 1}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"URL: {url}")
        print(f"参数: {params}")
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success'):
                data = result.get('data', [])
                print(f"\n✅ 返回 {len(data)} 条记录")
                
                if len(data) > 0:
                    print(f"\n第一条记录字段:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    print("\n" + "="*60)
    print("2. 检查评审汇总 (带stage=BOOK)")
    print("="*60)
    
    params = {"competitionId": 1, "stage": "BOOK"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"URL: {url}")
        print(f"参数: {params}")
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success'):
                data = result.get('data', [])
                print(f"\n✅ 返回 {len(data)} 条记录")
                
                if len(data) > 0:
                    print(f"\n第一条记录字段:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def check_review_tasks(token):
    """检查评审任务API"""
    url = f"{BASE_URL}/admin/reviews/tasks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"competitionId": 1, "stage": "BOOK"}
    
    print("\n" + "="*60)
    print("3. 检查评审任务列表")
    print("="*60)
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"URL: {url}")
        print(f"参数: {params}")
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success'):
                data = result.get('data', [])
                print(f"\n✅ 返回 {len(data)} 条记录")
                
                if len(data) > 0:
                    print(f"\n第一条记录字段:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def check_registrations(token):
    """检查报名列表（看是否有书审阶段的报名）"""
    url = f"{BASE_URL}/admin/registrations/filter"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "competitionId": 1,
        "stage": "BOOK",
        "page": 0,
        "size": 5
    }
    
    print("\n" + "="*60)
    print("4. 检查书审阶段报名列表")
    print("="*60)
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"URL: {url}")
        print(f"参数: {params}")
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                data = result.get('data', {})
                content = data.get('content', [])
                total = data.get('totalElements', 0)
                
                print(f"✅ 总共 {total} 条报名记录")
                print(f"返回前 {len(content)} 条\n")
                
                if len(content) > 0:
                    print(f"第一条报名记录:")
                    print(json.dumps(content[0], indent=2, ensure_ascii=False))
            else:
                print(f"❌ 失败: {result.get('message')}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def main():
    print("="*60)
    print("书审评分数据检查")
    print("="*60)
    print()
    
    token = login()
    if not token:
        print("❌ 无法获取token，测试终止")
        return
    
    check_review_summary(token)
    check_review_tasks(token)
    check_registrations(token)
    
    print("\n" + "="*60)
    print("检查完成")
    print("="*60)

if __name__ == "__main__":
    main()
