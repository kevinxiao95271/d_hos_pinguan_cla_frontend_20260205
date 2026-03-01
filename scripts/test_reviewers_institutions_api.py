#!/usr/bin/env python3
"""
测试评审专家管理页面的机构列表API
验证不同参数下的API响应
"""

import requests
import json

BASE_URL = "http://localhost:8080/api"

# OPS账号登录
def login():
    """使用OPS账号登录"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "phone": "13800000005",
        "password": "ops2026"
    }
    
    print("=" * 60)
    print("1. 登录OPS账号")
    print("=" * 60)
    
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            token = result['data']['token']
            print(f"✅ 登录成功")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print(f"❌ 登录失败: {result.get('message')}")
            return None
    else:
        print(f"❌ 请求失败: {response.text}")
        return None

def test_institutions_api(token):
    """测试机构列表API的不同调用方式"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/institutions/search"
    
    # 测试1: 不传参数（undefined）
    print("\n" + "=" * 60)
    print("2. 测试不传参数（模拟前端当前行为）")
    print("=" * 60)
    print(f"请求: POST {url}")
    print(f"请求体: None")
    
    try:
        response = requests.post(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功")
            print(f"响应格式: {type(result.get('data'))}")
            if isinstance(result.get('data'), list):
                print(f"返回数组长度: {len(result['data'])}")
            elif isinstance(result.get('data'), dict):
                print(f"返回对象键: {list(result['data'].keys())}")
                if 'content' in result['data']:
                    print(f"content长度: {len(result['data']['content'])}")
        else:
            print(f"❌ 请求失败")
            print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
    
    # 测试2: 传递空对象
    print("\n" + "=" * 60)
    print("3. 测试传递空对象 {}")
    print("=" * 60)
    print(f"请求: POST {url}")
    print(f"请求体: {{}}")
    
    try:
        response = requests.post(url, json={}, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功")
            print(f"响应格式: {type(result.get('data'))}")
            if isinstance(result.get('data'), list):
                print(f"返回数组长度: {len(result['data'])}")
                if len(result['data']) > 0:
                    print(f"第一条数据: {json.dumps(result['data'][0], ensure_ascii=False, indent=2)}")
            elif isinstance(result.get('data'), dict):
                print(f"返回对象键: {list(result['data'].keys())}")
                if 'content' in result['data']:
                    print(f"content长度: {len(result['data']['content'])}")
                    if len(result['data']['content']) > 0:
                        print(f"第一条数据: {json.dumps(result['data']['content'][0], ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 请求失败")
            print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
    
    # 测试3: 传递分页参数
    print("\n" + "=" * 60)
    print("4. 测试传递分页参数")
    print("=" * 60)
    
    params = {
        "page": 0,
        "size": 100
    }
    
    print(f"请求: POST {url}")
    print(f"请求体: {json.dumps(params, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=params, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功")
            print(f"响应格式: {type(result.get('data'))}")
            
            if isinstance(result.get('data'), list):
                print(f"返回数组长度: {len(result['data'])}")
                if len(result['data']) > 0:
                    sample = result['data'][0]
                    print(f"数据字段: {list(sample.keys())}")
                    print(f"示例: {sample.get('name', 'N/A')}")
            elif isinstance(result.get('data'), dict):
                data = result['data']
                print(f"返回对象键: {list(data.keys())}")
                
                if 'content' in data:
                    print(f"✅ 分页格式")
                    print(f"  - content长度: {len(data['content'])}")
                    print(f"  - totalElements: {data.get('totalElements', 'N/A')}")
                    print(f"  - totalPages: {data.get('totalPages', 'N/A')}")
                    print(f"  - size: {data.get('size', 'N/A')}")
                    print(f"  - number: {data.get('number', 'N/A')}")
                    
                    if len(data['content']) > 0:
                        sample = data['content'][0]
                        print(f"数据字段: {list(sample.keys())}")
                        print(f"示例机构: {sample.get('name', 'N/A')}")
        else:
            print(f"❌ 请求失败")
            print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
    
    # 测试4: 大分页（获取更多数据用于下拉列表）
    print("\n" + "=" * 60)
    print("5. 测试大分页（size=10000，用于下拉列表）")
    print("=" * 60)
    
    params = {
        "page": 0,
        "size": 10000
    }
    
    print(f"请求: POST {url}")
    print(f"请求体: {json.dumps(params, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=params, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功")
            
            if isinstance(result.get('data'), dict) and 'content' in result['data']:
                data = result['data']
                print(f"✅ 获取到 {len(data['content'])} 条机构数据")
                print(f"总数据量: {data.get('totalElements', 'N/A')}")
                print(f"是否足够: {'✅ 是' if len(data['content']) >= data.get('totalElements', 0) else '❌ 否，需要更大的size'}")
        else:
            print(f"❌ 请求失败")
            print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

def test_reviewers_api(token):
    """测试评委列表API（验证页面为什么仍然工作）"""
    
    print("\n" + "=" * 60)
    print("6. 测试评委列表API（验证为什么页面仍然工作）")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/admin/reviewers"
    
    print(f"请求: GET {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功")
            
            if isinstance(result.get('data'), list):
                reviewers = result['data']
                print(f"评委数量: {len(reviewers)}")
                
                if len(reviewers) > 0:
                    sample = reviewers[0]
                    print(f"数据字段: {list(sample.keys())}")
                    print(f"✅ 包含 institutionName: {'institutionName' in sample}")
                    print(f"示例评委: {sample.get('name', 'N/A')} - {sample.get('institutionName', 'N/A')}")
                    print(f"\n说明: 评委列表中的机构名称由后端直接返回，不依赖前端的机构列表")
            elif isinstance(result.get('data'), dict) and 'content' in result['data']:
                reviewers = result['data']['content']
                print(f"评委数量: {len(reviewers)}")
                
                if len(reviewers) > 0:
                    sample = reviewers[0]
                    print(f"数据字段: {list(sample.keys())}")
                    print(f"✅ 包含 institutionName: {'institutionName' in sample}")
                    print(f"示例评委: {sample.get('name', 'N/A')} - {sample.get('institutionName', 'N/A')}")
        else:
            print(f"❌ 请求失败")
            print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

def main():
    print("评审专家管理页面 - 机构列表API测试")
    print("=" * 60)
    
    # 登录
    token = login()
    if not token:
        print("\n❌ 登录失败，无法继续测试")
        return
    
    # 测试机构API
    test_institutions_api(token)
    
    # 测试评委API
    test_reviewers_api(token)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print("""
问题原因:
  评审专家管理页面调用 getInstitutions() 时没有传递任何参数
  导致 POST /institutions/search 请求体为空，后端返回 400

影响范围:
  ❌ 机构下拉列表为空（无法按机构筛选评委）
  ❌ 新增/编辑评委时无法选择机构
  ✅ 评委列表正常显示（institutionName由后端返回）

解决方案:
  1. 传递空对象: getInstitutions({})
  2. 传递分页参数: getInstitutions({ page: 0, size: 10000 })
  3. 处理分页响应格式（如果返回的是 { content: [], totalElements: N }）

推荐方案:
  使用方案2，传递分页参数，并处理分页响应格式
    """)

if __name__ == "__main__":
    main()
