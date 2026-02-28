#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试材料上传的正确路径
"""

import requests
import json
import io
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def main():
    print("\n" + "="*80)
    print("  材料上传路径测试")
    print("="*80)
    
    # 1. 登录
    print("\n[步骤1] 登录...")
    max_retries = 3
    token = None
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login-with-password",
                json={"phone": "13100009911", "password": "test009911"},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    token = data['data']['token']
                    role = data['data'].get('role')
                    print(f"✅ 登录成功 (角色: {role})")
                    break
                else:
                    print(f"❌ 登录失败: {data.get('message')}")
                    return
            else:
                print(f"❌ 登录失败，状态码: {response.status_code}")
                return
        except requests.exceptions.Timeout:
            print(f"⚠️ 登录超时 (尝试 {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("❌ 登录失败，超过最大重试次数")
                return
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return
    
    if not token:
        return
    
    # 2. 获取报名ID
    print("\n[步骤2] 获取报名ID...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/registrations/my",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data') and len(data['data']) > 0:
                reg = data['data'][0]
                reg_id = reg.get('id')
                project_name = reg.get('projectName', '未命名')
                status = reg.get('status', '未知')
                print(f"✅ 找到报名记录")
                print(f"  ID: {reg_id}")
                print(f"  项目名称: {project_name}")
                print(f"  状态: {status}")
            else:
                print("❌ 没有报名记录")
                return
        else:
            print(f"❌ 获取报名失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 异常: {e}")
        return
    
    # 3. 测试不同的上传路径
    print("\n[步骤3] 测试材料上传路径...")
    print("="*80)
    
    # 创建测试文件
    test_content = b"Test PDF content"
    
    test_cases = [
        ("前端当前使用", f"/api/materials/upload/{reg_id}"),
        ("文档中的路径1", f"/api/registrations/{reg_id}/materials"),
        ("文档中的路径2", f"/api/registrations/{reg_id}/materials/upload"),
        ("简化路径1", f"/api/materials/{reg_id}"),
        ("简化路径2", f"/api/materials/{reg_id}/upload"),
    ]
    
    for name, path in test_cases:
        print(f"\n【{name}】")
        print(f"  路径: POST {path}")
        
        files = {'file': ('test.pdf', test_content, 'application/pdf')}
        
        try:
            response = requests.post(
                f"{BASE_URL}{path}",
                headers={"Authorization": f"Bearer {token}"},
                files=files,
                timeout=15
            )
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ 成功！")
                print(f"  响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                print(f"\n  >>> 找到正确路径: {path}")
                break
            elif response.status_code == 404:
                print(f"  ❌ 404 - 接口不存在")
            elif response.status_code == 400:
                try:
                    result = response.json()
                    print(f"  ⚠️ 400 - 请求错误: {result.get('message', 'N/A')}")
                except:
                    print(f"  ⚠️ 400 - {response.text[:100]}")
            elif response.status_code == 500:
                print(f"  ❌ 500 - 服务器错误")
                try:
                    result = response.json()
                    print(f"  错误: {result.get('message', 'N/A')}")
                except:
                    print(f"  错误: {response.text[:200]}")
            else:
                print(f"  状态码: {response.status_code}")
                print(f"  响应: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
    
    print("\n" + "="*80)
    print("  测试完成")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
