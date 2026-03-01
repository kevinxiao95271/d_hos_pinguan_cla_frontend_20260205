#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OPS角色的用户管理和报名列表API
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:6031/api"
LOGIN_DATA = {
    "phone": "13800000005",
    "password": "ops2026"
}

class APITester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        
    def login(self):
        """登录获取token"""
        print("\n" + "="*60)
        print("1. 测试登录API")
        print("="*60)
        
        url = f"{BASE_URL}/auth/login-with-password"
        try:
            response = self.session.post(url, json=LOGIN_DATA, timeout=60)
            print(f"请求URL: {url}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('data', {}).get('token')
                    print(f"✅ 登录成功")
                    print(f"Token: {self.token[:50]}..." if self.token else "无Token")
                    
                    # 设置请求头
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}',
                        'Content-Type': 'application/json'
                    })
                    return True
                else:
                    print(f"❌ 登录失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 登录失败: HTTP {response.status_code}")
                print(f"响应: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {str(e)}")
            return False
    
    def test_user_statistics(self):
        """测试用户统计API"""
        print("\n" + "="*60)
        print("2. 测试用户统计API")
        print("="*60)
        
        url = f"{BASE_URL}/admin/users/statistics"
        try:
            response = self.session.get(url, timeout=60)
            print(f"请求URL: {url}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data.get('data', {})
                    print(f"✅ 用户统计API正常")
                    print(f"   总用户数: {stats.get('totalUsers', 0)}")
                    print(f"   参赛者: {stats.get('contestants', 0)} (启用: {stats.get('contestantsEnabled', 0)})")
                    print(f"   评委: {stats.get('reviewers', 0)} (启用: {stats.get('reviewersEnabled', 0)})")
                    print(f"   已禁用: {stats.get('disabledUsers', 0)}")
                    return True
                else:
                    print(f"❌ API返回失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"响应: {response.text[:500]}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return False
    
    def test_query_users(self):
        """测试查询用户列表API"""
        print("\n" + "="*60)
        print("3. 测试查询用户列表API")
        print("="*60)
        
        url = f"{BASE_URL}/admin/users/query"
        payload = {
            "page": 0,
            "size": 20
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=60)
            print(f"请求URL: {url}")
            print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('data', {})
                    users = result.get('content', [])
                    total = result.get('totalElements', 0)
                    
                    print(f"✅ 用户列表API正常")
                    print(f"   总记录数: {total}")
                    print(f"   当前页记录: {len(users)}")
                    
                    if users:
                        print(f"\n   前3条用户数据:")
                        for i, user in enumerate(users[:3], 1):
                            print(f"   [{i}] ID:{user.get('id')} | {user.get('name')} | {user.get('phone')} | {user.get('role')} | {'启用' if user.get('enabled') else '禁用'}")
                    
                    return True
                else:
                    print(f"❌ API返回失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"响应: {response.text[:500]}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return False
    
    def test_filter_registrations(self):
        """测试筛选报名列表API"""
        print("\n" + "="*60)
        print("4. 测试筛选报名列表API")
        print("="*60)
        
        # 先获取赛事列表
        competitions_url = f"{BASE_URL}/competitions"
        try:
            comp_response = self.session.get(competitions_url, timeout=60)
            competitions = []
            competition_id = None
            
            if comp_response.status_code == 200:
                comp_data = comp_response.json()
                if comp_data.get('success'):
                    competitions = comp_data.get('data', [])
                    if competitions:
                        competition_id = competitions[0].get('id')
                        print(f"   找到赛事: {competitions[0].get('name')} (ID: {competition_id})")
            
            if not competition_id:
                print("⚠️  未找到赛事，使用默认ID=1测试")
                competition_id = 1
            
        except Exception as e:
            print(f"⚠️  获取赛事列表失败: {str(e)}，使用默认ID=1")
            competition_id = 1
        
        # 测试报名列表API
        url = f"{BASE_URL}/admin/registrations/filter"
        params = {
            "competitionId": competition_id,
            "page": 0,
            "size": 20
        }
        
        try:
            response = self.session.get(url, params=params, timeout=60)
            print(f"请求URL: {url}")
            print(f"请求参数: {json.dumps(params, ensure_ascii=False)}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('data', {})
                    
                    # 处理两种可能的返回格式
                    if isinstance(result, dict) and 'content' in result:
                        registrations = result.get('content', [])
                        total = result.get('totalElements', 0)
                    elif isinstance(result, list):
                        registrations = result
                        total = len(registrations)
                    else:
                        registrations = []
                        total = 0
                    
                    print(f"✅ 报名列表API正常")
                    print(f"   总记录数: {total}")
                    print(f"   当前页记录: {len(registrations)}")
                    
                    if registrations:
                        print(f"\n   前3条报名数据:")
                        for i, reg in enumerate(registrations[:3], 1):
                            reg_id = reg.get('registrationId') or reg.get('id')
                            print(f"   [{i}] ID:{reg_id} | {reg.get('projectName')} | {reg.get('institutionName')} | {reg.get('status')}")
                    else:
                        print(f"   ⚠️  当前赛事暂无报名数据")
                    
                    return True
                else:
                    print(f"❌ API返回失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"响应: {response.text[:500]}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("OPS角色API测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        results = {
            '登录': False,
            '用户统计': False,
            '用户列表': False,
            '报名列表': False
        }
        
        # 1. 登录
        if self.login():
            results['登录'] = True
            
            # 2. 用户统计
            results['用户统计'] = self.test_user_statistics()
            
            # 3. 用户列表
            results['用户列表'] = self.test_query_users()
            
            # 4. 报名列表
            results['报名列表'] = self.test_filter_registrations()
        
        # 输出测试总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        for api_name, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {api_name}: {'正常' if status else '异常'}")
        
        all_passed = all(results.values())
        print("\n" + "="*60)
        if all_passed:
            print("🎉 所有API测试通过！")
        else:
            print("⚠️  部分API测试失败，请检查后端服务")
        print("="*60)
        
        return all_passed

if __name__ == '__main__':
    tester = APITester()
    tester.run_all_tests()
