#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试机构等级信息是否正确返回
"""

import requests
import json
import sys
import codecs

# 设置Windows终端编码
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "http://localhost:6031/api"

def test_apis():
    """测试各个API的机构等级返回"""
    
    print("=" * 80)
    print("测试机构等级信息")
    print("=" * 80)
    print()
    
    # 1. 登录获取token
    print("【1】登录获取token...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13966000011",
        "name": "参赛者11",
        "role": "CONTESTANT"
    }, timeout=10)
    
    if login_res.status_code != 200:
        print(f"❌ 登录失败: {login_res.status_code}")
        return
    
    login_data = login_res.json()
    if not login_data.get('success'):
        print(f"❌ 登录失败: {login_data.get('message')}")
        return
    
    token = login_data['data']['token']
    print(f"✅ 登录成功，token: {token[:20]}...")
    print()
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 测试我的报名列表
    print("【2】测试我的报名列表 API...")
    my_reg_res = requests.get(f"{BASE_URL}/registrations/my", headers=headers, timeout=10)
    if my_reg_res.status_code == 200:
        my_reg_data = my_reg_res.json()
        if my_reg_data.get('success') and my_reg_data.get('data'):
            registrations = my_reg_data['data']
            if isinstance(registrations, list) and len(registrations) > 0:
                first_reg = registrations[0]
                print(f"✅ 找到 {len(registrations)} 条报名记录")
                print(f"   第一条记录的机构信息：")
                print(f"   - institutionName: {first_reg.get('institutionName', 'N/A')}")
                print(f"   - institutionLevel: {first_reg.get('institutionLevel', 'N/A')}")
                print(f"   - institutionId: {first_reg.get('institutionId', 'N/A')}")
                
                reg_id = first_reg.get('registrationId')
                if not reg_id:
                    reg_id = first_reg.get('id')
                
                # 3. 测试报名详情API
                if reg_id:
                    print()
                    print(f"【3】测试报名详情 API (registrationId={reg_id})...")
                    detail_res = requests.get(f"{BASE_URL}/registrations/{reg_id}", headers=headers, timeout=10)
                    if detail_res.status_code == 200:
                        detail_data = detail_res.json()
                        if detail_data.get('success') and detail_data.get('data'):
                            data = detail_data['data']
                            print(f"✅ 获取详情成功")
                            print(f"   机构信息：")
                            
                            # 检查institution对象
                            institution = data.get('institution')
                            if institution:
                                print(f"   - institution.name: {institution.get('name', 'N/A')}")
                                print(f"   - institution.level: {institution.get('level', 'N/A')}")
                                print(f"   - institution.code: {institution.get('code', 'N/A')}")
                                print(f"   - institution.region: {institution.get('region', 'N/A')}")
                            else:
                                print(f"   ❌ 没有找到 institution 对象")
                            
                            # 检查registration对象
                            registration = data.get('registration')
                            if registration:
                                print(f"   registration对象：")
                                print(f"   - institutionName: {registration.get('institutionName', 'N/A')}")
                                print(f"   - institutionLevel: {registration.get('institutionLevel', 'N/A')}")
                    else:
                        print(f"❌ 详情API失败: {detail_res.status_code}")
            else:
                print(f"⚠️  没有报名记录")
        else:
            print(f"❌ API返回失败: {my_reg_data.get('message')}")
    else:
        print(f"❌ 请求失败: {my_reg_res.status_code}")
    
    print()
    
    # 4. 测试组委会登录并查看列表
    print("【4】测试组委会登录...")
    committee_login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }, timeout=10)
    
    if committee_login_res.status_code == 200:
        committee_data = committee_login_res.json()
        if committee_data.get('success'):
            committee_token = committee_data['data']['token']
            print(f"✅ 组委会登录成功")
            
            committee_headers = {"Authorization": f"Bearer {committee_token}"}
            
            # 测试书审分组列表
            print()
            print("【5】测试书审分组列表 API...")
            filter_res = requests.get(
                f"{BASE_URL}/admin/registrations/filter",
                headers=committee_headers,
                params={"page": 0, "size": 10},
                timeout=10
            )
            
            if filter_res.status_code == 200:
                filter_data = filter_res.json()
                if filter_data.get('success') and filter_data.get('data'):
                    data = filter_data['data']
                    
                    # 处理分页数据
                    if isinstance(data, dict):
                        content = data.get('content', [])
                    else:
                        content = data if isinstance(data, list) else []
                    
                    if content:
                        print(f"✅ 找到 {len(content)} 条记录")
                        first_item = content[0]
                        print(f"   第一条记录的机构信息：")
                        print(f"   - institutionName: {first_item.get('institutionName', 'N/A')}")
                        print(f"   - institutionLevel: {first_item.get('institutionLevel', 'N/A')}")
                        print(f"   - institutionId: {first_item.get('institutionId', 'N/A')}")
                    else:
                        print(f"⚠️  没有找到记录")
            else:
                print(f"❌ 请求失败: {filter_res.status_code}")
    
    print()
    
    # 6. 测试评委登录
    print("【6】测试评委登录...")
    reviewer_login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000021",
        "name": "李明华",
        "role": "REVIEWER",
        "reviewerGroupCode": "A1",
        "interviewGroupCode": "A1",
        "expertBackground": "MEDICAL"
    }, timeout=10)
    
    if reviewer_login_res.status_code == 200:
        reviewer_data = reviewer_login_res.json()
        if reviewer_data.get('success'):
            reviewer_token = reviewer_data['data']['token']
            print(f"✅ 评委登录成功")
            
            reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}
            
            # 测试评委任务列表
            print()
            print("【7】测试评委任务列表 API...")
            tasks_res = requests.get(
                f"{BASE_URL}/reviews/my-tasks",
                headers=reviewer_headers,
                timeout=10
            )
            
            if tasks_res.status_code == 200:
                tasks_data = tasks_res.json()
                if tasks_data.get('success') and tasks_data.get('data'):
                    tasks = tasks_data['data']
                    if tasks:
                        print(f"✅ 找到 {len(tasks)} 个任务")
                        first_task = tasks[0]
                        print(f"   第一个任务的机构信息：")
                        print(f"   - institutionName: {first_task.get('institutionName', 'N/A')}")
                        print(f"   - institutionLevel: {first_task.get('institutionLevel', 'N/A')}")
                        print(f"   - projectName: {first_task.get('projectName', 'N/A')}")
                    else:
                        print(f"⚠️  没有任务")
            else:
                print(f"❌ 请求失败: {tasks_res.status_code}")
    
    print()
    print("=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_apis()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("   请确保后端服务运行在 http://localhost:6031")
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
