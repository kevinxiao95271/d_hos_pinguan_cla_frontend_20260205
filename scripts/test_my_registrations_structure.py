#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试"我的报名"接口，查看是否包含赛事ID
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_my_registrations():
    """测试我的报名接口"""
    print("=" * 80)
    print("测试我的报名接口 - GET /api/registrations/my")
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
        print(f"[OK] 登录成功！")
        
    except Exception as e:
        print(f"[ERROR] 登录异常: {e}")
        return
    
    # 2. 获取我的报名
    print("\n[2] 获取我的报名列表...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.get(
            f"{BASE_URL}/api/registrations/my",
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        if not result.get('success'):
            print(f"[ERROR] 请求失败: {result.get('message')}")
            return
        
        registrations = result.get('data', [])
        print(f"[OK] 获取成功！共 {len(registrations)} 条报名记录")
        
        if not registrations:
            print("[WARNING] 没有报名记录")
            return
        
        # 3. 分析数据结构
        print("\n[3] 分析数据结构...")
        print(f"\n共找到 {len(registrations)} 条报名记录：")
        print("-" * 80)
        
        for idx, reg in enumerate(registrations, 1):
            print(f"\n报名记录 #{idx}:")
            print(f"  ID: {reg.get('id')}")
            print(f"  项目名称: {reg.get('projectName')}")
            print(f"  竞赛组别: {reg.get('groupType')}")
            print(f"  状态: {reg.get('status')}")
            print(f"  赛事ID (competitionId): {reg.get('competitionId')}  ← 关键字段！")
            print(f"  机构ID: {reg.get('institutionId')}")
            print(f"  创建时间: {reg.get('createdAt')}")
            print(f"  提交时间: {reg.get('submittedAt')}")
        
        # 4. 检查关键字段
        print("\n[4] 关键字段检查...")
        sample = registrations[0]
        
        has_competition_id = 'competitionId' in sample and sample.get('competitionId') is not None
        
        if has_competition_id:
            print(f"\n✅ 包含赛事ID字段！")
            print(f"   competitionId = {sample.get('competitionId')}")
            print("\n结论：")
            print("  - 前端可以获取到用户已报名的赛事ID列表")
            print("  - 应该在赛事列表页面判断该赛事是否已报名")
            print("  - 如果已报名，应该禁用'立即报名'按钮或改为'查看报名'")
        else:
            print(f"\n❌ 不包含赛事ID字段！")
            print("  - 无法判断用户已报名哪些赛事")
            print("  - 需要后端添加 competitionId 字段")
        
        # 5. 完整JSON输出
        print("\n[5] 第一条报名的完整数据：")
        print("-" * 80)
        print(json.dumps(sample, indent=2, ensure_ascii=False))
        print("-" * 80)
        
        # 6. 前端修复建议
        if has_competition_id:
            print("\n[6] 前端修复建议...")
            print("""
修改文件：src/views/contestant/Competitions.vue

步骤1: 同时加载赛事列表和我的报名
const myRegistrations = ref([])  // 新增

const loadData = async () => {
  try {
    loading.value = true
    
    // 并行加载赛事列表和我的报名
    const [competitionsRes, myRegsRes] = await Promise.all([
      getCompetitions(),
      getMyRegistrations()
    ])
    
    if (competitionsRes.success) {
      competitions.value = competitionsRes.data || []
    }
    
    if (myRegsRes.success) {
      myRegistrations.value = myRegsRes.data || []
    }
  } finally {
    loading.value = false
  }
}

步骤2: 判断赛事是否已报名
const isRegistered = (competitionId) => {
  return myRegistrations.value.some(
    reg => reg.competitionId === competitionId
  )
}

步骤3: 修改按钮逻辑
const canRegister = (item) => {
  // 只有报名阶段且未报名的才能报名
  return item.stage === 'REGISTER' && !isRegistered(item.id)
}

const getButtonText = (item) => {
  if (isRegistered(item.id)) {
    return '已报名'  // 或 '查看报名'
  }
  return canRegister(item) ? '立即报名' : '报名已结束'
}

const handleButtonClick = (item) => {
  if (isRegistered(item.id)) {
    // 跳转到我的报名详情
    const myReg = myRegistrations.value.find(
      reg => reg.competitionId === item.id
    )
    if (myReg) {
      router.push(`/contestant/registration/${myReg.id}`)
    }
  } else {
    // 跳转到报名页面
    router.push(`/contestant/register/${item.id}`)
  }
}

步骤4: 修改模板
<el-button
  :type="isRegistered(item.id) ? 'default' : 'primary'"
  :disabled="!canRegister(item.id) && !isRegistered(item.id)"
  @click="handleButtonClick(item)"
>
  {{ getButtonText(item) }}
</el-button>
""")
        
    except Exception as e:
        print(f"[ERROR] 获取报名列表异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_my_registrations()
