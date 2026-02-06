#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试书审阶段相关的 API
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

def test_login():
    """登录获取 token"""
    print("\n" + "="*60)
    print("1. 测试登录")
    print("="*60)
    
    payload = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN",
        "title": "组委会成员",
        "institutionId": None,
        "reviewerGroupCode": None,
        "interviewGroupCode": None,
        "expertBackground": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        print(f"[状态码] {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[响应] {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get("success") and data.get("data"):
                token = data["data"].get("token")
                print(f"[OK] 登录成功! Token: {token[:30]}...")
                return token
            else:
                print(f"[ERROR] 登录失败: {data.get('message')}")
                return None
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            print(f"[响应] {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] 异常: {str(e)}")
        return None

def test_get_dictionaries(token):
    """测试获取字典数据"""
    print("\n" + "="*60)
    print("2. 测试获取字典数据 - method")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/dictionaries/method",
            headers=headers,
            timeout=10
        )
        print(f"[状态码] {response.status_code}")
        print(f"[响应] {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"[OK] 获取字典成功，共 {len(data.get('data', []))} 条")
                return True
            else:
                print(f"[ERROR] {data.get('message')}")
                return False
        elif response.status_code == 401:
            print("[ERROR] 401 未授权 - Token 可能无效")
            return False
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 异常: {str(e)}")
        return False

def test_filter_registrations(token, competition_id=1):
    """测试筛选报名列表"""
    print("\n" + "="*60)
    print("3. 测试筛选报名列表")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "competitionId": competition_id,
        "institutionName": "",
        "groupType": "",
        "groupCode": "",
        "projectName": "",
        "methodCode": ""
    }
    
    print(f"[请求参数] {params}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/registrations/filter",
            headers=headers,
            params=params,
            timeout=10
        )
        print(f"[状态码] {response.status_code}")
        print(f"[响应] {response.text[:800]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                registrations = data.get("data", [])
                print(f"[OK] 获取报名列表成功，共 {len(registrations)} 条")
                if len(registrations) > 0:
                    print(f"[示例数据] {json.dumps(registrations[0], ensure_ascii=False, indent=2)}")
                else:
                    print("[INFO] 报名列表为空，可能原因：")
                    print("  1. 赛事 ID 不存在")
                    print("  2. 该赛事还没有报名数据")
                    print("  3. 后端数据库中没有测试数据")
                return True
            else:
                print(f"[ERROR] {data.get('message')}")
                return False
        elif response.status_code == 401:
            print("[ERROR] 401 未授权 - Token 可能无效或已过期")
            return False
        elif response.status_code == 404:
            print("[ERROR] 404 未找到 - API 端点可能不存在")
            return False
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 异常: {str(e)}")
        return False

def test_get_competitions(token):
    """测试获取赛事列表"""
    print("\n" + "="*60)
    print("4. 测试获取赛事列表")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/competitions",
            headers=headers,
            timeout=10
        )
        print(f"[状态码] {response.status_code}")
        print(f"[响应] {response.text[:800]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                competitions = data.get("data", [])
                print(f"[OK] 获取赛事列表成功，共 {len(competitions)} 条")
                if len(competitions) > 0:
                    for comp in competitions:
                        print(f"  - ID: {comp.get('id')}, 名称: {comp.get('name')}")
                else:
                    print("[INFO] 赛事列表为空，需要先创建赛事")
                return competitions
            else:
                print(f"[ERROR] {data.get('message')}")
                return []
        elif response.status_code == 401:
            print("[ERROR] 401 未授权")
            return []
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"[ERROR] 异常: {str(e)}")
        return []

def main():
    print("\n书审阶段 API 测试工具")
    print("="*60)
    
    # 1. 登录
    token = test_login()
    if not token:
        print("\n[终止] 登录失败，无法继续测试")
        return
    
    # 2. 测试字典 API
    test_get_dictionaries(token)
    
    # 3. 测试赛事列表
    competitions = test_get_competitions(token)
    
    # 4. 测试报名列表筛选
    if competitions:
        competition_id = competitions[0].get("id")
        test_filter_registrations(token, competition_id)
    else:
        print("\n[INFO] 尝试使用默认赛事 ID = 1")
        test_filter_registrations(token, 1)
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()
