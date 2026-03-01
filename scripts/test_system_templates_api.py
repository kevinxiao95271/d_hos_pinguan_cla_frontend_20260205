#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统模版管理API
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

def test_get_active_templates(token):
    """测试获取有效模版列表"""
    print_section("步骤2: 测试获取有效模版列表")
    
    url = f"{BASE_URL}/system-templates/active"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"请求: GET {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}")
            
            if data.get('success'):
                templates = data.get('data', [])
                print(f"\n✅ API返回成功")
                print(f"有效模版数量: {len(templates) if templates else 0}")
                
                if templates:
                    print(f"\n模版列表:")
                    for i, t in enumerate(templates, 1):
                        print(f"  [{i}] {t}")
                else:
                    print(f"⚠️  暂无有效模版")
                return True
            else:
                print(f"❌ success=false: {data.get('message')}")
                return False
        elif response.status_code == 404:
            print(f"❌ 404 Not Found - API端点不存在")
            print(f"响应: {response.text[:500]}")
            return False
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def test_get_all_templates(token):
    """测试获取所有模版列表"""
    print_section("步骤3: 测试获取所有模版列表")
    
    url = f"{BASE_URL}/system-templates"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"请求: GET {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}")
            
            if data.get('success'):
                templates = data.get('data', [])
                print(f"\n✅ API返回成功")
                print(f"所有模版数量: {len(templates) if templates else 0}")
                
                if templates:
                    print(f"\n模版列表:")
                    for i, t in enumerate(templates, 1):
                        print(f"  [{i}] {t}")
                else:
                    print(f"⚠️  暂无模版")
                return True
            else:
                print(f"❌ success=false: {data.get('message')}")
                return False
        elif response.status_code == 404:
            print(f"❌ 404 Not Found - API端点不存在")
            print(f"响应: {response.text[:500]}")
            return False
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def test_upload_template(token):
    """测试上传模版（不实际上传文件，只测试端点）"""
    print_section("步骤4: 测试上传模版端点")
    
    url = f"{BASE_URL}/system-templates/upload"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"请求: POST {url}")
    print(f"说明: 不实际上传文件，只测试端点是否存在")
    
    try:
        # 发送空请求，看看端点是否存在
        response = requests.post(url, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 400:
            print(f"✅ 端点存在（返回400是因为没有文件，这是正常的）")
            print(f"响应: {response.text[:500]}")
            return True
        elif response.status_code == 404:
            print(f"❌ 404 Not Found - API端点不存在")
            print(f"响应: {response.text[:500]}")
            return False
        else:
            print(f"⚠️  HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return True  # 端点存在，只是返回了其他状态码
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def test_delete_template(token):
    """测试删除模版端点（不实际删除）"""
    print_section("步骤5: 测试删除模版端点")
    
    template_id = 999  # 使用不存在的ID
    url = f"{BASE_URL}/system-templates/{template_id}"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"请求: DELETE {url}")
    print(f"说明: 使用不存在的ID测试端点")
    
    try:
        response = requests.delete(url, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 404:
            # 可能是端点不存在，也可能是模版不存在
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            if data and data.get('message'):
                print(f"✅ 端点存在（返回404是因为模版不存在）")
                print(f"响应: {json.dumps(data, ensure_ascii=False)}")
                return True
            else:
                print(f"❌ 404 Not Found - API端点可能不存在")
                print(f"响应: {response.text[:500]}")
                return False
        elif response.status_code in [200, 400, 403]:
            print(f"✅ 端点存在")
            print(f"响应: {response.text[:500]}")
            return True
        else:
            print(f"⚠️  HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return True
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def test_download_template(token):
    """测试下载模版端点（不实际下载）"""
    print_section("步骤6: 测试下载模版端点")
    
    template_id = 999  # 使用不存在的ID
    url = f"{BASE_URL}/system-templates/{template_id}/download"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"请求: GET {url}")
    print(f"说明: 使用不存在的ID测试端点")
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 404:
            # 检查是否返回JSON错误信息
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                data = response.json()
                print(f"✅ 端点存在（返回404是因为模版不存在）")
                print(f"响应: {json.dumps(data, ensure_ascii=False)}")
                return True
            else:
                print(f"❌ 404 Not Found - API端点可能不存在")
                print(f"响应: {response.text[:500]}")
                return False
        elif response.status_code in [200, 400, 403]:
            print(f"✅ 端点存在")
            return True
        else:
            print(f"⚠️  HTTP {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return True
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def main():
    print_section("系统模版管理API测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    token = login()
    if not token:
        print("\n❌ 登录失败，无法继续测试")
        return
    
    results = {
        '获取有效模版': test_get_active_templates(token),
        '获取所有模版': test_get_all_templates(token),
        '上传模版端点': test_upload_template(token),
        '删除模版端点': test_delete_template(token),
        '下载模版端点': test_download_template(token)
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
        print("\n需要后端处理的问题:")
        
        failed_apis = [name for name, status in results.items() if not status]
        for i, api_name in enumerate(failed_apis, 1):
            print(f"  {i}. {api_name} - API端点不存在或返回错误")
    
    print("="*80)

if __name__ == '__main__':
    main()
