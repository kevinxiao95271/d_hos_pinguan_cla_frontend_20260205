#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查后端服务状态
"""

import requests
import time

BASE_URL = "http://localhost:6031"

def check_backend():
    print("="*60)
    print("后端服务状态检查")
    print("="*60)
    
    # 1. 检查基础连接
    print("\n[1] 检查基础连接...")
    try:
        response = requests.get(f"{BASE_URL}/actuator/health", timeout=3)
        print(f"    ✓ 健康检查: {response.status_code}")
        if response.status_code == 200:
            print(f"    ✓ 响应: {response.json()}")
    except requests.exceptions.Timeout:
        print("    ✗ 健康检查超时 - 后端可能未启动或响应缓慢")
        return False
    except requests.exceptions.ConnectionError:
        print("    ✗ 无法连接到后端 - 请确认后端服务是否已启动")
        print(f"    ✗ 检查地址: {BASE_URL}")
        return False
    except Exception as e:
        print(f"    ✗ 错误: {str(e)}")
    
    # 2. 检查 Swagger 文档
    print("\n[2] 检查 Swagger 文档...")
    try:
        response = requests.get(f"{BASE_URL}/swagger-ui/index.html", timeout=3)
        if response.status_code == 200:
            print(f"    ✓ Swagger UI 可访问")
            print(f"    ✓ 地址: {BASE_URL}/swagger-ui/index.html")
        else:
            print(f"    ? Swagger UI 状态码: {response.status_code}")
    except Exception as e:
        print(f"    ✗ Swagger UI 不可访问: {str(e)}")
    
    # 3. 快速登录测试
    print("\n[3] 快速登录测试...")
    payload = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN",
        "title": "组委会成员",
        "institutionId": None,
        "reviewerGroupCode": None,
        "interviewGroupCode": None,
        "expertBackground": None
    }
    
    print(f"    → 发送登录请求...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=payload,
            timeout=10  # 10秒超时
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"    ✓ 登录成功! 响应时间: {elapsed:.2f}秒")
                return True
            else:
                print(f"    ✗ 登录失败: {data.get('message')}")
                return False
        else:
            print(f"    ✗ HTTP {response.status_code}")
            print(f"    ✗ 响应: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"    ✗ 登录请求超时! 已等待 {elapsed:.2f}秒")
        print(f"    ✗ 后端可能正在处理大量请求或数据库连接有问题")
        return False
    except requests.exceptions.ConnectionError:
        print(f"    ✗ 连接被拒绝 - 后端服务未启动")
        return False
    except Exception as e:
        print(f"    ✗ 异常: {str(e)}")
        return False

def main():
    print("\n[INFO] Starting backend service check...\n")
    
    is_healthy = check_backend()
    
    print("\n" + "="*60)
    if is_healthy:
        print("[OK] Backend service is running normally")
        print("="*60)
        print("\nSuggestions:")
        print("  - Refresh frontend page and retry login")
        print("  - Check network connection if still timeout")
    else:
        print("[ERROR] Backend service is NOT running")
        print("="*60)
        print("\nPlease check:")
        print("  1. Is backend service started?")
        print("     Command: cd D:\\AiCode\\traegj\\d_hos_pinguan_traegj_backend_20260205")
        print("     Command: mvn spring-boot:run")
        print("  2. Is port 6031 occupied by other process?")
        print("  3. Is database connection working?")
        print("  4. Check backend logs for errors")
        print("\nAfter starting backend, wait 10-30 seconds, then retry login")

if __name__ == "__main__":
    main()
