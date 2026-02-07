#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试品管工具筛选 - 验证 methodLabel 参数
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_method_label_filter():
    """测试使用 methodLabel 参数筛选"""
    print("=" * 80)
    print("测试品管工具筛选 - methodLabel 参数")
    print("=" * 80)
    
    # 1. 登录
    print("\n[1] 登录组委会账号...")
    login_data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Admin",
        "role": "COMMITTEE_ADMIN"
    }
    
    try:
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=10
        )
        login_resp.raise_for_status()
        login_result = login_resp.json()
        
        if not login_result.get('success'):
            print(f"[ERROR] 登录失败")
            return
        
        token = login_result['data']['token']
        print(f"[OK] 登录成功！")
        
    except Exception as e:
        print(f"[ERROR] 登录异常: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. 获取字典数据（品管工具列表）
    print("\n[2] 获取品管工具字典...")
    try:
        dict_resp = requests.get(
            f"{BASE_URL}/api/dictionaries/method",
            headers=headers,
            timeout=10
        )
        dict_resp.raise_for_status()
        dict_result = dict_resp.json()
        
        if dict_result.get('success'):
            methods = dict_result['data']
            print(f"[OK] 获取到 {len(methods)} 个品管工具")
            print("\n可用的品管工具：")
            for method in methods[:5]:  # 显示前5个
                print(f"  - {method['label']} (code: {method['code']})")
            if len(methods) > 5:
                print(f"  ... 还有 {len(methods) - 5} 个")
        else:
            print(f"[ERROR] 获取字典失败")
            methods = []
    except Exception as e:
        print(f"[ERROR] 获取字典异常: {e}")
        methods = []
    
    # 3. 测试使用 methodLabel 筛选（用户示例）
    print("\n[3] 测试使用 methodLabel='品管圈-课题达成' 筛选...")
    try:
        filter_resp = requests.get(
            f"{BASE_URL}/api/admin/registrations/filter",
            params={
                "competitionId": 21,
                "methodLabel": "品管圈-课题达成"
            },
            headers=headers,
            timeout=10
        )
        filter_resp.raise_for_status()
        filter_result = filter_resp.json()
        
        if filter_result.get('success'):
            registrations = filter_result['data']
            print(f"[OK] 筛选成功！找到 {len(registrations)} 个报名")
            
            if registrations:
                print("\n筛选结果示例：")
                for reg in registrations[:3]:  # 显示前3个
                    print(f"  - ID: {reg.get('registrationId')}")
                    print(f"    项目: {reg.get('projectName')}")
                    print(f"    工具: {reg.get('methodLabel')}")
                    print(f"    机构: {reg.get('institutionName')}")
                    print()
            else:
                print("\n[INFO] 该条件下没有匹配的报名数据")
        else:
            print(f"[ERROR] 筛选失败: {filter_result.get('message')}")
            
    except Exception as e:
        print(f"[ERROR] 筛选异常: {e}")
    
    # 4. 测试使用其他品管工具筛选
    if methods:
        print("\n[4] 测试使用第一个品管工具筛选...")
        first_method = methods[0]['label']
        print(f"测试工具: {first_method}")
        
        try:
            filter_resp = requests.get(
                f"{BASE_URL}/api/admin/registrations/filter",
                params={
                    "competitionId": 21,
                    "methodLabel": first_method
                },
                headers=headers,
                timeout=10
            )
            filter_resp.raise_for_status()
            filter_result = filter_resp.json()
            
            if filter_result.get('success'):
                registrations = filter_result['data']
                print(f"[OK] 找到 {len(registrations)} 个报名")
                
                if registrations:
                    print("\n部分结果：")
                    for reg in registrations[:2]:
                        print(f"  - {reg.get('projectName')} (工具: {reg.get('methodLabel')})")
            else:
                print(f"[ERROR] 筛选失败: {filter_result.get('message')}")
                
        except Exception as e:
            print(f"[ERROR] 筛选异常: {e}")
    
    # 5. 对比使用 methodCode 筛选（应该不工作或返回不同结果）
    print("\n[5] 测试使用 methodCode 参数（旧方式，应该不工作）...")
    try:
        filter_resp = requests.get(
            f"{BASE_URL}/api/admin/registrations/filter",
            params={
                "competitionId": 21,
                "methodCode": "pdca"  # 使用 code 而不是 label
            },
            headers=headers,
            timeout=10
        )
        filter_resp.raise_for_status()
        filter_result = filter_resp.json()
        
        if filter_result.get('success'):
            registrations = filter_result['data']
            print(f"[INFO] methodCode 参数返回 {len(registrations)} 个结果")
            if len(registrations) == 0:
                print("  ✅ 符合预期：methodCode 参数不起作用")
            else:
                print(f"  ⚠️ 意外：methodCode 参数仍然有效")
        else:
            print(f"[INFO] methodCode 参数返回失败（符合预期）")
            
    except Exception as e:
        print(f"[INFO] methodCode 参数请求异常（可能符合预期）: {e}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    print("""
前端修复要点：
1. filters 对象中使用 methodLabel 而不是 methodCode
2. 下拉框的 value 绑定 item.label 而不是 item.code
3. 显示筛选条件时直接使用 filters.methodLabel

修复后：
- 选择"品管圈-课题达成"
- 前端传给后端: methodLabel='品管圈-课题达成'
- 后端返回匹配的报名数据
""")

if __name__ == '__main__':
    test_method_label_filter()
