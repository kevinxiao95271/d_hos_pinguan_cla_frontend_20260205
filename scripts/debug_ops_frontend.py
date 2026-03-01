#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试OPS前端页面数据为空的问题
模拟前端实际请求流程
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:6031/api"
LOGIN_DATA = {
    "phone": "13800000005",
    "password": "ops2026"
}

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def login():
    """登录获取token"""
    print_section("步骤1: 登录")
    
    url = f"{BASE_URL}/auth/login-with-password"
    print(f"请求: POST {url}")
    print(f"参数: {json.dumps(LOGIN_DATA, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=LOGIN_DATA, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data.get('data', {}).get('token')
                user_info = data.get('data', {})
                
                print(f"✅ 登录成功")
                print(f"Token: {token[:50]}...")
                print(f"用户信息: {json.dumps(user_info, ensure_ascii=False, indent=2)}")
                
                return token
            else:
                print(f"❌ 登录失败: {data.get('message')}")
                return None
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return None
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return None

def test_user_statistics(token):
    """测试用户统计API"""
    print_section("步骤2: 测试用户统计API")
    
    url = f"{BASE_URL}/admin/users/statistics"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"请求: GET {url}")
    print(f"请求头: Authorization: Bearer {token[:30]}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:1000]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n解析后的数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            if data.get('success'):
                print(f"\n✅ API返回成功")
                stats = data.get('data', {})
                if stats:
                    print(f"统计数据: {json.dumps(stats, ensure_ascii=False, indent=2)}")
                else:
                    print(f"⚠️  data字段为空或null")
            else:
                print(f"❌ success=false: {data.get('message')}")
        else:
            print(f"❌ HTTP错误")
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

def test_query_users(token):
    """测试查询用户列表API"""
    print_section("步骤3: 测试查询用户列表API")
    
    url = f"{BASE_URL}/admin/users/query"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "page": 0,
        "size": 20
    }
    
    print(f"请求: POST {url}")
    print(f"请求头: Authorization: Bearer {token[:30]}...")
    print(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:1000]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n解析后的数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
            
            if data.get('success'):
                print(f"\n✅ API返回成功")
                result = data.get('data', {})
                
                if isinstance(result, dict):
                    users = result.get('content', [])
                    total = result.get('totalElements', 0)
                    print(f"总记录数: {total}")
                    print(f"当前页记录数: {len(users)}")
                    
                    if users:
                        print(f"\n前3条用户:")
                        for i, user in enumerate(users[:3], 1):
                            print(f"  [{i}] {user}")
                    else:
                        print(f"⚠️  content数组为空")
                elif isinstance(result, list):
                    print(f"返回列表，长度: {len(result)}")
                else:
                    print(f"⚠️  data字段类型异常: {type(result)}")
            else:
                print(f"❌ success=false: {data.get('message')}")
        else:
            print(f"❌ HTTP错误")
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

def test_filter_registrations(token):
    """测试筛选报名列表API"""
    print_section("步骤4: 测试筛选报名列表API")
    
    # 先获取赛事列表
    comp_url = f"{BASE_URL}/competitions"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"4.1 获取赛事列表")
    print(f"请求: GET {comp_url}")
    
    competition_id = None
    try:
        response = requests.get(comp_url, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                competitions = data.get('data', [])
                print(f"赛事数量: {len(competitions)}")
                
                if competitions:
                    competition_id = competitions[0].get('id')
                    print(f"使用赛事: {competitions[0].get('name')} (ID: {competition_id})")
                else:
                    print(f"⚠️  赛事列表为空")
            else:
                print(f"❌ 获取赛事失败: {data.get('message')}")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
    
    if not competition_id:
        print(f"⚠️  未找到赛事，使用默认ID=1")
        competition_id = 1
    
    # 测试报名列表
    print(f"\n4.2 获取报名列表")
    url = f"{BASE_URL}/admin/registrations/filter"
    params = {
        "competitionId": competition_id,
        "page": 0,
        "size": 20
    }
    
    print(f"请求: GET {url}")
    print(f"参数: {json.dumps(params, ensure_ascii=False)}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:1000]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n解析后的数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
            
            if data.get('success'):
                print(f"\n✅ API返回成功")
                result = data.get('data', {})
                
                if isinstance(result, dict) and 'content' in result:
                    registrations = result.get('content', [])
                    total = result.get('totalElements', 0)
                    print(f"总记录数: {total}")
                    print(f"当前页记录数: {len(registrations)}")
                    
                    if registrations:
                        print(f"\n前3条报名:")
                        for i, reg in enumerate(registrations[:3], 1):
                            print(f"  [{i}] {reg}")
                    else:
                        print(f"⚠️  content数组为空")
                elif isinstance(result, list):
                    print(f"返回列表，长度: {len(result)}")
                    if result:
                        print(f"\n前3条报名:")
                        for i, reg in enumerate(result[:3], 1):
                            print(f"  [{i}] {reg}")
                    else:
                        print(f"⚠️  列表为空")
                else:
                    print(f"⚠️  data字段类型异常: {type(result)}")
            else:
                print(f"❌ success=false: {data.get('message')}")
        else:
            print(f"❌ HTTP错误")
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

def check_browser_console():
    """提示检查浏览器控制台"""
    print_section("前端调试建议")
    
    print("""
请在浏览器中执行以下操作来调试：

1. 打开浏览器开发者工具 (F12)

2. 切换到 Console 标签，查看是否有错误信息

3. 切换到 Network 标签，筛选 XHR 请求

4. 登录系统后，访问用户管理页面

5. 查看以下请求：
   - /api/admin/users/statistics
   - /api/admin/users/query

6. 检查请求详情：
   - Request Headers 中是否有 Authorization
   - Response 中的数据是否正确
   - Status Code 是否为 200

7. 在 Console 中执行以下命令查看 Token：
   ```javascript
   console.log('Token:', localStorage.getItem('token'))
   console.log('UserInfo:', localStorage.getItem('userInfo'))
   ```

8. 如果 Token 为空，说明登录状态丢失，需要重新登录

9. 如果 Token 存在但请求返回 401，说明 Token 已过期

10. 如果请求返回空数据但 API 测试正常，可能是：
    - 前端过滤条件导致数据被过滤
    - 前端数据解析逻辑有问题
    - 前端状态管理有问题
""")

def main():
    print_section("OPS前端数据为空问题调试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 登录
    token = login()
    if not token:
        print("\n❌ 登录失败，无法继续测试")
        return
    
    # 测试各个API
    test_user_statistics(token)
    test_query_users(token)
    test_filter_registrations(token)
    
    # 调试建议
    check_browser_console()
    
    print_section("调试完成")
    print("""
总结：
1. 如果上述所有API测试都返回了数据，说明后端API正常
2. 前端显示空数据的原因可能是：
   - Token未正确传递到请求中
   - 前端数据解析逻辑有问题
   - 前端过滤/筛选条件导致数据被过滤
   - 浏览器缓存问题

建议操作：
1. 清除浏览器缓存并刷新页面 (Ctrl+Shift+Delete)
2. 重新登录系统
3. 打开浏览器开发者工具查看 Network 请求
4. 检查 Console 是否有 JavaScript 错误
""")

if __name__ == '__main__':
    main()
