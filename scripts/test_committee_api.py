#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试组委会API的机构等级返回
"""

import requests
import sys
import codecs

# 设置Windows终端编码
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "http://localhost:6031/api"

def test_committee():
    print("=" * 80)
    print("测试组委会API")
    print("=" * 80)
    print()
    
    # 登录组委会
    print("【1】组委会登录...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }, timeout=10)
    
    if login_res.status_code != 200:
        print(f"❌ 登录失败: {login_res.status_code}")
        return
    
    login_data = login_res.json()
    if not login_data.get('success'):
        print(f"❌ 登录失败: {login_data.get('message')}")
        return
    
    token = login_data['data']['token']
    print(f"✅ 登录成功")
    print()
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取当前赛事列表
    print("【2】获取赛事列表...")
    comp_res = requests.get(f"{BASE_URL}/competition/list", headers=headers, timeout=10)
    if comp_res.status_code == 200:
        comp_data = comp_res.json()
        if comp_data.get('success') and comp_data.get('data'):
            competitions = comp_data['data']
            if competitions:
                print(f"✅ 找到 {len(competitions)} 个赛事")
                first_comp = competitions[0]
                comp_id = first_comp.get('id')
                print(f"   第一个赛事: {first_comp.get('name')} (ID: {comp_id})")
                print()
                
                # 切换赛事
                print(f"【3】切换到赛事 {comp_id}...")
                switch_res = requests.post(
                    f"{BASE_URL}/competition/switch/{comp_id}",
                    headers=headers,
                    timeout=10
                )
                if switch_res.status_code == 200:
                    print(f"✅ 切换成功")
                    print()
                else:
                    print(f"⚠️  切换失败: {switch_res.status_code}")
                    print()
            else:
                print(f"⚠️  没有赛事，需要先创建赛事")
                return
    
    # 测试书审分组列表
    print("【4】测试书审分组列表 (无过滤条件)...")
    filter_res = requests.get(
        f"{BASE_URL}/admin/registrations/filter",
        headers=headers,
        params={"page": 0, "size": 5},
        timeout=10
    )
    
    print(f"   状态码: {filter_res.status_code}")
    
    if filter_res.status_code == 200:
        filter_data = filter_res.json()
        if filter_data.get('success') and filter_data.get('data'):
            data = filter_data['data']
            
            # 处理分页数据
            if isinstance(data, dict):
                content = data.get('content', [])
                total = data.get('totalElements', 0)
            else:
                content = data if isinstance(data, list) else []
                total = len(content)
            
            print(f"✅ 成功获取数据")
            print(f"   总记录数: {total}")
            print(f"   当前页记录数: {len(content)}")
            
            if content:
                print()
                print("   前3条记录的机构等级信息：")
                for i, item in enumerate(content[:3], 1):
                    print(f"   {i}. 项目: {item.get('projectName', 'N/A')[:20]}")
                    print(f"      机构名称: {item.get('institutionName', 'N/A')}")
                    print(f"      机构等级: {item.get('institutionLevel', 'N/A')}")
                    print()
            else:
                print(f"⚠️  当前赛事没有报名记录")
        else:
            print(f"❌ API返回失败: {filter_data.get('message')}")
    else:
        try:
            error_data = filter_res.json()
            print(f"❌ 请求失败: {error_data.get('message', '未知错误')}")
        except:
            print(f"❌ 请求失败: HTTP {filter_res.status_code}")
            print(f"   响应内容: {filter_res.text[:200]}")
    
    print()
    
    # 测试面谈分组列表
    print("【5】测试面谈分组列表...")
    interview_res = requests.get(
        f"{BASE_URL}/admin/registrations/interview-groups",
        headers=headers,
        params={"page": 0, "size": 5},
        timeout=10
    )
    
    print(f"   状态码: {interview_res.status_code}")
    
    if interview_res.status_code == 200:
        interview_data = interview_res.json()
        if interview_data.get('success') and interview_data.get('data'):
            data = interview_data['data']
            
            if isinstance(data, dict):
                content = data.get('content', [])
                total = data.get('totalElements', 0)
            else:
                content = data if isinstance(data, list) else []
                total = len(content)
            
            print(f"✅ 成功获取数据")
            print(f"   总记录数: {total}")
            print(f"   当前页记录数: {len(content)}")
            
            if content:
                print()
                print("   前3条记录的机构等级信息：")
                for i, item in enumerate(content[:3], 1):
                    print(f"   {i}. 项目: {item.get('projectName', 'N/A')[:20]}")
                    print(f"      机构名称: {item.get('institutionName', 'N/A')}")
                    print(f"      机构等级: {item.get('institutionLevel', 'N/A')}")
                    print()
            else:
                print(f"⚠️  当前赛事没有面谈数据")
        else:
            print(f"❌ API返回失败: {interview_data.get('message')}")
    else:
        print(f"❌ 请求失败: {interview_res.status_code}")
    
    print()
    print("=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_committee()
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
