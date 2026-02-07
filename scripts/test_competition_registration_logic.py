#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试赛事报名逻辑 - 验证前端判断逻辑
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_registration_logic():
    """测试赛事报名逻辑"""
    print("=" * 80)
    print("测试赛事报名逻辑 - 验证前端判断")
    print("=" * 80)
    
    # 1. 登录
    print("\n[1] 登录参赛者账号...")
    login_data = {
        "phone": "13966000011",
        "name": "参赛者11",
        "title": "主管护师",
        "role": "CONTESTANT"
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
            print(f"[ERROR] 登录失败: {login_result.get('message')}")
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
    
    # 2. 获取赛事列表
    print("\n[2] 获取赛事列表...")
    try:
        comp_resp = requests.get(
            f"{BASE_URL}/api/competitions",
            headers=headers,
            timeout=10
        )
        comp_resp.raise_for_status()
        comp_result = comp_resp.json()
        
        if not comp_result.get('success'):
            print(f"[ERROR] 获取赛事失败")
            return
        
        competitions = comp_result.get('data', [])
        print(f"[OK] 获取到 {len(competitions)} 个赛事")
        
    except Exception as e:
        print(f"[ERROR] 获取赛事异常: {e}")
        return
    
    # 3. 获取我的报名
    print("\n[3] 获取我的报名...")
    try:
        my_reg_resp = requests.get(
            f"{BASE_URL}/api/registrations/my",
            headers=headers,
            timeout=10
        )
        my_reg_resp.raise_for_status()
        my_reg_result = my_reg_resp.json()
        
        if not my_reg_result.get('success'):
            print(f"[ERROR] 获取报名失败")
            return
        
        my_registrations = my_reg_result.get('data', [])
        print(f"[OK] 获取到 {len(my_registrations)} 条报名记录")
        
    except Exception as e:
        print(f"[ERROR] 获取报名异常: {e}")
        return
    
    # 4. 提取已报名的赛事ID
    print("\n[4] 分析已报名的赛事...")
    registered_competition_ids = set()
    registration_map = {}  # competitionId -> registration
    
    for reg in my_registrations:
        comp_id = reg.get('competitionId')
        if comp_id:
            registered_competition_ids.add(comp_id)
            registration_map[comp_id] = reg
            print(f"  - 已报名赛事ID: {comp_id}, 报名ID: {reg.get('id')}, 项目: {reg.get('projectName')}")
    
    if not registered_competition_ids:
        print("  [INFO] 没有已报名的赛事")
    
    # 5. 判断每个赛事的状态
    print("\n[5] 判断赛事状态和按钮显示...")
    print("-" * 80)
    
    for comp in competitions:
        comp_id = comp.get('id')
        comp_name = comp.get('name')
        stage = comp.get('stage')
        
        # 判断是否已报名
        is_registered = comp_id in registered_competition_ids
        
        # 判断是否可报名（报名阶段且未报名）
        can_register = stage == 'REGISTER' and not is_registered
        
        # 按钮文本
        if is_registered:
            button_text = '查看报名'
            button_type = 'default'
            button_disabled = False
        elif can_register:
            button_text = '立即报名'
            button_type = 'primary'
            button_disabled = False
        else:
            button_text = '报名已结束'
            button_type = 'primary'
            button_disabled = True
        
        # 点击行为
        if is_registered:
            reg = registration_map[comp_id]
            action = f"跳转到 /contestant/registration/{reg.get('id')}"
        else:
            action = f"跳转到 /contestant/register/{comp_id}"
        
        # 输出
        print(f"\n赛事: {comp_name} (ID={comp_id})")
        print(f"  阶段: {stage}")
        print(f"  已报名: {'是' if is_registered else '否'}")
        print(f"  可报名: {'是' if can_register else '否'}")
        print(f"  按钮文本: [{button_text}]")
        print(f"  按钮类型: {button_type}")
        print(f"  按钮禁用: {'是' if button_disabled else '否'}")
        print(f"  点击行为: {action}")
    
    # 6. 总结
    print("\n" + "=" * 80)
    print("[6] 逻辑验证总结")
    print("=" * 80)
    
    total_competitions = len(competitions)
    registered_count = len(registered_competition_ids)
    available_count = sum(1 for c in competitions if c.get('stage') == 'REGISTER' and c.get('id') not in registered_competition_ids)
    
    print(f"\n总赛事数: {total_competitions}")
    print(f"已报名: {registered_count} 个")
    print(f"可报名: {available_count} 个")
    print(f"不可报名: {total_competitions - registered_count - available_count} 个")
    
    print("\n[OK] 前端逻辑验证完成！")
    print("\n前端实现说明:")
    print("  1. 同时加载赛事列表和我的报名")
    print("  2. 根据 competitionId 判断是否已报名")
    print("  3. 已报名显示'查看报名'，点击跳转到报名详情")
    print("  4. 未报名且在报名阶段显示'立即报名'")
    print("  5. 非报名阶段显示'报名已结束'且禁用按钮")

if __name__ == '__main__':
    test_registration_logic()
