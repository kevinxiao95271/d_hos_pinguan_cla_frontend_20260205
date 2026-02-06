#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的登录测试 - 验证后端是否正常响应
"""

import requests
import time
import sys

BASE_URL = "http://localhost:6031/api"

def test_simple_login():
    """简单快速的登录测试"""
    print("="*60)
    print("Quick Login Test")
    print("="*60)
    
    payload = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN",
        "title": "Committee Member",
        "institutionId": None,
        "reviewerGroupCode": None,
        "interviewGroupCode": None,
        "expertBackground": None
    }
    
    print("\n[INFO] Testing backend login...")
    print(f"[INFO] URL: {BASE_URL}/auth/login")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=payload,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n[RESULT] Status Code: {response.status_code}")
        print(f"[RESULT] Response Time: {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"[SUCCESS] Login successful!")
                print(f"[SUCCESS] Token: {data['data']['token'][:50]}...")
                return True
            else:
                print(f"[FAIL] Login failed: {data.get('message')}")
                return False
        else:
            print(f"[FAIL] HTTP {response.status_code}")
            print(f"[RESPONSE] {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"\n[TIMEOUT] Request timeout after {elapsed:.2f} seconds")
        print(f"[ADVICE] Backend might be slow or not responding")
        return False
        
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Cannot connect to backend")
        print(f"[ADVICE] Please check if backend is running at http://localhost:6031")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple_login()
    
    print("\n" + "="*60)
    if success:
        print("[OK] Backend is working normally!")
        print("="*60)
        print("\nYou can now:")
        print("  1. Restart frontend dev server (npm run dev)")
        print("  2. Clear browser cache (Ctrl+Shift+Delete)")
        print("  3. Refresh page and try login again")
        sys.exit(0)
    else:
        print("[FAIL] Backend test failed!")
        print("="*60)
        print("\nPlease:")
        print("  1. Check if backend is running")
        print("  2. Visit http://localhost:6031/actuator/health")
        print("  3. Check backend logs for errors")
        sys.exit(1)
