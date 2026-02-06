#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解码JWT Token查看payload"""

import requests
import sys
import json
import base64

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:6031/api"

def decode_jwt_payload(token):
    """解码JWT的payload部分（不验证签名）"""
    try:
        # JWT格式: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # 解码 payload (第二部分)
        payload = parts[1]
        # 添加padding
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"解码失败: {e}")
        return None

try:
    # 1. 登录
    print("1️⃣  登录...")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Title",
        "role": "COMMITTEE_ADMIN"
    }, timeout=30)
    
    if r.status_code != 200:
        print(f"❌ 登录失败: {r.status_code}")
        sys.exit(1)
    
    response_data = r.json()['data']
    token = response_data['token']
    
    print("✅ 登录成功\n")
    print("="*60)
    print("登录响应数据:")
    print("="*60)
    print(json.dumps(response_data, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("JWT Token Payload:")
    print("="*60)
    payload = decode_jwt_payload(token)
    if payload:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        
        print("\n" + "="*60)
        print("关键字段检查:")
        print("="*60)
        print(f"   - sub (用户ID): {payload.get('sub')}")
        print(f"   - role: {payload.get('role')}")
        print(f"   - iat (签发时间): {payload.get('iat')}")
        print(f"   - exp (过期时间): {payload.get('exp')}")
        
        # 检查role
        role = payload.get('role')
        if role == 'COMMITTEE_ADMIN':
            print(f"\n   ✅ role 字段正确: {role}")
        else:
            print(f"\n   ⚠️  role 字段: {role} (期望: COMMITTEE_ADMIN)")
    
    # 2. 测试普通接口（非admin）
    print("\n" + "="*60)
    print("2️⃣  测试普通接口 (GET /api/registrations)")
    print("="*60)
    r = requests.get(
        f"{BASE_URL}/registrations",
        headers={"Authorization": f"Bearer {token}"},
        params={"competitionId": 21},
        timeout=30
    )
    print(f"   状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✅ 普通接口可访问")
    else:
        print(f"   ❌ 普通接口也无法访问")
    
    # 3. 测试admin接口
    print("\n" + "="*60)
    print("3️⃣  测试admin接口 (GET /api/admin/registrations/filter)")
    print("="*60)
    r = requests.get(
        f"{BASE_URL}/admin/registrations/filter",
        headers={"Authorization": f"Bearer {token}"},
        params={"competitionId": 21},
        timeout=30
    )
    print(f"   状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✅ Admin接口可访问")
    elif r.status_code == 401:
        print(f"   ❌ 401 - 未授权")
        print(f"   响应: {r.text[:500]}")
    elif r.status_code == 403:
        print(f"   ❌ 403 - 无权限")
        print(f"   响应: {r.text[:500]}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
