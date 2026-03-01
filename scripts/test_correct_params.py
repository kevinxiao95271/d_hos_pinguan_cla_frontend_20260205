#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试正确的参数格式
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

def login():
    """登录"""
    url = f"{BASE_URL}/auth/login-with-password"
    response = requests.post(url, json={
        "phone": "13800000005",
        "password": "ops2026"
    }, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            return data.get('data', {}).get('token')
    return None

def test_with_empty_strings(token):
    """测试包含空字符串的参数（前端当前的方式）"""
    print("\n" + "="*80)
    print("测试1: 包含空字符串的参数（前端当前方式）")
    print("="*80)
    
    url = f"{BASE_URL}/admin/users/query"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 模拟前端发送的参数
    payload = {
        "phone": "",
        "name": "",
        "role": "",
        "institutionId": None,
        "enabled": None,
        "page": 0,
        "size": 20
    }
    
    print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 请求成功")
            data = response.json()
            if data.get('success'):
                print(f"返回数据量: {len(data.get('data', {}).get('content', []))}")
            else:
                print(f"❌ API返回失败: {data.get('message')}")
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

def test_without_empty_fields(token):
    """测试不包含空字段的参数（推荐方式）"""
    print("\n" + "="*80)
    print("测试2: 不包含空字段的参数（推荐方式）")
    print("="*80)
    
    url = f"{BASE_URL}/admin/users/query"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 只发送必需的参数
    payload = {
        "page": 0,
        "size": 20
    }
    
    print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 请求成功")
            data = response.json()
            if data.get('success'):
                print(f"返回数据量: {len(data.get('data', {}).get('content', []))}")
            else:
                print(f"❌ API返回失败: {data.get('message')}")
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

def test_with_null_values(token):
    """测试包含null值的参数"""
    print("\n" + "="*80)
    print("测试3: 包含null值的参数")
    print("="*80)
    
    url = f"{BASE_URL}/admin/users/query"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "phone": None,
        "name": None,
        "role": None,
        "institutionId": None,
        "enabled": None,
        "page": 0,
        "size": 20
    }
    
    print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 请求成功")
            data = response.json()
            if data.get('success'):
                print(f"返回数据量: {len(data.get('data', {}).get('content', []))}")
            else:
                print(f"❌ API返回失败: {data.get('message')}")
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

def main():
    print("="*80)
    print("测试不同参数格式对API的影响")
    print("="*80)
    
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print(f"✅ 登录成功，Token: {token[:30]}...")
    
    test_with_empty_strings(token)
    test_without_empty_fields(token)
    test_with_null_values(token)
    
    print("\n" + "="*80)
    print("结论")
    print("="*80)
    print("""
如果测试1失败（400错误），说明后端不接受空字符串参数。
解决方案：前端在发送请求前，过滤掉空字符串和null值。

修复代码示例：
```javascript
const loadUsers = async () => {
  tableLoading.value = true
  try {
    // 构建参数，过滤空值
    const params = {
      page: currentPage.value - 1,
      size: pageSize.value
    }
    
    // 只添加非空的搜索条件
    if (searchForm.phone) params.phone = searchForm.phone
    if (searchForm.name) params.name = searchForm.name
    if (searchForm.role) params.role = searchForm.role
    if (searchForm.institutionId) params.institutionId = searchForm.institutionId
    if (searchForm.enabled !== null) params.enabled = searchForm.enabled

    const res = await queryUsers(params)
    if (res.success && res.data) {
      users.value = res.data.content
      total.value = res.data.totalElements
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    tableLoading.value = false
  }
}
```
""")

if __name__ == '__main__':
    main()
