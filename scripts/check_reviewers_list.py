#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查评委列表API
查看为什么任务分配时看不到这些评审专家
"""

import requests
import json

BASE_URL = "http://localhost:6031/api"
TIMEOUT = 10

# 用户提供的评审专家名单
EXPECTED_REVIEWERS = [
    "张春梅", "黄丽华", "张幸国", "郭佳奕", "孙彩霞", "蔡斌", "朱健倩", "王跃胜",
    "朱胜春", "潘红英", "王建平", "李益民", "朱玲凤", "周权", "吴定英", "冯志仙",
    "李盈", "王临润", "赵彩莲", "马红丽", "陈水红", "潘红英", "李伟", "俞雪芬",
    "黄小琼", "谭明明", "杨军", "赵雪红", "方英", "徐海铭", "朱良枫", "洪理泉",
    "杨永挺", "吴海英", "章兰英", "宋剑平", "蔡晓芳", "冯素文", "袁铄慧", "封亚萍",
    "潘永苗", "潘胜东", "沈国", "马楠", "蔡雪黎", "金静芬", "秦刚", "张勤",
    "陈肖敏", "冯玉权", "楼尉", "毛伟", "张国兵", "蒋鸿雁", "庄一渝", "陈翔",
    "陈昌贵", "陈美芬", "叶向红", "兰美娟", "沈杨", "冯济业", "陈飞波", "卜智斌",
    "高超", "杜洲舸", "李雅岑", "滕英", "吕娜", "徐敏慧", "邢时通", "郑叶平",
    "楼玉美", "徐辉", "姚智萍", "朱文俊", "王华芬", "胡鸿宇", "胡斌春", "张常乐",
    "裴继强", "李瑾", "严涓", "严志瑜", "叶世伟", "徐敏", "戴金华", "方玢茹",
    "钱玮", "周琳", "刘彩霞", "周莹", "钱莎莎", "朱利明", "宁丽", "李雅",
    "程晓英", "陈艺成", "陈俊航", "陈雪琴", "朱军梅", "袁惠萍", "周尧英", "张岩",
    "张雪霞"
]

def login():
    """登录组委会账号"""
    url = f"{BASE_URL}/auth/login-with-password"
    data = {"phone": "13800000127", "password": "committee2026"}
    
    print("🔐 登录组委会账号...")
    try:
        response = requests.post(url, json=data, timeout=TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 登录成功\n")
                return result['data']['token']
    except Exception as e:
        print(f"❌ 登录失败: {e}\n")
    return None

def check_reviewers_api(token):
    """检查评委列表API"""
    url = f"{BASE_URL}/admin/reviewers"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("="*60)
    print("1. 检查评委列表API (不带参数)")
    print("="*60)
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        print(f"URL: {url}")
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
                
                # 判断是否是分页数据
                if isinstance(data, dict) and 'content' in data:
                    reviewers = data.get('content', [])
                    total = data.get('totalElements', 0)
                    print(f"✅ 分页格式 - 总共 {total} 位评委")
                    print(f"当前页返回 {len(reviewers)} 位")
                elif isinstance(data, list):
                    reviewers = data
                    print(f"✅ 数组格式 - 返回 {len(reviewers)} 位评委")
                else:
                    print(f"⚠️ 未知格式: {type(data)}")
                    reviewers = []
                
                if len(reviewers) > 0:
                    print(f"\n第一位评委信息:")
                    print(json.dumps(reviewers[0], indent=2, ensure_ascii=False))
                    
                    # 检查字段
                    print(f"\n字段列表:")
                    for key in reviewers[0].keys():
                        print(f"  - {key}")
                
                return reviewers, total if isinstance(data, dict) else len(reviewers)
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return [], 0

def check_reviewers_with_competition(token):
    """检查带competitionId参数的评委列表"""
    url = f"{BASE_URL}/admin/reviewers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"competitionId": 1}
    
    print("\n" + "="*60)
    print("2. 检查评委列表API (带competitionId)")
    print("="*60)
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"URL: {url}")
        print(f"参数: {params}")
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
                
                # 判断是否是分页数据
                if isinstance(data, dict) and 'content' in data:
                    reviewers = data.get('content', [])
                    total = data.get('totalElements', 0)
                    print(f"✅ 分页格式 - 总共 {total} 位评委")
                    print(f"当前页返回 {len(reviewers)} 位")
                elif isinstance(data, list):
                    reviewers = data
                    print(f"✅ 数组格式 - 返回 {len(reviewers)} 位评委")
                else:
                    print(f"⚠️ 未知格式: {type(data)}")
                    reviewers = []
                
                return reviewers, total if isinstance(data, dict) else len(reviewers)
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return [], 0

def check_reviewers_with_pagination(token):
    """检查带分页参数的评委列表"""
    url = f"{BASE_URL}/admin/reviewers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "competitionId": 1,
        "page": 0,
        "size": 200  # 获取更多数据
    }
    
    print("\n" + "="*60)
    print("3. 检查评委列表API (带分页参数)")
    print("="*60)
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        print(f"URL: {url}")
        print(f"参数: {params}")
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
                
                # 判断是否是分页数据
                if isinstance(data, dict) and 'content' in data:
                    reviewers = data.get('content', [])
                    total = data.get('totalElements', 0)
                    print(f"✅ 分页格式 - 总共 {total} 位评委")
                    print(f"当前页返回 {len(reviewers)} 位")
                elif isinstance(data, list):
                    reviewers = data
                    print(f"✅ 数组格式 - 返回 {len(reviewers)} 位评委")
                else:
                    print(f"⚠️ 未知格式: {type(data)}")
                    reviewers = []
                
                return reviewers, total if isinstance(data, dict) else len(reviewers)
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return [], 0

def compare_with_expected(reviewers):
    """对比实际返回的评委和期望的评委名单"""
    print("\n" + "="*60)
    print("4. 对比期望的评委名单")
    print("="*60)
    
    print(f"\n期望的评委数: {len(EXPECTED_REVIEWERS)}")
    print(f"实际返回的评委数: {len(reviewers)}")
    
    # 提取实际返回的评委姓名
    actual_names = set()
    for reviewer in reviewers:
        name = reviewer.get('name') or reviewer.get('reviewerName')
        if name:
            actual_names.add(name)
    
    print(f"实际有姓名的评委数: {len(actual_names)}")
    
    # 找出缺失的评委
    expected_set = set(EXPECTED_REVIEWERS)
    missing = expected_set - actual_names
    
    if missing:
        print(f"\n❌ 缺失的评委 ({len(missing)} 位):")
        for name in sorted(missing):
            print(f"  - {name}")
    else:
        print(f"\n✅ 所有期望的评委都在列表中！")
    
    # 找出多余的评委
    extra = actual_names - expected_set
    if extra:
        print(f"\n额外的评委 ({len(extra)} 位):")
        for name in sorted(extra):
            print(f"  - {name}")
    
    # 显示实际返回的所有评委姓名
    if len(actual_names) > 0 and len(actual_names) <= 20:
        print(f"\n实际返回的评委姓名:")
        for name in sorted(actual_names):
            print(f"  - {name}")

def main():
    print("="*60)
    print("检查评委列表API")
    print("="*60)
    print()
    
    token = login()
    if not token:
        print("❌ 无法获取token，测试终止")
        return
    
    # 测试不同的API调用方式
    reviewers1, total1 = check_reviewers_api(token)
    reviewers2, total2 = check_reviewers_with_competition(token)
    reviewers3, total3 = check_reviewers_with_pagination(token)
    
    # 使用返回最多数据的结果进行对比
    if len(reviewers3) >= len(reviewers2) >= len(reviewers1):
        print(f"\n使用分页参数的结果进行对比 ({len(reviewers3)} 位)")
        compare_with_expected(reviewers3)
    elif len(reviewers2) >= len(reviewers1):
        print(f"\n使用competitionId参数的结果进行对比 ({len(reviewers2)} 位)")
        compare_with_expected(reviewers2)
    else:
        print(f"\n使用无参数的结果进行对比 ({len(reviewers1)} 位)")
        compare_with_expected(reviewers1)
    
    print("\n" + "="*60)
    print("检查完成")
    print("="*60)

if __name__ == "__main__":
    main()
