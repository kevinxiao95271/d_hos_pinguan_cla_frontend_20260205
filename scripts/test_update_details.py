#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试成员和活动说明更新 - 获取详细错误信息
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

def login_contestant():
    """参赛者登录"""
    print_section("1. 参赛者登录")
    url = f"{BASE_URL}/auth/login"
    payload = {
        "phone": "13800000011",
        "name": "Contestant A",
        "role": "CONTESTANT"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('data', {}).get('token')
            print(f"✅ 登录成功")
            return token
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

def create_registration(token):
    """创建报名"""
    print_section("2. 创建报名")
    url = f"{BASE_URL}/registrations"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "competitionId": 21,
        "institutionId": 1,
        "projectName": "详细测试项目",
        "groupType": "BASIC"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            registration_id = result.get('data', {}).get('id')
            print(f"✅ 创建成功，registrationId={registration_id}")
            return registration_id
        else:
            print(f"❌ 创建失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

def test_update_members_detailed(token, registration_id):
    """测试更新成员 - 获取详细错误"""
    print_section("3. 测试更新成员信息")
    
    # 测试1: 完整字段
    print("\n测试1: MENTOR 包含 department 字段")
    url = f"{BASE_URL}/registrations/{registration_id}/members"
    headers = {"Authorization": f"Bearer {token}"}
    payload1 = {
        "members": [
            {
                "name": "张三",
                "title": "主管护师",
                "department": "内科",
                "role": "PARTICIPANT"
            },
            {
                "name": "王五",
                "title": "副主任护师",
                "department": "",  # 空字符串
                "role": "MENTOR"
            }
        ]
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload1, timeout=30)
        print(f"请求: {json.dumps(payload1, ensure_ascii=False, indent=2)}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 测试1成功")
            return True
    except Exception as e:
        print(f"❌ 测试1异常: {str(e)}")
    
    # 测试2: MENTOR 不含 department
    print("\n测试2: MENTOR 不含 department 字段")
    payload2 = {
        "members": [
            {
                "name": "李四",
                "title": "护师",
                "department": "外科",
                "role": "PARTICIPANT"
            },
            {
                "name": "赵六",
                "title": "副主任护师",
                "role": "MENTOR"
            }
        ]
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload2, timeout=30)
        print(f"请求: {json.dumps(payload2, ensure_ascii=False, indent=2)}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 测试2成功")
            return True
    except Exception as e:
        print(f"❌ 测试2异常: {str(e)}")
    
    return False

def test_update_activity_detailed(token, registration_id):
    """测试更新活动说明 - 获取详细错误"""
    print_section("4. 测试更新活动说明")
    
    # 先获取字典数据
    print("先查询有效的字典值...")
    try:
        # 获取主题类型
        response1 = requests.get(f"{BASE_URL}/dictionaries/subject_type", timeout=30)
        print(f"\n主题类型字典: {response1.status_code}")
        if response1.status_code == 200:
            subject_types = response1.json().get('data', [])
            print(f"可用值: {[item.get('code') for item in subject_types[:5]]}")
        
        # 获取品管工具
        response2 = requests.get(f"{BASE_URL}/dictionaries/method", timeout=30)
        print(f"品管工具字典: {response2.status_code}")
        if response2.status_code == 200:
            methods = response2.json().get('data', [])
            print(f"可用值: {[item.get('code') for item in methods[:5]]}")
    except Exception as e:
        print(f"获取字典失败: {e}")
    
    # 测试1: 使用示例中的值
    print("\n测试1: 使用 PATIENT_CARE 和 PDCA")
    url = f"{BASE_URL}/registrations/{registration_id}/activity"
    headers = {"Authorization": f"Bearer {token}"}
    payload1 = {
        "theme": "护理质量改进",
        "keywords": "护理, 质量, 改进",
        "subjectTypeCode": "PATIENT_CARE",
        "methodCode": "PDCA",
        "averageWorkYears": 8,
        "averageAge": 35
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload1, timeout=30)
        print(f"请求: {json.dumps(payload1, ensure_ascii=False, indent=2)}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 测试1成功")
            return True
    except Exception as e:
        print(f"❌ 测试1异常: {str(e)}")
    
    # 测试2: 使用字典中的第一个值
    print("\n测试2: 使用字典中的实际值")
    if 'subject_types' in locals() and 'methods' in locals():
        if subject_types and methods:
            payload2 = {
                "theme": "测试主题",
                "keywords": "测试, 关键词",
                "subjectTypeCode": subject_types[0].get('code'),
                "methodCode": methods[0].get('code'),
                "averageWorkYears": 5,
                "averageAge": 30
            }
            
            try:
                response = requests.put(url, headers=headers, json=payload2, timeout=30)
                print(f"请求: {json.dumps(payload2, ensure_ascii=False, indent=2)}")
                print(f"状态码: {response.status_code}")
                print(f"响应: {response.text}")
                
                if response.status_code == 200:
                    print("✅ 测试2成功")
                    return True
            except Exception as e:
                print(f"❌ 测试2异常: {str(e)}")
    
    return False

def main():
    print("\n" + "=" * 60)
    print("  详细测试：成员和活动说明更新")
    print("=" * 60)
    
    # 1. 登录
    token = login_contestant()
    if not token:
        print("\n❌ 登录失败，测试终止")
        return
    
    # 2. 创建报名
    registration_id = create_registration(token)
    if not registration_id:
        print("\n❌ 创建报名失败，测试终止")
        return
    
    # 3. 测试更新成员
    members_ok = test_update_members_detailed(token, registration_id)
    
    # 4. 测试更新活动说明
    activity_ok = test_update_activity_detailed(token, registration_id)
    
    # 总结
    print_section("测试总结")
    print(f"更新成员: {'✅ 成功' if members_ok else '❌ 失败'}")
    print(f"更新活动说明: {'✅ 成功' if activity_ok else '❌ 失败'}")

if __name__ == "__main__":
    main()
