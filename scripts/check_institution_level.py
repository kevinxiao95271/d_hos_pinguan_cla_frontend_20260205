#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查机构等级信息是否正确返回
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

def check_field(data, path, description):
    """检查字段是否存在"""
    parts = path.split('.')
    current = data
    
    for part in parts:
        if isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                print(f"   ❌ 缺少字段: {path}")
                return False
        else:
            print(f"   ❌ 路径错误: {path}")
            return False
    
    if current:
        print(f"   ✅ {description}: {current}")
        return True
    else:
        print(f"   ⚠️  {description}: 值为空")
        return False

def test_scenario(scenario_name, token, url, params=None, check_paths=None):
    """测试一个场景"""
    print(f"\n{'='*80}")
    print(f"【场景】{scenario_name}")
    print(f"{'='*80}")
    print(f"URL: {url}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        if params:
            response = requests.get(url, headers=headers, params=params, timeout=15)
        else:
            response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ API返回失败: {data.get('message')}")
            return False
        
        api_data = data.get('data')
        if not api_data:
            print(f"⚠️  没有数据")
            return False
        
        # 显示原始数据结构（简化）
        print(f"\n数据类型: {type(api_data).__name__}")
        
        # 检查指定的字段路径
        results = []
        for path, description in check_paths:
            result = check_field(api_data, path, description)
            results.append(result)
        
        all_ok = all(results)
        print(f"\n结果: {'✅ 全部通过' if all_ok else '❌ 部分缺失'}")
        return all_ok
        
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    print("="*80)
    print("机构等级信息检测")
    print("="*80)
    
    # 存储各个角色的token
    tokens = {}
    
    # 1. 参赛者登录
    print("\n【步骤1】参赛者登录...")
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "phone": "13966000011",
            "name": "参赛者11",
            "role": "CONTESTANT"
        }, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            if data.get('success'):
                tokens['contestant'] = data['data']['token']
                print(f"✅ 参赛者登录成功")
            else:
                print(f"❌ 登录失败: {data.get('message')}")
                return
        else:
            print(f"❌ HTTP {res.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return
    
    # 2. 组委会登录
    print("\n【步骤2】组委会登录...")
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "phone": "13800000041",
            "name": "CommitteeAdmin A",
            "role": "COMMITTEE_ADMIN"
        }, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            if data.get('success'):
                tokens['committee'] = data['data']['token']
                print(f"✅ 组委会登录成功")
        else:
            print(f"❌ HTTP {res.status_code}")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
    
    # 3. 评委登录
    print("\n【步骤3】评委登录...")
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "phone": "13800000021",
            "name": "李明华",
            "role": "REVIEWER",
            "reviewerGroupCode": "A1",
            "interviewGroupCode": "A1",
            "expertBackground": "MEDICAL"
        }, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            if data.get('success'):
                tokens['reviewer'] = data['data']['token']
                print(f"✅ 评委登录成功")
        else:
            print(f"❌ HTTP {res.status_code}")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
    
    # 获取第一条报名记录ID
    print("\n【步骤4】获取报名记录...")
    registration_id = None
    try:
        res = requests.get(
            f"{BASE_URL}/registrations/my",
            headers={"Authorization": f"Bearer {tokens['contestant']}"},
            timeout=15
        )
        if res.status_code == 200:
            data = res.json()
            if data.get('success') and data.get('data'):
                registrations = data['data']
                if registrations:
                    registration_id = registrations[0].get('registrationId') or registrations[0].get('id')
                    print(f"✅ 找到报名记录ID: {registration_id}")
    except Exception as e:
        print(f"❌ 获取报名记录失败: {e}")
    
    # 测试四个场景
    results = {}
    
    # 场景1：参赛者报名详情
    if registration_id and 'contestant' in tokens:
        results['场景1'] = test_scenario(
            "参赛者 - 我的报名详情",
            tokens['contestant'],
            f"{BASE_URL}/registrations/{registration_id}",
            check_paths=[
                ("institution.level", "机构等级 (institution.level)"),
                ("institution.name", "机构名称"),
                ("registration.institutionName", "报名表中的机构名称")
            ]
        )
    
    # 场景2：书审分组列表
    if 'committee' in tokens:
        results['场景2'] = test_scenario(
            "组委会 - 书审分组列表",
            tokens['committee'],
            f"{BASE_URL}/admin/registrations/filter",
            params={"page": 0, "size": 5},
            check_paths=[
                ("content.0.institutionLevel", "第一条记录的机构等级"),
                ("content.0.institutionName", "第一条记录的机构名称"),
                ("content.0.projectName", "第一条记录的项目名称")
            ]
        )
    
    # 场景3：书审分组详情（使用相同的报名ID）
    if registration_id and 'committee' in tokens:
        results['场景3'] = test_scenario(
            "组委会 - 书审分组详情",
            tokens['committee'],
            f"{BASE_URL}/registrations/{registration_id}",
            check_paths=[
                ("institution.level", "机构等级 (institution.level)"),
                ("institution.name", "机构名称"),
                ("registration.institutionName", "报名表中的机构名称")
            ]
        )
    
    # 场景4：评委任务列表
    if 'reviewer' in tokens:
        results['场景4'] = test_scenario(
            "评委 - 评审任务列表",
            tokens['reviewer'],
            f"{BASE_URL}/reviews/my-tasks",
            check_paths=[
                ("0.institutionLevel", "第一个任务的机构等级"),
                ("0.institutionName", "第一个任务的机构名称"),
                ("0.projectName", "第一个任务的项目名称")
            ]
        )
    
    # 汇总结果
    print("\n")
    print("="*80)
    print("检测结果汇总")
    print("="*80)
    
    for scenario, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{scenario}: {status}")
    
    all_passed = all(results.values())
    
    print("\n")
    if all_passed:
        print("🎉 所有场景的机构等级信息都正确返回！")
    else:
        print("⚠️  部分场景的机构等级信息缺失，请查看详细日志")
    
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
