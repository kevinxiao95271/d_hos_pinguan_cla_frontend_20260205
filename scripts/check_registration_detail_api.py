#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查报名详情API的机构信息字段
测试项目编号70的详情数据
"""

import requests
import json
import io
import sys

# 解决Windows控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def main():
    print("\n" + "="*80)
    print("  报名详情API - 机构信息字段检查")
    print("="*80)
    
    # 1. 登录获取token
    print("\n[步骤1] 登录获取token...")
    login_url = f"{BASE_URL}/api/auth/login-with-password"
    
    try:
        response = requests.post(
            login_url,
            json={
                "phone": "13300005566",
                "password": "test005566"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['token']
                print(f"✅ 登录成功")
            else:
                print(f"❌ 登录失败: {data.get('message')}")
                return
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return
    
    # 2. 获取项目编号70的详情
    print("\n[步骤2] 获取项目编号70的详情...")
    print("\n接口信息:")
    print("  路径: GET /api/registrations/70")
    print("  说明: 获取单个报名的详细信息")
    
    detail_url = f"{BASE_URL}/api/registrations/70"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(detail_url, headers=headers, timeout=10)
        
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 请求成功\n")
            
            # 显示完整响应
            print("="*80)
            print("  完整响应数据（前3000字符）")
            print("="*80)
            print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
            print("\n...")
            
            if data.get('success'):
                detail = data.get('data', {})
                
                print("\n" + "="*80)
                print("  机构信息字段分析")
                print("="*80)
                
                # 检查顶层字段
                print("\n【顶层字段检查】")
                print(f"  institutionName: {detail.get('institutionName', '未找到')}")
                print(f"  institutionLevel: {detail.get('institutionLevel', '未找到')}")
                print(f"  institutionType: {detail.get('institutionType', '未找到')}")
                
                # 检查registration子对象
                if 'registration' in detail:
                    print("\n【registration对象中的字段】")
                    reg = detail['registration']
                    print(f"  institutionName: {reg.get('institutionName', '未找到')}")
                    print(f"  institutionLevel: {reg.get('institutionLevel', '未找到')}")
                    print(f"  institutionType: {reg.get('institutionType', '未找到')}")
                
                # 检查institution子对象
                if 'institution' in detail:
                    print("\n【institution对象中的字段】")
                    inst = detail['institution']
                    print(f"  name: {inst.get('name', '未找到')}")
                    print(f"  level: {inst.get('level', '未找到')}")
                    print(f"  type: {inst.get('type', '未找到')}")
                    print(f"  完整对象: {json.dumps(inst, indent=2, ensure_ascii=False)}")
                else:
                    print("\n【institution对象】")
                    print("  ❌ 不存在 - 后端未返回institution对象")
                
                # 显示所有顶层字段
                print("\n【响应数据的所有顶层字段】")
                for key in sorted(detail.keys()):
                    value = detail[key]
                    if isinstance(value, list):
                        print(f"  {key}: [数组，长度={len(value)}]")
                    elif isinstance(value, dict):
                        print(f"  {key}: {{对象，键={list(value.keys())[:3]}...}}")
                    elif isinstance(value, str) and len(str(value)) > 50:
                        print(f"  {key}: {str(value)[:50]}...")
                    else:
                        print(f"  {key}: {value}")
                
                # 结论
                print("\n" + "="*80)
                print("  结论")
                print("="*80)
                
                has_institution_info = False
                institution_location = []
                
                if detail.get('institutionName'):
                    has_institution_info = True
                    institution_location.append("顶层: institutionName")
                if detail.get('institutionLevel'):
                    has_institution_info = True
                    institution_location.append("顶层: institutionLevel")
                if 'registration' in detail and detail['registration'].get('institutionName'):
                    has_institution_info = True
                    institution_location.append("registration.institutionName")
                if 'registration' in detail and detail['registration'].get('institutionLevel'):
                    has_institution_info = True
                    institution_location.append("registration.institutionLevel")
                if 'institution' in detail:
                    has_institution_info = True
                    institution_location.append("institution对象")
                
                if has_institution_info:
                    print("\n✅ 后端API有返回机构信息")
                    print("\n机构信息位置:")
                    for loc in institution_location:
                        print(f"  - {loc}")
                else:
                    print("\n❌ 后端API未返回机构信息")
                    print("\n可能的原因:")
                    print("  1. 后端DTO未包含institution相关字段")
                    print("  2. 数据库关联查询未执行")
                    print("  3. 该报名记录的institution_id为空")
                
                print("\n建议:")
                if 'institution' not in detail:
                    print("  ⚠️ 后端需要在详情API中返回 'institution' 对象")
                    print("  ⚠️ 该对象应包含: name, level, type 等字段")
                
        else:
            print(f"❌ 请求失败")
            print(f"响应: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
