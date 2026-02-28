#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试品管工具筛选功能
"""

import requests
import json
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def main():
    print("\n" + "="*80)
    print("  品管工具筛选功能测试")
    print("="*80)
    
    # 1. 登录
    print("\n[步骤1] 登录...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login-with-password",
            json={"phone": "13300005566", "password": "test005566"},
            timeout=10
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
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 获取字典数据（品管工具）
    print("\n[步骤2] 获取品管工具字典...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/dictionaries/method",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                methods = data['data']
                print(f"✅ 获取到 {len(methods)} 个品管工具")
                print("\n品管工具列表:")
                for item in methods[:5]:
                    print(f"  - code: {item.get('code')}, label: {item.get('label')}")
                
                # 选择第一个进行测试
                if len(methods) > 0:
                    test_method = methods[0]
                    print(f"\n选择用于测试: code='{test_method['code']}', label='{test_method['label']}'")
                else:
                    print("⚠️ 没有品管工具数据")
                    return
            else:
                print(f"⚠️ 获取失败")
                return
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 异常: {e}")
        return
    
    # 3. 测试不同的参数名
    print("\n" + "="*80)
    print("  测试不同参数名的筛选效果")
    print("="*80)
    
    test_cases = [
        ("无筛选参数", {}),
        ("使用 methodCode (代码)", {"methodCode": test_method['code']}),
        ("使用 methodLabel (标签)", {"methodLabel": test_method['label']}),
        ("使用 method (简写)", {"method": test_method['code']}),
    ]
    
    for test_name, params in test_cases:
        print(f"\n【测试】{test_name}")
        print(f"  参数: {json.dumps(params, ensure_ascii=False)}")
        
        try:
            # 构建完整参数
            full_params = {
                "competitionId": 1,
                "page": 0,
                "size": 10,
                **params
            }
            
            response = requests.get(
                f"{BASE_URL}/api/admin/registrations/filter",
                headers={"Authorization": f"Bearer {token}"},
                params=full_params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    # 处理响应数据
                    raw_data = data.get('data', [])
                    if isinstance(raw_data, dict):
                        content = raw_data.get('content', [])
                        total = raw_data.get('totalElements', 0)
                    else:
                        content = raw_data if isinstance(raw_data, list) else []
                        total = len(content)
                    
                    print(f"  ✅ 状态码: 200")
                    print(f"  ✅ 返回数据: {len(content)} 条 (总计: {total})")
                    
                    # 显示前3条的品管工具信息
                    if len(content) > 0:
                        print(f"  前{min(3, len(content))}条数据的品管工具:")
                        for i, item in enumerate(content[:3]):
                            method_label = item.get('methodLabel', '未设置')
                            method_code = item.get('methodCode', '未设置')
                            project_name = item.get('projectName', '未知项目')
                            print(f"    [{i+1}] {project_name[:30]}: methodLabel='{method_label}', methodCode='{method_code}'")
                else:
                    print(f"  ❌ 响应失败: {data.get('message')}")
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
    
    # 4. 验证筛选逻辑
    print("\n" + "="*80)
    print("  筛选逻辑验证")
    print("="*80)
    
    print(f"\n✅ 结论:")
    print(f"  1. 查看上述各测试的返回数量")
    print(f"  2. 如果 methodCode 返回数量 < 无筛选数量，说明后端支持 methodCode")
    print(f"  3. 如果 methodLabel 返回数量 < 无筛选数量，说明后端支持 methodLabel")
    print(f"  4. 如果两者返回数量相同，说明筛选未生效")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
