#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试更新成员和活动说明 - 使用已有的报名
"""

import sys
import io
import requests
import json

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031/api"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def test_members_various_formats():
    """测试多种成员格式"""
    print_section("测试成员更新 - 多种格式")
    
    # 先登录获取token
    print("正在登录...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "phone": "13800000011",
            "name": "Contestant A",
            "role": "CONTESTANT"
        }, timeout=30)
        
        if response.status_code != 200:
            print(f"登录失败: {response.status_code}")
            print(f"响应: {response.text}")
            return
        
        token = response.json().get('data', {}).get('token')
        print("登录成功")
    except Exception as e:
        print(f"登录异常: {e}")
        return
    
    # 创建新报名
    print("\n创建新报名...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{BASE_URL}/registrations", 
                                headers=headers,
                                json={
                                    "competitionId": 21,
                                    "institutionId": 1,
                                    "projectName": "成员测试项目",
                                    "groupType": "BASIC"
                                }, timeout=30)
        
        if response.status_code != 200:
            print(f"创建失败: {response.status_code}")
            print(f"响应: {response.text}")
            return
        
        registration_id = response.json().get('data', {}).get('id')
        print(f"创建成功: registrationId={registration_id}")
    except Exception as e:
        print(f"创建异常: {e}")
        return
    
    # 测试多种成员格式
    url = f"{BASE_URL}/registrations/{registration_id}/members"
    
    test_cases = [
        {
            "name": "测试1: MENTOR带department",
            "data": {
                "members": [
                    {
                        "name": "张三",
                        "title": "主管护师",
                        "department": "内科",
                        "role": "PARTICIPANT"
                    },
                    {
                        "name": "导师甲",
                        "title": "副主任护师",
                        "department": "护理部",
                        "role": "MENTOR"
                    }
                ]
            }
        },
        {
            "name": "测试2: MENTOR不带department",
            "data": {
                "members": [
                    {
                        "name": "李四",
                        "title": "护师",
                        "department": "外科",
                        "role": "PARTICIPANT"
                    },
                    {
                        "name": "导师乙",
                        "title": "主任护师",
                        "role": "MENTOR"
                    }
                ]
            }
        },
        {
            "name": "测试3: MENTOR的department为空字符串",
            "data": {
                "members": [
                    {
                        "name": "王五",
                        "title": "护师",
                        "department": "儿科",
                        "role": "PARTICIPANT"
                    },
                    {
                        "name": "导师丙",
                        "title": "副主任护师",
                        "department": "",
                        "role": "MENTOR"
                    }
                ]
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}")
        print(f"请求数据: {json.dumps(test_case['data'], ensure_ascii=False, indent=2)}")
        
        try:
            response = requests.put(url, headers=headers, json=test_case['data'], timeout=30)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            
            if response.status_code == 200:
                print("✅ 成功")
            else:
                print("❌ 失败")
        except Exception as e:
            print(f"❌ 异常: {e}")

def test_activity_with_dict():
    """测试活动说明 - 先获取字典"""
    print_section("测试活动说明更新 - 使用字典值")
    
    # 先登录
    print("正在登录...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "phone": "13800000011",
            "name": "Contestant A",
            "role": "CONTESTANT"
        }, timeout=30)
        
        if response.status_code != 200:
            print(f"登录失败: {response.status_code}")
            return
        
        token = response.json().get('data', {}).get('token')
        print("登录成功")
    except Exception as e:
        print(f"登录异常: {e}")
        return
    
    # 获取字典
    print("\n获取主题类型字典...")
    subject_type_code = None
    try:
        response = requests.get(f"{BASE_URL}/dictionaries/subject_type", timeout=30)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json().get('data', [])
            if data:
                subject_type_code = data[0].get('code')
                print(f"第一个主题类型: {data[0].get('code')} - {data[0].get('label')}")
                print(f"所有code: {[item.get('code') for item in data[:10]]}")
    except Exception as e:
        print(f"获取字典异常: {e}")
    
    print("\n获取品管工具字典...")
    method_code = None
    try:
        response = requests.get(f"{BASE_URL}/dictionaries/method", timeout=30)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json().get('data', [])
            if data:
                method_code = data[0].get('code')
                print(f"第一个品管工具: {data[0].get('code')} - {data[0].get('label')}")
                print(f"所有code: {[item.get('code') for item in data[:10]]}")
    except Exception as e:
        print(f"获取字典异常: {e}")
    
    if not subject_type_code or not method_code:
        print("\n⚠️ 无法获取字典值，跳过测试")
        return
    
    # 创建新报名
    print("\n创建新报名...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{BASE_URL}/registrations", 
                                headers=headers,
                                json={
                                    "competitionId": 21,
                                    "institutionId": 1,
                                    "projectName": "活动说明测试项目",
                                    "groupType": "BASIC"
                                }, timeout=30)
        
        if response.status_code != 200:
            print(f"创建失败: {response.status_code}")
            return
        
        registration_id = response.json().get('data', {}).get('id')
        print(f"创建成功: registrationId={registration_id}")
    except Exception as e:
        print(f"创建异常: {e}")
        return
    
    # 测试活动说明更新
    url = f"{BASE_URL}/registrations/{registration_id}/activity"
    payload = {
        "theme": "测试主题",
        "keywords": "测试, 关键词",
        "subjectTypeCode": subject_type_code,
        "methodCode": method_code,
        "averageWorkYears": 5,
        "averageAge": 30
    }
    
    print(f"\n更新活动说明:")
    print(f"请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ 成功")
        else:
            print("❌ 失败")
    except Exception as e:
        print(f"❌ 异常: {e}")

def main():
    print("\n" + "=" * 60)
    print("  直接测试：更新接口详细调试")
    print("=" * 60)
    
    # 等待一下，让后端稳定
    import time
    print("\n等待5秒...")
    time.sleep(5)
    
    test_members_various_formats()
    test_activity_with_dict()

if __name__ == "__main__":
    main()
