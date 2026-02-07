#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试评审详情API
验证 GET /api/registrations/{registrationId}/review-details 是否正常返回
"""

import requests
import json
import sys

BASE_URL = "http://localhost:6031"
REGISTRATION_ID = 106  # 护理交接班规范化-1

def print_safe(text):
    """安全打印，避免编码错误"""
    try:
        print(text, flush=True)
    except:
        print(text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'), flush=True)

def login():
    """登录获取token"""
    print_safe("=" * 60)
    print_safe("Step 1: Login to get token")
    print_safe("=" * 60)
    
    login_url = f"{BASE_URL}/api/auth/login"
    payload = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "title": "Title",
        "role": "COMMITTEE_ADMIN"
    }
    
    try:
        response = requests.post(login_url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data', {}).get('token'):
                token = data['data']['token']
                print_safe("Login successful, got token")
                return token
            else:
                print_safe(f"Login failed: {data.get('message', 'Unknown error')}")
                return None
        else:
            print_safe(f"Login request failed: {response.status_code}")
            return None
    except Exception as e:
        print_safe(f"Login exception: {str(e)}")
        return None

def test_review_details(token):
    """测试获取评审详情"""
    print_safe("\n" + "=" * 60)
    print_safe(f"Step 2: Get review details for registration {REGISTRATION_ID}")
    print_safe("=" * 60)
    
    url = f"{BASE_URL}/api/registrations/{REGISTRATION_ID}/review-details"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print_safe(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_safe("API call successful")
            print_safe("\nResponse data structure:")
            print_safe(json.dumps(data, ensure_ascii=False, indent=2))
            
            if data.get('success') and data.get('data'):
                details = data['data']
                print_safe(f"\nReturned {len(details)} stage(s) of review details")
                
                for detail in details:
                    stage = detail.get('stage', 'Unknown')
                    print_safe(f"\n{'='*40}")
                    print_safe(f"Stage: {stage}")
                    print_safe(f"{'='*40}")
                    print_safe(f"Plan score: {detail.get('avgPlan')}")
                    print_safe(f"Problem score: {detail.get('avgProblem')}")
                    print_safe(f"Action score: {detail.get('avgAction')}")
                    print_safe(f"Success score: {detail.get('avgSuccess')}")
                    print_safe(f"Review score: {detail.get('avgReview')}")
                    print_safe(f"Operation score: {detail.get('avgOperation')}")
                    print_safe(f"Presentation score: {detail.get('avgPresentation')}")
                    print_safe(f"Total score: {detail.get('avgTotal')}")
                    
                    highlights = detail.get('highlights', [])
                    weaknesses = detail.get('weaknesses', [])
                    print_safe(f"\nHighlights ({len(highlights)}):")
                    for i, h in enumerate(highlights, 1):
                        print_safe(f"  {i}. {h}")
                    
                    print_safe(f"\nWeaknesses/Suggestions ({len(weaknesses)}):")
                    for i, w in enumerate(weaknesses, 1):
                        print_safe(f"  {i}. {w}")
                
                return True
            else:
                print_safe(f"Response failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print_safe(f"Request failed: {response.status_code}")
            print_safe(f"Response content: {response.text}")
            return False
    except Exception as e:
        print_safe(f"Request exception: {str(e)}")
        return False

def main():
    """主函数"""
    print_safe("\n" + "=" * 60)
    print_safe("Review Details API Test")
    print_safe("=" * 60 + "\n")
    
    # 登录
    token = login()
    if not token:
        print_safe("\nCannot get token, test terminated")
        sys.exit(1)
    
    # 测试评审详情API
    success = test_review_details(token)
    
    # 总结
    print_safe("\n" + "=" * 60)
    print_safe("Test Summary")
    print_safe("=" * 60)
    if success:
        print_safe("Review details API test PASSED")
        print_safe("Frontend can use this API to get detailed scores and reviewer comments")
    else:
        print_safe("Review details API test FAILED")
        print_safe("Please check backend service or data")
    print_safe("=" * 60)

if __name__ == "__main__":
    main()
