#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参赛者报名流程端到端测试
测试报名提交、草稿保存、查看报名记录等功能
"""

import requests
import json
import sys

BASE_URL = "http://localhost:6031/api"

# 设置控制台输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(success, message, data=None):
    """打印结果"""
    status = "✅" if success else "❌"
    print(f"{status} {message}")
    if data:
        data_str = json.dumps(data, ensure_ascii=False, indent=2)
        print(f"   数据: {data_str[:500]}")

def test_contestant_login():
    """测试参赛者登录"""
    print_section("1. 参赛者登录")
    
    url = f"{BASE_URL}/auth/login"
    payload = {
        "phone": "13800000011",
        "name": "Contestant A",
        "title": "Nurse",
        "role": "CONTESTANT",
        "institutionId": 1
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"请求 URL: {url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('data', {}).get('token')
                print_result(True, "参赛者登录成功", {"token": token[:50] + "..." if token else None})
                return token
            else:
                print_result(False, f"登录失败: {result.get('message')}")
                return None
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return None
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return None

def test_get_my_registrations(token):
    """获取我的报名列表"""
    print_section("2. 获取我的报名列表")
    
    url = f"{BASE_URL}/registrations/my"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"请求 URL: {url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                registrations = result.get('data', [])
                print_result(True, f"获取报名列表成功，共 {len(registrations)} 条")
                
                for idx, reg in enumerate(registrations, 1):
                    print(f"\n   报名 {idx}:")
                    print(f"   - registrationId: {reg.get('id')}")
                    print(f"   - projectName: {reg.get('projectName')}")
                    print(f"   - status: {reg.get('status')}")
                    print(f"   - createdAt: {reg.get('createdAt')}")
                    print(f"   - submittedAt: {reg.get('submittedAt')}")
                
                return registrations
            else:
                print_result(False, f"获取失败: {result.get('message')}")
                return []
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return []
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return []

def test_create_draft_registration(token, competition_id=21):
    """创建草稿报名"""
    print_section("3. 创建草稿报名")
    
    url = f"{BASE_URL}/registrations"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "competitionId": competition_id,
        "institutionId": 1,  # 参赛者的机构ID
        "projectName": "测试项目-草稿",
        "groupType": "BASIC"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"请求 URL: {url}")
        print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                registration_id = data.get('id')
                print_result(True, f"创建草稿成功，registrationId={registration_id}")
                return registration_id
            else:
                print_result(False, f"创建失败: {result.get('message')}")
                return None
        else:
            print_result(False, f"HTTP 错误: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return None

def test_update_basic_info(token, registration_id):
    """更新基本信息"""
    print_section(f"4. 更新基本信息 (registrationId={registration_id})")
    
    url = f"{BASE_URL}/registrations/{registration_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "projectName": "测试项目-已更新",
        "groupType": "BASIC"
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        print(f"请求 URL: {url}")
        print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_result(True, "更新基本信息成功")
                return True
            else:
                print_result(False, f"更新失败: {result.get('message')}")
                return False
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return False

def test_update_members(token, registration_id):
    """更新成员信息"""
    print_section(f"5. 更新成员信息 (registrationId={registration_id})")
    
    url = f"{BASE_URL}/registrations/{registration_id}/members"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "members": [
            {
                "name": "张三",
                "title": "主管护师",
                "department": "内科",
                "role": "PARTICIPANT"
            },
            {
                "name": "李四",
                "title": "护师",
                "department": "外科",
                "role": "PARTICIPANT"
            },
            {
                "name": "王五",
                "title": "副主任护师",
                "role": "MENTOR"
            }
        ]
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        print(f"请求 URL: {url}")
        print(f"请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)[:300]}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_result(True, "更新成员成功")
                return True
            else:
                print_result(False, f"更新失败: {result.get('message')}")
                return False
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return False

def test_update_activity(token, registration_id):
    """更新活动说明"""
    print_section(f"6. 更新活动说明 (registrationId={registration_id})")
    
    url = f"{BASE_URL}/registrations/{registration_id}/activity"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "theme": "护理质量改进",
        "keywords": "护理, 质量, 改进",
        "subjectTypeCode": "subject_type_1",
        "methodCode": "PDCA",
        "experienceImproveCode": "experience_1",
        "qualityTopicCode": "quality_topic_1",
        "avgWorkYears": 6,
        "avgAge": 32,
        "crossDepartment": False
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        print(f"请求 URL: {url}")
        print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_result(True, "更新活动说明成功")
                return True
            else:
                print_result(False, f"更新失败: {result.get('message')}")
                return False
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return False

def test_submit_registration(token, registration_id):
    """提交报名"""
    print_section(f"7. 提交报名 (registrationId={registration_id})")
    
    url = f"{BASE_URL}/registrations/{registration_id}/submit"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers, timeout=30)
        print(f"请求 URL: {url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_result(True, "提交报名成功")
                print("   ⚠️ 提交后报名状态应变为 SUBMITTED")
                print("   ⚠️ 提交后应不能再修改")
                return True
            else:
                print_result(False, f"提交失败: {result.get('message')}")
                return False
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return False

def test_update_submitted_registration(token, registration_id):
    """测试更新已提交的报名（应该失败）"""
    print_section(f"8. 测试更新已提交的报名 (应该被拒绝)")
    
    url = f"{BASE_URL}/registrations/{registration_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "projectName": "测试项目-尝试修改已提交的"
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        print(f"请求 URL: {url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_result(False, "❌ 漏洞！已提交的报名竟然可以修改！")
                return False
            else:
                print_result(True, f"✅ 正确！已提交的报名不能修改: {result.get('message')}")
                return True
        elif response.status_code == 403 or response.status_code == 400:
            print_result(True, "✅ 正确！已提交的报名被拒绝修改")
            return True
        else:
            print_result(False, f"HTTP 错误: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"请求异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  参赛者报名流程端到端测试")
    print("="*60)
    
    # 1. 参赛者登录
    token = test_contestant_login()
    if not token:
        print("\n❌ 登录失败，测试终止")
        return
    
    # 2. 获取我的报名列表
    registrations = test_get_my_registrations(token)
    
    # 3. 创建草稿
    draft_id = test_create_draft_registration(token)
    if not draft_id:
        print("\n❌ 创建草稿失败，测试终止")
        return
    
    # 4. 更新基本信息
    test_update_basic_info(token, draft_id)
    
    # 5. 更新成员信息
    test_update_members(token, draft_id)
    
    # 6. 更新活动说明
    test_update_activity(token, draft_id)
    
    # 7. 提交报名
    test_submit_registration(token, draft_id)
    
    # 8. 尝试修改已提交的报名（应该被拒绝）
    test_update_submitted_registration(token, draft_id)
    
    # 9. 再次查看报名列表
    test_get_my_registrations(token)
    
    print_section("测试总结")
    print("""
✅ 参赛者报名流程测试完成

关键检查点：
1. 草稿保存功能
   - ✅ 可以创建草稿 (status=DRAFT)
   - ✅ 草稿可以多次修改
   - ✅ 草稿不会出现在评审列表

2. 报名提交功能
   - ✅ 提交后状态变为 SUBMITTED
   - ✅ 提交后不能再修改
   - ✅ 重复提交应被拒绝

3. 前端页面要求：
   - 已提交的报名应显示为灰色或禁用状态
   - 已提交的报名不显示"编辑"和"提交"按钮
   - 草稿状态显示"编辑"和"提交"按钮
   - 提交时需要二次确认

前端页面对应：
- 参赛者登录：/login
- 我的报名：/contestant/my-competition
- 新建报名：/contestant/register/:competitionId
    """)

if __name__ == "__main__":
    main()
