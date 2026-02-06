#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试参赛者完整流程
"""

import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031/api"

# 5个推荐的参赛者账号
CONTESTANTS = [
    {"phone": "13966000011", "name": "参赛者11", "institution": "嘉兴市第一医院", "registrationId": 116},
    {"phone": "13966000012", "name": "参赛者12", "institution": "嘉兴市第二医院", "registrationId": 117},
    {"phone": "13966000013", "name": "参赛者13", "institution": "湖州市中心医院", "registrationId": 118},
    {"phone": "13966000014", "name": "参赛者14", "institution": "绍兴市人民医院", "registrationId": 119},
    {"phone": "13966000015", "name": "参赛者15", "institution": "金华市中心医院", "registrationId": 120},
]

def login(contestant):
    """登录"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": contestant["phone"],
        "name": contestant["name"],
        "title": "项目负责人",
        "role": "CONTESTANT"
    }, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('data', {}).get('token')
    return None

def get_my_registrations(token):
    """获取我的报名列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/registrations/my", headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('data', []) if result.get('success') else None
    return None

def get_registration_detail(token, registration_id):
    """获取报名详情"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/registrations/{registration_id}", headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('data') if result.get('success') else None
    return None

def test_contestant(contestant):
    """测试单个参赛者"""
    print(f"\n{'='*70}")
    print(f"测试参赛者: {contestant['name']} ({contestant['phone']})")
    print(f"机构: {contestant['institution']}")
    print(f"{'='*70}")
    
    # 1. 登录
    print("\n1️⃣  登录...")
    token = login(contestant)
    if not token:
        print("❌ 登录失败")
        return None
    print("✅ 登录成功")
    
    # 2. 获取我的报名列表
    print("\n2️⃣  获取我的报名列表...")
    registrations = get_my_registrations(token)
    if registrations is None:
        print("❌ 获取报名列表失败")
        return None
    
    print(f"✅ 获取成功，共 {len(registrations)} 个报名")
    
    if len(registrations) == 0:
        print("⚠️  暂无报名")
        return {
            "contestant": contestant,
            "token": token,
            "registrations": [],
            "detail": None
        }
    
    # 显示报名列表
    for i, reg in enumerate(registrations, 1):
        print(f"\n报名 {i}:")
        print(f"  ID: {reg.get('id')}")
        print(f"  项目名称: {reg.get('projectName')}")
        print(f"  状态: {reg.get('status')}")
        print(f"  竞赛组别: {reg.get('groupType')}")
        print(f"  分组: {reg.get('groupCode')}")
    
    # 3. 获取第一个报名的详情
    first_reg = registrations[0]
    reg_id = first_reg.get('id')
    
    print(f"\n3️⃣  获取报名详情 (ID={reg_id})...")
    detail = get_registration_detail(token, reg_id)
    if not detail:
        print("❌ 获取详情失败")
        return None
    
    print("✅ 获取详情成功")
    
    # 检查详情数据结构
    print("\n详情数据结构:")
    registration = detail.get('registration', {})
    members = detail.get('members', [])
    activity_info = detail.get('activityInfo')
    summary = detail.get('projectSummary')
    
    print(f"  registration:")
    print(f"    id: {registration.get('id')}")
    print(f"    projectName: {registration.get('projectName')}")
    print(f"    groupType: {registration.get('groupType')}")
    print(f"    status: {registration.get('status')}")
    
    print(f"  members: {len(members)} 人")
    for member in members[:2]:
        print(f"    - {member.get('name')} ({member.get('title')}) - {member.get('role')}")
    
    print(f"  activityInfo: {'有' if activity_info else '无'}")
    if activity_info:
        print(f"    theme: {activity_info.get('theme')}")
        print(f"    methodLabel: {activity_info.get('methodLabel')}")
    
    print(f"  projectSummary: {'有' if summary else '无'}")
    
    return {
        "contestant": contestant,
        "token": token,
        "registrations": registrations,
        "detail": detail
    }

def check_frontend_compatibility(results):
    """检查前端兼容性"""
    print("\n\n" + "="*70)
    print("  前端兼容性检查")
    print("="*70)
    
    issues = []
    
    for result in results:
        if not result:
            continue
        
        contestant = result['contestant']
        registrations = result['registrations']
        detail = result['detail']
        
        print(f"\n检查 {contestant['name']}:")
        
        # 检查报名列表字段
        if len(registrations) > 0:
            reg = registrations[0]
            required_fields = ['id', 'projectName', 'status', 'groupType']
            for field in required_fields:
                if field not in reg or reg.get(field) is None:
                    issues.append(f"❌ {contestant['name']}: 报名列表缺少字段 {field}")
                    print(f"  ❌ 报名列表缺少字段: {field}")
                else:
                    print(f"  ✅ 报名列表有字段: {field}")
        
        # 检查详情数据结构
        if detail:
            if 'registration' not in detail:
                issues.append(f"❌ {contestant['name']}: 详情缺少 registration 对象")
                print(f"  ❌ 详情缺少 registration 对象")
            else:
                print(f"  ✅ 详情有 registration 对象")
            
            if 'members' not in detail:
                issues.append(f"❌ {contestant['name']}: 详情缺少 members 数组")
                print(f"  ❌ 详情缺少 members 数组")
            else:
                print(f"  ✅ 详情有 members 数组 ({len(detail['members'])} 人)")
            
            if 'activityInfo' in detail and detail['activityInfo']:
                print(f"  ✅ 详情有 activityInfo")
            else:
                print(f"  ⚠️  详情缺少 activityInfo（可能还未填写）")
    
    return issues

def main():
    print("\n" + "="*70)
    print("  测试参赛者完整流程")
    print("="*70)
    print(f"\n共测试 {len(CONTESTANTS)} 个参赛者账号\n")
    
    results = []
    
    for contestant in CONTESTANTS:
        result = test_contestant(contestant)
        results.append(result)
    
    # 检查前端兼容性
    issues = check_frontend_compatibility(results)
    
    # 总结
    print("\n\n" + "="*70)
    print("  📊 测试总结")
    print("="*70)
    
    success_count = len([r for r in results if r is not None])
    print(f"\n成功测试: {success_count}/{len(CONTESTANTS)}")
    
    # 统计报名情况
    total_registrations = sum(len(r['registrations']) for r in results if r)
    print(f"总报名数: {total_registrations}")
    
    if issues:
        print(f"\n⚠️  发现 {len(issues)} 个兼容性问题:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ 所有API都符合前端预期！")
    
    # 前端使用建议
    print("\n" + "="*70)
    print("  🎯 前端使用建议")
    print("="*70)
    
    print("""
1. 报名列表页面 (MyRegistrations.vue):
   - API: GET /api/registrations/my
   - 显示字段: id, projectName, status, groupType, groupCode
   
2. 报名详情页面:
   - API: GET /api/registrations/{id}
   - 数据结构:
     {
       registration: { id, projectName, groupType, status },
       members: [{ name, title, role, department }],
       activityInfo: { theme, methodLabel, subjectTypeLabel },
       projectSummary: { plan, problemAnalysis, implementation, result, review }
     }
   
3. 评审结果页面:
   - API: GET /api/registrations/{id}/review-results
   
4. 注意事项:
   - ✅ 使用 detail.registration.projectName，不是 detail.projectName
   - ✅ 使用 detail.projectSummary，不是 detail.summary
   - ✅ members 数组可能为空（草稿状态）
   - ✅ activityInfo 可能为 null（未填写）
    """)
    
    print("\n" + "="*70)
    print("  ✅ 测试完成")
    print("="*70)

if __name__ == "__main__":
    main()
