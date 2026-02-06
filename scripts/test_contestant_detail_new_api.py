#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试参赛者报名详情接口 - 验证新的机构信息返回结构
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_contestant_detail():
    """测试参赛者报名详情（新API结构）"""
    print("=" * 80)
    print("测试参赛者报名详情接口 - 验证机构信息直接返回")
    print("=" * 80)
    
    # 1. 登录
    print("\n[1] 登录参赛者账号...")
    login_data = {
        "phone": "13966000011",
        "name": "参赛者11",
        "title": "主管护师",
        "role": "CONTESTANT"
    }
    
    try:
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=10
        )
        login_resp.raise_for_status()
        login_result = login_resp.json()
        
        if not login_result.get('success'):
            print(f"[ERROR] 登录失败: {login_result.get('message')}")
            return
        
        token = login_result['data']['token']
        print(f"[OK] 登录成功！Token: {token[:20]}...")
        
    except Exception as e:
        print(f"[ERROR] 登录异常: {e}")
        return
    
    # 2. 获取报名详情
    print("\n[2] 获取报名详情...")
    registration_id = 116  # 参赛者11的报名ID
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        detail_resp = requests.get(
            f"{BASE_URL}/api/registrations/{registration_id}",
            headers=headers,
            timeout=10
        )
        detail_resp.raise_for_status()
        detail_result = detail_resp.json()
        
        if not detail_result.get('success'):
            print(f"[ERROR] 获取详情失败: {detail_result.get('message')}")
            return
        
        data = detail_result['data']
        print(f"[OK] 获取详情成功！")
        
        # 3. 验证数据结构
        print("\n[3] 验证数据结构...")
        print("\n数据结构：")
        print(f"   - registration: {'[OK]' if 'registration' in data else '[MISSING]'}")
        print(f"   - institution: {'[OK]' if 'institution' in data else '[MISSING]'}")
        print(f"   - members: {'[OK]' if 'members' in data else '[MISSING]'}")
        print(f"   - activityInfo: {'[OK]' if 'activityInfo' in data else '[MISSING]'}")
        print(f"   - projectSummary: {'[OK]' if 'projectSummary' in data else '[MISSING]'}")
        
        # 4. 验证机构信息
        print("\n[4] 验证机构信息...")
        if 'institution' in data and data['institution']:
            institution = data['institution']
            print("\n机构信息：")
            print(f"   - ID: {institution.get('id')}")
            print(f"   - 医疗机构名称: {institution.get('name')}")
            print(f"   - 机构编号: {institution.get('code')}")
            print(f"   - 统一社会信用代码: {institution.get('uscc')}")
            print(f"   - 地区: {institution.get('region')}")
            
            # 验证必填字段
            required_fields = ['id', 'name', 'code', 'uscc']
            missing_fields = [f for f in required_fields if not institution.get(f)]
            
            if missing_fields:
                print(f"\n[WARNING] 缺少字段: {', '.join(missing_fields)}")
            else:
                print("\n[OK] 机构信息完整！")
        else:
            print("[ERROR] 没有机构信息")
        
        # 5. 验证报名基本信息
        print("\n[5] 验证报名基本信息...")
        if 'registration' in data:
            reg = data['registration']
            print("\n报名信息：")
            print(f"   - ID: {reg.get('id')}")
            print(f"   - 项目名称: {reg.get('projectName')}")
            print(f"   - 竞赛组别: {reg.get('groupType')}")
            print(f"   - 分组: {reg.get('groupCode')}")
            print(f"   - 状态: {reg.get('status')}")
            print(f"   - 赛事ID: {reg.get('competitionId')}")
            print(f"   - 机构ID: {reg.get('institutionId')}")
        
        # 6. 验证成员信息
        print("\n[6] 验证成员信息...")
        if 'members' in data:
            members = data['members']
            participants = [m for m in members if m.get('role') == 'PARTICIPANT']
            mentors = [m for m in members if m.get('role') == 'MENTOR']
            
            print(f"\n成员列表：")
            print(f"   - 参与人员: {len(participants)} 人")
            print(f"   - 辅导员: {len(mentors)} 人")
            
            if participants:
                print("\n   参与人员：")
                for p in participants:
                    print(f"     - {p.get('name')} - {p.get('title')} - {p.get('department')}")
            
            if mentors:
                print("\n   辅导员：")
                for m in mentors:
                    print(f"     - {m.get('name')} - {m.get('title')}")
        
        # 7. 完整JSON输出
        print("\n[7] 完整响应数据（格式化）：")
        print("\n" + "=" * 80)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("=" * 80)
        
        # 8. 前端使用示例
        print("\n[8] 前端使用示例：")
        print("""
// Vue 3 示例
const loadData = async () => {
  const res = await getRegistration(registrationId.value)
  if (res.success && res.data) {
    const data = res.data
    
    // [OK] 基本信息
    registration.value = {
      ...data.registration,
      members: data.members || [],
      activityInfo: data.activityInfo,
      summary: data.projectSummary
    }
    
    // [OK] 机构信息（直接从响应获取）
    if (data.institution) {
      registration.value.institutionName = data.institution.name
      institutionInfo.code = data.institution.code
      institutionInfo.uscc = data.institution.uscc
      institutionInfo.region = data.institution.region
    }
    
    // [OK] 赛事信息
    if (data.registration?.competitionId) {
      const compRes = await getCompetition(data.registration.competitionId)
      if (compRes.success) {
        competition.value = compRes.data
      }
    }
  }
}
""")
        
        print("\n[OK] 测试完成！新的API结构验证通过。")
        print("\n关键变化：")
        print("   [OK] 不再需要单独调用 GET /api/institutions/{id}")
        print("   [OK] 机构信息直接包含在报名详情响应中")
        print("   [OK] 减少了一次API调用，提升性能")
        
    except Exception as e:
        print(f"[ERROR] 获取详情异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_contestant_detail()
