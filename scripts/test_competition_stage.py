#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断赛事阶段字段问题
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_competition_stage():
    """测试赛事阶段字段"""
    print("=" * 80)
    print("诊断赛事阶段 (stage) 字段")
    print("=" * 80)
    
    # 1. 登录
    print("\n[1] 登录...")
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
    
    # 2. 获取赛事列表
    print("\n[2] 获取赛事列表...")
    try:
        resp = requests.get(
            f"{BASE_URL}/api/competitions",
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        if not result.get('success'):
            print(f"[ERROR] 获取失败")
            return
        
        competitions = result.get('data', [])
        print(f"[OK] 获取到 {len(competitions)} 个赛事\n")
        
        # 3. 检查每个赛事的 stage 字段
        print("-" * 80)
        for idx, comp in enumerate(competitions, 1):
            comp_id = comp.get('id')
            comp_name = comp.get('name')
            stage = comp.get('stage')
            register_start = comp.get('registerStart')
            register_end = comp.get('registerEnd')
            
            print(f"\n赛事 #{idx}: {comp_name} (ID={comp_id})")
            print(f"  stage 字段: {stage}")
            print(f"  stage 类型: {type(stage)}")
            print(f"  stage 是否为空: {'是' if stage is None else '否'}")
            print(f"  报名开始: {register_start}")
            print(f"  报名结束: {register_end}")
            
            # 判断前端按钮状态
            if stage is None:
                print(f"  [问题] stage 为 None!")
                print(f"  前端判断: canRegister = False (stage !== 'REGISTER')")
                print(f"  按钮状态: 禁用 (灰色)")
            elif stage == 'REGISTER':
                print(f"  [正常] stage = 'REGISTER'")
                print(f"  前端判断: canRegister = True")
                print(f"  按钮状态: 可用 (蓝色)")
            else:
                print(f"  [正常] stage = '{stage}'")
                print(f"  前端判断: canRegister = False (非报名阶段)")
                print(f"  按钮状态: 禁用 (显示'报名已结束')")
        
        # 4. 统计
        print("\n" + "=" * 80)
        print("[4] 统计结果")
        print("=" * 80)
        
        null_stage_count = sum(1 for c in competitions if c.get('stage') is None)
        register_stage_count = sum(1 for c in competitions if c.get('stage') == 'REGISTER')
        other_stage_count = len(competitions) - null_stage_count - register_stage_count
        
        print(f"\n总赛事数: {len(competitions)}")
        print(f"stage = 'REGISTER': {register_stage_count} 个  (按钮可用)")
        print(f"stage = None: {null_stage_count} 个  (按钮禁用 ← 问题!)")
        print(f"其他阶段: {other_stage_count} 个  (按钮禁用)")
        
        if null_stage_count > 0:
            print("\n[问题诊断]")
            print("  stage 字段为 None 的赛事会导致按钮被禁用！")
            print("\n原因:")
            print("  前端判断逻辑:")
            print("    canRegister = item.stage === 'REGISTER' && !isRegistered(item.id)")
            print("    disabled = !canRegister && !isRegistered")
            print("\n  当 stage = None 时:")
            print("    None === 'REGISTER' → false")
            print("    canRegister = false")
            print("    如果未报名: !canRegister && !isRegistered = true && true = true")
            print("    所以按钮被禁用!")
            print("\n解决方案:")
            print("  方案1: 后端修复 - 更新 stage 字段为 'REGISTER' (推荐)")
            print("  方案2: 前端容错 - 当 stage 为 None 且在报名时间内，判断为可报名")
            
            # 输出SQL修复建议
            print("\n后端SQL修复建议:")
            for comp in competitions:
                if comp.get('stage') is None:
                    print(f"  UPDATE competition SET stage = 'REGISTER' WHERE id = {comp.get('id')};  -- {comp.get('name')}")
        
    except Exception as e:
        print(f"[ERROR] 异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_competition_stage()
