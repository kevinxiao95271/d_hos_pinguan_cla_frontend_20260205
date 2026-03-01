#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统设置API
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

def test_get_setting(token, key):
    """测试获取单个配置项"""
    url = f"{BASE_URL}/admin/settings"
    headers = {'Authorization': f'Bearer {token}'}
    params = {'key': key}
    
    print(f"\n测试获取配置: {key}")
    print(f"请求: GET {url}?key={key}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get('success'):
                print(f"✅ 获取成功")
                return True, data.get('data')
            else:
                print(f"❌ success=false: {data.get('message')}")
                return False, None
        elif response.status_code == 404:
            print(f"⚠️  404 - 配置项不存在")
            print(f"响应: {response.text[:500]}")
            return False, None
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False, None
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False, None

def test_save_setting(token, key, value):
    """测试保存配置项"""
    url = f"{BASE_URL}/admin/settings"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'key': key,
        'value': str(value)
    }
    
    print(f"\n测试保存配置: {key} = {value}")
    print(f"请求: POST {url}")
    print(f"参数: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get('success'):
                print(f"✅ 保存成功")
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
    print_section("系统设置API测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    token = login()
    if not token:
        print("\n❌ 登录失败，无法继续测试")
        return
    
    # 前端使用的配置项
    settings_keys = [
        'maxRegistrationsPerInstitution',  # 机构报名配额限制（已实现）
        'reviewerMaxLoad',                 # 评审专家最大负荷（未实现）
        'basicGroupCount',                 # 基层组分组数量（未实现）
        'comprehensiveGroupCount',         # 综合组分组数量（未实现）
        'advancedGroupCount',              # 进阶组分组数量（未实现）
        'shortlistRatio'                   # 入围比例（未实现）
    ]
    
    print_section("步骤2: 测试获取所有配置项")
    
    get_results = {}
    for key in settings_keys:
        success, data = test_get_setting(token, key)
        get_results[key] = success
    
    print_section("步骤3: 测试保存配置项")
    
    # 只测试一个配置项的保存
    test_key = 'maxRegistrationsPerInstitution'
    test_value = 8
    save_success = test_save_setting(token, test_key, test_value)
    
    print_section("测试总结")
    
    print("\n获取配置项结果:")
    for key, success in get_results.items():
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {key}: {'成功' if success else '失败/不存在'}")
    
    print(f"\n保存配置项结果:")
    print(f"{'✅' if save_success else '❌'} {test_key}: {'成功' if save_success else '失败'}")
    
    print("\n" + "="*80)
    print("前端调用分析")
    print("="*80)
    print("""
前端代码位置: src/views/ops/Settings.vue

调用的API:
1. GET /admin/settings?key={key} - 获取单个配置项
2. POST /admin/settings - 保存配置项
   请求体: { "key": "xxx", "value": "xxx" }

前端逻辑:
1. 页面加载时，逐个查询所有配置项
2. 如果配置项不存在，使用默认值
3. 保存时，逐个保存所有配置项

可能的问题:
1. 如果后端某些配置项不存在，会报404或返回success=false
2. 前端会尝试查询6个配置项，但后端可能只实现了部分
3. 前端代码已经做了容错处理（try-catch），但控制台会有错误日志

建议:
1. 后端实现所有6个配置项的存储
2. 或者前端只查询已实现的配置项
3. 或者后端返回所有配置项的默认值
""")
    
    print("="*80)

if __name__ == '__main__':
    main()
