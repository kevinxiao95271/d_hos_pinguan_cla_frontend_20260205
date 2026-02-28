#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端服务探测脚本 - 端口6031
测试后端API是否可用
"""

import requests
import json
import sys
from datetime import datetime

# 解决Windows控制台编码问题
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_health_check():
    """测试健康检查接口"""
    print_section("1. 健康检查")
    
    endpoints = [
        "/",
        "/actuator/health",
        "/api/health",
        "/health"
    ]
    
    for endpoint in endpoints:
        url = BASE_URL + endpoint
        print(f"\n[测试] {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
            
            if response.status_code == 200:
                print("  ✅ 端点可用")
                return True
        except requests.exceptions.ConnectionError:
            print(f"  ❌ 连接失败 - 服务未运行")
        except requests.exceptions.Timeout:
            print(f"  ❌ 超时")
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    return False

def test_login_api():
    """测试登录API"""
    print_section("2. 登录API测试")
    
    # 测试用户账号
    test_accounts = [
        {
            "username": "13300005566",
            "password": "123456",
            "desc": "参赛者账号"
        },
        {
            "username": "ops",
            "password": "ops123",
            "desc": "OPS账号"
        },
        {
            "username": "admin",
            "password": "admin123",
            "desc": "管理员账号"
        }
    ]
    
    login_url = f"{BASE_URL}/api/auth/login-with-password"
    
    for account in test_accounts:
        print(f"\n[测试] {account['desc']}: {account['username']}")
        
        try:
            response = requests.post(
                login_url,
                json={
                    "username": account['username'],
                    "password": account['password']
                },
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 登录成功")
                print(f"  响应: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
                
                # 保存token供后续测试使用
                if data.get('success') and data.get('data', {}).get('token'):
                    return data['data']['token']
            else:
                print(f"  ❌ 登录失败")
                print(f"  响应: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ 连接失败")
            return None
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    return None

def test_competitions_api(token=None):
    """测试赛事列表API"""
    print_section("3. 赛事列表API测试")
    
    url = f"{BASE_URL}/api/competitions"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print("[使用Token]")
    else:
        print("[无Token]")
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取成功")
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
            return data
        else:
            print("❌ 获取失败")
            print(f"响应: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    return None

def test_system_templates_api():
    """测试系统模版API（公开接口）"""
    print_section("4. 系统模版API测试（公开接口）")
    
    url = f"{BASE_URL}/api/system-templates/active"
    print(f"[测试] {url}")
    print("[说明] 此接口应该是公开的，无需token")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取成功（公开接口正常）")
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
            return True
        elif response.status_code == 401:
            print("⚠️ 返回401 - 接口未加入白名单")
        else:
            print(f"❌ 状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    return False

def test_registrations_api(token):
    """测试报名列表API"""
    print_section("5. 报名列表API测试")
    
    if not token:
        print("⚠️ 需要token，跳过测试")
        return
    
    url = f"{BASE_URL}/api/admin/registrations/filter"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "competitionId": 21,
        "page": 0,
        "size": 10
    }
    
    print(f"[测试] {url}")
    print(f"[参数] {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取成功")
            
            if data.get('success'):
                content = data.get('data', {}).get('content', [])
                print(f"  返回 {len(content)} 条报名记录")
                
                if len(content) > 0:
                    print(f"\n  第一条记录示例:")
                    first = content[0]
                    print(f"    - 项目ID: {first.get('registrationId')}")
                    print(f"    - 项目名称: {first.get('projectName')}")
                    print(f"    - 医疗机构: {first.get('institutionName')}")
                    print(f"    - 材料数量: {len(first.get('materials', []))}")
            else:
                print(f"  响应: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
        else:
            print("❌ 获取失败")
            print(f"响应: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败")
    except Exception as e:
        print(f"❌ 错误: {e}")

def main():
    """主函数"""
    print("\n" + "="*80)
    print("  后端服务探测脚本")
    print(f"  目标: {BASE_URL}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 1. 健康检查
    if not test_health_check():
        print("\n" + "="*80)
        print("  ❌ 后端服务未运行或端口6031不可用")
        print("="*80)
        print("\n建议：")
        print("  1. 检查后端服务是否启动")
        print("  2. 确认端口是否为6031")
        print("  3. 检查防火墙设置")
        sys.exit(1)
    
    # 2. 登录测试
    token = test_login_api()
    
    # 3. 赛事列表测试
    competitions = test_competitions_api(token)
    
    # 4. 系统模版测试（公开接口）
    test_system_templates_api()
    
    # 5. 报名列表测试
    if token:
        test_registrations_api(token)
    
    # 总结
    print("\n" + "="*80)
    print("  测试完成")
    print("="*80)
    
    if token:
        print("\n✅ 后端服务正常运行")
        print(f"   - 端口: 6031")
        print(f"   - 登录: 正常")
        print(f"   - API: 可用")
    else:
        print("\n⚠️ 后端服务运行中，但登录失败")
        print("   - 可能是账号密码错误")
        print("   - 或数据库未初始化")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
