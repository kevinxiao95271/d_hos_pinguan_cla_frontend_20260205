#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试机构管理API
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
    try:
        response = requests.post(url, json=LOGIN_DATA, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data.get('data', {}).get('token')
                print(f"✅ 登录成功")
                return token
        print(f"❌ 登录失败")
        return None
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return None

def test_get_institutions_no_params(token):
    """测试获取机构列表（不带参数）"""
    print_section("步骤2: 测试获取机构列表（不带参数）")
    
    url = f"{BASE_URL}/institutions"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"请求: GET {url}")
    print(f"参数: 无")
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}")
            
            if data.get('success'):
                result = data.get('data', [])
                
                # 判断是分页对象还是数组
                if isinstance(result, dict):
                    institutions = result.get('content', [])
                    total = result.get('totalElements', 0)
                    print(f"\n✅ API返回成功（分页格式）")
                    print(f"总记录数: {total}")
                    print(f"当前页记录数: {len(institutions)}")
                elif isinstance(result, list):
                    institutions = result
                    print(f"\n✅ API返回成功（数组格式）")
                    print(f"记录数: {len(institutions)}")
                else:
                    print(f"⚠️  data字段类型异常: {type(result)}")
                    return False
                
                if institutions:
                    print(f"\n前3条机构:")
                    for i, inst in enumerate(institutions[:3], 1):
                        print(f"  [{i}] {inst.get('name', 'N/A')} - {inst.get('level', 'N/A')}")
                else:
                    print(f"⚠️  机构列表为空")
                
                return True
            else:
                print(f"❌ success=false: {data.get('message')}")
                return False
        elif response.status_code == 400:
            print(f"❌ 400 Bad Request - 可能需要参数")
            print(f"响应: {response.text[:500]}")
            return False
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def test_get_institutions_with_pagination(token):
    """测试获取机构列表（带分页参数）"""
    print_section("步骤3: 测试获取机构列表（带分页参数）")
    
    url = f"{BASE_URL}/institutions"
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        "page": 0,
        "size": 50
    }
    
    print(f"请求: GET {url}")
    print(f"参数: {json.dumps(params, ensure_ascii=False)}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}")
            
            if data.get('success'):
                result = data.get('data', [])
                
                if isinstance(result, dict):
                    institutions = result.get('content', [])
                    total = result.get('totalElements', 0)
                    print(f"\n✅ API返回成功（分页格式）")
                    print(f"总记录数: {total}")
                    print(f"当前页记录数: {len(institutions)}")
                elif isinstance(result, list):
                    institutions = result
                    print(f"\n✅ API返回成功（数组格式）")
                    print(f"记录数: {len(institutions)}")
                else:
                    print(f"⚠️  data字段类型异常: {type(result)}")
                    return False
                
                if institutions:
                    print(f"\n前3条机构:")
                    for i, inst in enumerate(institutions[:3], 1):
                        print(f"  [{i}] {inst.get('name', 'N/A')} - {inst.get('level', 'N/A')}")
                else:
                    print(f"⚠️  机构列表为空")
                
                return True
            else:
                print(f"❌ success=false: {data.get('message')}")
                return False
        elif response.status_code == 400:
            print(f"❌ 400 Bad Request")
            print(f"响应: {response.text[:500]}")
            return False
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def test_search_institutions(token):
    """测试搜索机构（POST方式）"""
    print_section("步骤4: 测试搜索机构API")
    
    url = f"{BASE_URL}/institutions/search"
    headers = {'Authorization': f'Bearer {token}'}
    payload = {
        "page": 0,
        "size": 50
    }
    
    print(f"请求: POST {url}")
    print(f"参数: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}")
            
            if data.get('success'):
                result = data.get('data', {})
                institutions = result.get('content', [])
                total = result.get('totalElements', 0)
                
                print(f"\n✅ API返回成功")
                print(f"总记录数: {total}")
                print(f"当前页记录数: {len(institutions)}")
                
                if institutions:
                    print(f"\n前3条机构:")
                    for i, inst in enumerate(institutions[:3], 1):
                        print(f"  [{i}] {inst.get('name', 'N/A')} - {inst.get('level', 'N/A')}")
                else:
                    print(f"⚠️  机构列表为空")
                
                return True
            else:
                print(f"❌ success=false: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def main():
    print_section("机构管理API测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    token = login()
    if not token:
        print("\n❌ 登录失败，无法继续测试")
        return
    
    results = {
        '获取机构列表（无参数）': test_get_institutions_no_params(token),
        '获取机构列表（分页参数）': test_get_institutions_with_pagination(token),
        '搜索机构（POST）': test_search_institutions(token)
    }
    
    print_section("测试总结")
    
    for api_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {api_name}: {'正常' if status else '异常'}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 所有API测试通过！")
    else:
        print("⚠️  部分API测试失败")
        print("\n可能的原因:")
        print("  1. API需要特定的参数格式")
        print("  2. 后端对空参数的处理有问题（类似用户管理的问题）")
        print("  3. 数据库中没有机构数据")
    
    print("="*80)
    
    print("\n" + "="*80)
    print("前端调用分析")
    print("="*80)
    print("""
前端代码位置: src/views/ops/Institutions.vue

调用方式:
```javascript
const loadData = async () => {
  try {
    const res = await getInstitutions(getPaginationParams())
    if (res.success) {
      institutions.value = extractDataList(res.data)
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  }
}
```

getPaginationParams() 返回:
{
  page: 0,
  size: 50
}

问题可能是:
1. 如果API返回400，可能是参数格式问题（类似用户管理的空字符串问题）
2. 如果API返回空数组，可能是数据库中没有数据
3. 如果API返回404，可能是端点不存在
""")

if __name__ == '__main__':
    main()
