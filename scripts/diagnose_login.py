#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录过期问题诊断脚本
用于测试后端 Token 的有效期和 API 响应
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:6031/api"

class LoginDiagnostics:
    def __init__(self):
        self.token = None
        self.login_time = None
        
    def log(self, message, level="INFO"):
        """打印带时间戳的日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        symbol = "[OK]" if level == "SUCCESS" else "[ERROR]" if level == "ERROR" else "[INFO]"
        try:
            print(f"[{timestamp}] {symbol} {message}")
        except UnicodeEncodeError:
            print(f"[{timestamp}] {symbol} {message.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')}")
    
    def test_login(self, phone, name, role, **kwargs):
        """测试登录"""
        self.log(f"开始登录测试 - {role}")
        
        payload = {
            "phone": phone,
            "name": name,
            "role": role,
            "title": kwargs.get("title", "测试用户"),
            "institutionId": kwargs.get("institutionId"),
            "reviewerGroupCode": kwargs.get("reviewerGroupCode"),
            "interviewGroupCode": kwargs.get("interviewGroupCode"),
            "expertBackground": kwargs.get("expertBackground")
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    self.token = data["data"].get("token")
                    self.login_time = datetime.now()
                    self.log(f"登录成功! Token: {self.token[:30]}...", "SUCCESS")
                    self.log(f"登录时间: {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}", "SUCCESS")
                    return True
                else:
                    self.log(f"登录失败: {data.get('message', '未知错误')}", "ERROR")
                    return False
            else:
                self.log(f"登录失败: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"登录异常: {str(e)}", "ERROR")
            return False
    
    def test_token_validity(self, api_path="/competitions"):
        """测试 Token 有效性"""
        if not self.token:
            self.log("未登录，无法测试 Token", "ERROR")
            return False
        
        self.log(f"测试 Token 有效性 - {api_path}")
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{BASE_URL}{api_path}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log("Token 有效", "SUCCESS")
                return True
            elif response.status_code == 401:
                elapsed = datetime.now() - self.login_time
                self.log(f"Token 已过期! 有效期: {elapsed}", "ERROR")
                return False
            else:
                self.log(f"API 调用失败: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"测试异常: {str(e)}", "ERROR")
            return False
    
    def monitor_token_expiry(self, interval=60, max_duration=3600):
        """监控 Token 过期时间"""
        if not self.token:
            self.log("未登录，无法监控", "ERROR")
            return
        
        self.log(f"开始监控 Token 有效期（每 {interval} 秒检查一次，最多 {max_duration} 秒）")
        
        start_time = datetime.now()
        check_count = 0
        
        while True:
            elapsed = (datetime.now() - self.login_time).total_seconds()
            
            if elapsed > max_duration:
                self.log(f"已达到最大监控时间 {max_duration} 秒", "INFO")
                break
            
            check_count += 1
            self.log(f"第 {check_count} 次检查（已登录 {int(elapsed)} 秒）")
            
            if not self.test_token_validity():
                self.log(f"Token 在 {elapsed:.0f} 秒后过期", "ERROR")
                break
            
            time.sleep(interval)
    
    def comprehensive_test(self):
        """综合测试"""
        self.log("=" * 60)
        self.log("开始综合诊断测试")
        self.log("=" * 60)
        
        # 测试账号
        test_accounts = [
            {
                "phone": "13800000041",
                "name": "CommitteeAdmin A",
                "role": "COMMITTEE_ADMIN",
                "title": "组委会成员"
            },
            {
                "phone": "13800000011",
                "name": "Contestant A",
                "role": "CONTESTANT",
                "institutionId": 1,
                "title": "项目负责人"
            }
        ]
        
        for account in test_accounts:
            self.log(f"\n测试账号: {account['name']} ({account['role']})")
            
            if self.test_login(**account):
                # 立即测试
                self.test_token_validity()
                
                # 等待 30 秒后再次测试
                self.log("等待 30 秒后再次测试...")
                time.sleep(30)
                self.test_token_validity()
                
                # 等待 60 秒后再次测试
                self.log("等待 60 秒后再次测试...")
                time.sleep(30)  # 已经等了 30 秒，再等 30 秒就是 60 秒
                is_valid = self.test_token_validity()
                
                if is_valid:
                    self.log(f"Token 在 60 秒后仍然有效", "SUCCESS")
                else:
                    self.log(f"Token 在 60 秒内过期", "ERROR")
                
                self.log("-" * 60)
                break  # 只测试第一个成功登录的账号


def main():
    import sys
    
    print("=" * 60)
    print("Login Expiry Diagnostics Tool")
    print("=" * 60)
    
    diagnostics = LoginDiagnostics()
    
    # 支持命令行参数
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("请选择测试模式:")
        print("1. 快速测试（登录 + 立即验证）")
        print("2. 短期监控（60 秒）")
        print("3. 长期监控（10 分钟）")
        print("4. 综合测试（推荐）")
        
        try:
            choice = input("\n请输入选项 (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n使用默认选项: 1 (快速测试)")
            choice = "1"
    
    if choice == "1":
        # 快速测试
        if diagnostics.test_login(
            phone="13800000041",
            name="CommitteeAdmin A",
            role="COMMITTEE_ADMIN",
            title="组委会成员"
        ):
            diagnostics.test_token_validity()
            
    elif choice == "2":
        # 短期监控
        if diagnostics.test_login(
            phone="13800000041",
            name="CommitteeAdmin A",
            role="COMMITTEE_ADMIN",
            title="组委会成员"
        ):
            diagnostics.monitor_token_expiry(interval=10, max_duration=60)
            
    elif choice == "3":
        # 长期监控
        if diagnostics.test_login(
            phone="13800000041",
            name="CommitteeAdmin A",
            role="COMMITTEE_ADMIN",
            title="组委会成员"
        ):
            diagnostics.monitor_token_expiry(interval=30, max_duration=600)
            
    elif choice == "4":
        # 综合测试
        diagnostics.comprehensive_test()
        
    else:
        print("无效的选项")


if __name__ == "__main__":
    main()
