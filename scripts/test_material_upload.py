#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试材料上传功能
"""

import requests
import json
import io
import sys
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def main():
    print("\n" + "="*80)
    print("  材料上传功能测试")
    print("="*80)
    
    # 1. 登录
    print("\n[步骤1] 登录...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login-with-password",
            json={"phone": "13100009911", "password": "test009911"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['token']
                role = data['data'].get('role')
                print(f"✅ 登录成功 (角色: {role})")
            else:
                print(f"❌ 登录失败: {data.get('message')}")
                return
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 获取我的报名列表
    print("\n[步骤2] 获取我的报名列表...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/registrations/my",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                registrations = data['data']
                print(f"✅ 找到 {len(registrations)} 条报名记录")
                
                if len(registrations) > 0:
                    reg = registrations[0]
                    reg_id = reg.get('id')
                    project_name = reg.get('projectName', '未命名')
                    status = reg.get('status', '未知')
                    print(f"\n第一条报名:")
                    print(f"  ID: {reg_id}")
                    print(f"  项目名称: {project_name}")
                    print(f"  状态: {status}")
                    
                    # 3. 测试不同的上传路径
                    print("\n[步骤3] 测试材料上传接口路径...")
                    
                    # 创建一个测试文件
                    test_file_content = b"This is a test file"
                    
                    test_paths = [
                        f"/api/materials/upload/{reg_id}",
                        f"/api/materials/{reg_id}/upload",
                        f"/api/registrations/{reg_id}/materials",
                        f"/api/registrations/{reg_id}/materials/upload",
                    ]
                    
                    for path in test_paths:
                        print(f"\n测试路径: {path}")
                        
                        files = {'file': ('test.pdf', test_file_content, 'application/pdf')}
                        
                        try:
                            response = requests.post(
                                f"{BASE_URL}{path}",
                                headers={"Authorization": f"Bearer {token}"},
                                files=files,
                                timeout=10
                            )
                            
                            print(f"  状态码: {response.status_code}")
                            
                            if response.status_code == 200:
                                result = response.json()
                                print(f"  ✅ 成功: {json.dumps(result, ensure_ascii=False)}")
                                print(f"\n  >>> 找到正确路径: {path}")
                                break
                            elif response.status_code == 404:
                                print(f"  ❌ 404 接口不存在")
                            elif response.status_code == 400:
                                result = response.json()
                                print(f"  ⚠️ 400 请求错误: {result.get('message', 'N/A')}")
                            elif response.status_code == 500:
                                print(f"  ❌ 500 服务器错误")
                            else:
                                print(f"  状态码: {response.status_code}")
                                print(f"  响应: {response.text[:200]}")
                        except Exception as e:
                            print(f"  ❌ 异常: {e}")
                else:
                    print("⚠️ 没有报名记录")
            else:
                print(f"⚠️ 无数据")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("  测试完成")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
