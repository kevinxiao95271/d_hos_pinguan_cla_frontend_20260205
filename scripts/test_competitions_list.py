#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试赛事列表接口 - 诊断报名时间和当前阶段显示问题
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_competitions_list():
    """测试赛事列表接口"""
    print("=" * 80)
    print("测试赛事列表接口 - GET /api/competitions")
    print("=" * 80)
    
    # 1. 登录获取token（可选，取决于接口是否需要认证）
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
    
    # 2. 获取赛事列表
    print("\n[2] 获取赛事列表...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # 测试1: 不带参数
        print("\n测试1: GET /api/competitions (不带参数)")
        resp = requests.get(
            f"{BASE_URL}/api/competitions",
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        if not result.get('success'):
            print(f"[ERROR] 请求失败: {result.get('message')}")
            return
        
        competitions = result.get('data', [])
        print(f"[OK] 获取成功！共 {len(competitions)} 个赛事")
        
        # 3. 分析数据结构
        print("\n[3] 分析数据结构...")
        if not competitions:
            print("[WARNING] 赛事列表为空")
            return
        
        print(f"\n共找到 {len(competitions)} 个赛事：")
        print("-" * 80)
        
        for idx, comp in enumerate(competitions, 1):
            print(f"\n赛事 #{idx}:")
            print(f"  ID: {comp.get('id')}")
            print(f"  名称: {comp.get('name')}")
            print(f"  当前阶段: {comp.get('currentStage')} {get_stage_label(comp.get('currentStage'))}")
            
            # 报名时间
            reg_start = comp.get('registrationStartTime') or comp.get('registerStart')
            reg_end = comp.get('registrationEndTime') or comp.get('registerEnd')
            print(f"  报名开始时间: {reg_start if reg_start else '[缺失]'}")
            print(f"  报名结束时间: {reg_end if reg_end else '[缺失]'}")
            
            # 其他阶段时间
            book_start = comp.get('bookReviewStart') or comp.get('bookStart')
            book_end = comp.get('bookReviewEnd') or comp.get('bookEnd')
            print(f"  书审时间: {book_start} ~ {book_end}")
            
            interview_start = comp.get('interviewStart')
            interview_end = comp.get('interviewEnd')
            print(f"  面谈时间: {interview_start} ~ {interview_end}")
            
            final_start = comp.get('finalStart')
            final_end = comp.get('finalEnd')
            print(f"  决赛时间: {final_start} ~ {final_end}")
            
            print(f"  创建时间: {comp.get('createdAt')}")
        
        # 4. 检查字段缺失
        print("\n[4] 字段检查...")
        sample = competitions[0]
        
        expected_fields = [
            'id', 'name', 'currentStage',
            'registrationStartTime', 'registrationEndTime',
            'bookReviewStart', 'bookReviewEnd',
            'interviewStart', 'interviewEnd',
            'finalStart', 'finalEnd'
        ]
        
        # 检查可能的字段名变体
        alternative_fields = [
            'registerStart', 'registerEnd',
            'bookStart', 'bookEnd'
        ]
        
        print("\n期望字段检查：")
        for field in expected_fields:
            exists = field in sample
            value = sample.get(field)
            print(f"  {field}: {'[OK]' if exists else '[MISSING]'} = {value}")
        
        print("\n备选字段检查：")
        for field in alternative_fields:
            if field in sample:
                value = sample.get(field)
                print(f"  {field}: [FOUND] = {value}")
        
        # 5. 完整JSON输出
        print("\n[5] 第一个赛事的完整数据：")
        print("-" * 80)
        print(json.dumps(sample, indent=2, ensure_ascii=False))
        print("-" * 80)
        
        # 6. 诊断结果
        print("\n[6] 诊断结果...")
        
        has_reg_time = bool(sample.get('registrationStartTime') or sample.get('registerStart'))
        has_stage = bool(sample.get('currentStage'))
        
        if not has_reg_time:
            print("\n[问题] 报名时间字段缺失！")
            print("  可能原因：")
            print("    1. 后端未设置报名时间")
            print("    2. 字段名不匹配（应为 registrationStartTime/registrationEndTime）")
            print("  解决方案：")
            print("    - 检查后端 Competition 实体字段名")
            print("    - 确保创建赛事时设置了报名时间")
        else:
            print("\n[OK] 报名时间字段存在")
        
        if not has_stage:
            print("\n[问题] 当前阶段字段缺失！")
            print("  解决方案：")
            print("    - 确保后端返回 currentStage 字段")
        else:
            print(f"\n[OK] 当前阶段字段存在: {sample.get('currentStage')}")
        
        # 7. 前端代码检查
        print("\n[7] 前端代码说明...")
        print("""
前端代码路径：src/views/contestant/Competitions.vue

数据获取：
  const res = await getCompetitions()  // 调用 GET /api/competitions
  competitions.value = res.data || []

显示逻辑：
  报名时间：formatDateRange(item.registrationStartTime, item.registrationEndTime)
  当前阶段：getStageText(item.currentStage)

formatDateRange 函数：
  if (!start || !end) return '-'  // ← 如果时间为空，返回 '-'
  
getStageText 函数：
  返回阶段中文名称，如果 currentStage 为空则返回原值
""")
        
    except Exception as e:
        print(f"[ERROR] 获取赛事列表异常: {e}")
        import traceback
        traceback.print_exc()

def get_stage_label(stage):
    """获取阶段中文标签"""
    stage_map = {
        'REGISTRATION': '(报名中)',
        'BOOK': '(书审中)',
        'INTERVIEW': '(面谈中)',
        'FINAL': '(决赛中)'
    }
    return stage_map.get(stage, '')

if __name__ == '__main__':
    test_competitions_list()
