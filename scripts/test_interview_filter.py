#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试面谈页面的筛选是否只返回进阶组项目
"""

import requests
import json
import sys
import io

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031/api"

def test_interview_filter():
    """测试面谈评委分配页面的筛选"""
    
    print("=" * 80)
    print("测试面谈页面筛选 - 是否只返回进阶组")
    print("=" * 80)
    
    # 1. 登录获取token
    print("\n[步骤1] 登录组委会账号...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Admin",
        "role": "COMMITTEE_ADMIN"
    }, timeout=30)
    
    if login_res.status_code != 200:
        print(f"[错误] 登录失败: {login_res.status_code}")
        return
    
    token = login_res.json()['data']['token']
    print(f"[成功] 登录成功，token: {token[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. 测试面谈评委分配页面的筛选（应该固定为进阶组）
    print("\n[步骤2] 测试面谈评委分配 - 报名列表筛选...")
    print("请求参数: competitionId=21, groupType=ADVANCED, page=1, size=50")
    
    filter_res = requests.get(
        f"{BASE_URL}/admin/registrations/filter",
        headers=headers,
        params={
            "competitionId": 21,
            "groupType": "ADVANCED",  # 固定为进阶组
            "page": 1,
            "size": 50
        },
        timeout=30
    )
    
    if filter_res.status_code != 200:
        print(f"[错误] 请求失败: {filter_res.status_code}")
        print(f"响应: {filter_res.text}")
        return
    
    data = filter_res.json()
    if not data.get('success'):
        print(f"[错误] API返回失败: {data.get('message')}")
        return
    
    result = data['data']
    
    # 检查返回结果
    if isinstance(result, dict) and 'content' in result:
        # 分页响应
        items = result['content']
        total = result['totalCount']
        print(f"[成功] 返回分页数据: 共 {total} 条，当前页 {len(items)} 条")
    else:
        # 数组响应
        items = result
        print(f"[成功] 返回数组数据: {len(items)} 条")
    
    # 检查每个项目的组别
    print(f"\n[步骤3] 检查返回项目的组别...")
    non_advanced_count = 0
    advanced_count = 0
    
    for idx, item in enumerate(items[:20], 1):  # 检查前20个
        group_type = item.get('groupType', '未知')
        project_name = item.get('projectName', '未知')
        institution = item.get('institutionName', '未知')
        reg_id = item.get('registrationId', '?')
        
        if group_type != 'ADVANCED':
            non_advanced_count += 1
            print(f"  [{idx}] [警告] ID={reg_id} {project_name[:25]} | 组别={group_type} <- 不是进阶组!")
        else:
            advanced_count += 1
            if idx <= 5:  # 只显示前5个进阶组项目
                print(f"  [{idx}] [正常] ID={reg_id} {project_name[:25]} | 组别=进阶组")
    
    if len(items) > 20:
        print(f"  ... 还有 {len(items) - 20} 个项目未显示")
    
    print(f"\n[统计结果]")
    print(f"  总数: {len(items)}")
    print(f"  进阶组数量: {advanced_count}")
    print(f"  非进阶组数量: {non_advanced_count}")
    
    if non_advanced_count > 0:
        print(f"\n[问题] 发现 {non_advanced_count} 个非进阶组项目！")
        print("  原因分析:")
        print("  1. 可能是前端遗漏了 groupType=ADVANCED 参数")
        print("  2. 可能是后端API的筛选逻辑有问题")
        return False
    else:
        print(f"\n[成功] 所有项目都是进阶组，筛选正确！")
        return True

if __name__ == "__main__":
    try:
        result = test_interview_filter()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n[异常] 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
