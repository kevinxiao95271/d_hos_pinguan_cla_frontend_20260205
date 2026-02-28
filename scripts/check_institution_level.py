#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查书审分组列表API中的机构等级字段
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
    print("  书审分组列表 - 机构等级字段检查")
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
                print(f"角色: {data['data'].get('role', 'N/A')}")
            else:
                print(f"❌ 登录失败: {data.get('message')}")
                return
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return
    
    # 2. 调用报名列表API
    print("\n[步骤2] 调用书审分组列表API...")
    print("\n接口信息:")
    print("  路径: GET /api/admin/registrations/filter")
    print("  参数: competitionId=1, page=0, size=5")
    
    list_url = f"{BASE_URL}/api/admin/registrations/filter"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "competitionId": 1,
        "page": 0,
        "size": 5
    }
    
    try:
        response = requests.get(list_url, headers=headers, params=params, timeout=10)
        
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 请求成功\n")
            
            # 显示响应结构
            print("="*80)
            print("  响应数据结构")
            print("="*80)
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
            
            # 分析第一条数据
            if data.get('success'):
                # data可能是数组或带content的对象
                raw_data = data.get('data', [])
                if isinstance(raw_data, dict):
                    content = raw_data.get('content', [])
                else:
                    content = raw_data if isinstance(raw_data, list) else []
                
                if len(content) > 0:
                    print("\n" + "="*80)
                    print("  第一条报名记录详细分析")
                    print("="*80)
                    
                    first = content[0]
                    
                    print("\n【关键字段】")
                    print(f"  registrationId: {first.get('registrationId')}")
                    print(f"  projectName: {first.get('projectName')}")
                    print(f"  institutionName: {first.get('institutionName')}")
                    print(f"  institutionLevel: {first.get('institutionLevel')}  ← 机构等级字段")
                    
                    print("\n【字段说明】")
                    print("  字段名称: institutionLevel")
                    print(f"  字段值: '{first.get('institutionLevel')}'")
                    print(f"  字段类型: {type(first.get('institutionLevel')).__name__}")
                    print(f"  是否为空: {'是' if not first.get('institutionLevel') else '否'}")
                    
                    print("\n【完整字段列表】")
                    for key in sorted(first.keys()):
                        value = first[key]
                        if isinstance(value, list):
                            print(f"  {key}: [数组，长度={len(value)}]")
                        elif isinstance(value, dict):
                            print(f"  {key}: {{对象}}")
                        else:
                            print(f"  {key}: {value}")
                    
                    print("\n" + "="*80)
                    print("  结论")
                    print("="*80)
                    print(f"\n✅ 机构等级来源:")
                    print(f"   接口: GET /api/admin/registrations/filter")
                    print(f"   字段位置: data.content[i].institutionLevel")
                    print(f"   字段名称: institutionLevel")
                    print(f"   示例值: '{first.get('institutionLevel')}'")
                    print(f"   数据类型: 字符串")
                    
                    # 检查其他记录
                    print(f"\n【其他记录的机构等级】")
                    for i, record in enumerate(content[:5]):
                        level = record.get('institutionLevel', '未设置')
                        print(f"  记录{i+1}: {record.get('institutionName')} - {level}")
                    
                else:
                    print("\n⚠️ 返回的数据为空")
            else:
                print(f"\n❌ 响应失败: {data.get('message')}")
                
        else:
            print(f"❌ 请求失败")
            print(f"响应: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    main()
