#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE_URL = 'http://localhost:6039/api'

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

# 测试账号
test_accounts = [
    ('13800000127', 'committee2026', 'COMMITTEE_ADMIN', '评委会管理员'),
    ('13900000001', 'ops123456', 'OPS', '系统运维'),
]

print_section("新功能测试：密码重置 & 报名删除")

for phone, password, expected_role, role_name in test_accounts:
    print(f"\n{'='*60}")
    print(f"测试账号: {phone} ({role_name})")
    print(f"{'='*60}")
    
    # 登录
    login_res = requests.post(f'{BASE_URL}/auth/login-with-password', json={
        'phone': phone,
        'password': password
    })
    
    if login_res.status_code != 200:
        print(f"❌ 登录失败: {login_res.status_code}")
        continue
    
    login_data = login_res.json()
    if not login_data.get('success'):
        print(f"❌ 登录失败: {login_data.get('message')}")
        continue
    
    token = login_data['data']['token']
    user_role = login_data['data']['role']
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"✅ 登录成功，角色: {user_role}")
    
    # 测试1: 密码重置功能
    print_section(f"测试1: 密码重置 ({role_name})")
    
    # 先查询一个测试用户
    users_res = requests.get(f'{BASE_URL}/admin/users/query', headers=headers, params={
        'page': 0,
        'size': 5,
        'role': 'CONTESTANT'
    })
    
    if users_res.status_code == 200:
        users_data = users_res.json()
        if users_data.get('success') and users_data['data']:
            users_list = users_data['data'] if isinstance(users_data['data'], list) else users_data['data'].get('content', [])
            
            if users_list and len(users_list) > 0:
                test_user = users_list[0]
                test_user_id = test_user['id']
                print(f"选择测试用户: ID={test_user_id}, 姓名={test_user.get('name')}, 手机={test_user.get('phone')}")
                
                # 执行密码重置
                reset_res = requests.post(f'{BASE_URL}/admin/users/{test_user_id}/reset-password', headers=headers)
                print(f"\n密码重置响应:")
                print(f"  状态码: {reset_res.status_code}")
                print(f"  响应: {reset_res.text}")
                
                if reset_res.status_code == 200:
                    reset_data = reset_res.json()
                    if reset_data.get('success'):
                        new_password = reset_data['data'].get('newPassword')
                        print(f"  ✅ 密码重置成功")
                        print(f"  新密码: {new_password}")
                        print(f"  密码长度: {len(new_password) if new_password else 0}位")
                    else:
                        print(f"  ❌ 密码重置失败: {reset_data.get('message')}")
                elif reset_res.status_code == 403:
                    print(f"  ⚠️  权限不足（预期结果，非OPS角色）")
                else:
                    print(f"  ❌ 请求失败")
            else:
                print("⚠️  没有可测试的用户")
        else:
            print(f"❌ 查询用户失败: {users_data.get('message')}")
    else:
        print(f"❌ 查询用户失败: {users_res.status_code}")
    
    # 测试2: 报名删除功能
    print_section(f"测试2: 报名删除 ({role_name})")
    
    # 查询一些报名记录
    reg_res = requests.get(f'{BASE_URL}/admin/registrations/filter', headers=headers, params={
        'competitionId': 1,
        'status': 'DRAFT',
        'page': 0,
        'size': 3
    })
    
    if reg_res.status_code == 200:
        reg_data = reg_res.json()
        if reg_data.get('success'):
            regs = reg_data['data'] if isinstance(reg_data['data'], list) else reg_data['data'].get('content', [])
            
            if regs and len(regs) > 0:
                # 选择第一个草稿状态的报名进行测试
                test_reg = regs[0]
                test_reg_id = test_reg.get('id') or test_reg.get('registrationId')
                project_name = test_reg.get('projectName', '')
                print(f"选择测试报名: ID={test_reg_id}, 项目名称={project_name}")
                
                # 执行删除
                del_res = requests.delete(f'{BASE_URL}/admin/registrations/{test_reg_id}', headers=headers)
                print(f"\n删除报名响应:")
                print(f"  状态码: {del_res.status_code}")
                print(f"  响应: {del_res.text}")
                
                if del_res.status_code == 200:
                    del_data = del_res.json()
                    if del_data.get('success'):
                        print(f"  ✅ 删除成功")
                    else:
                        print(f"  ❌ 删除失败: {del_data.get('message')}")
                elif del_res.status_code == 403:
                    print(f"  ⚠️  权限不足（预期结果，非OPS角色）")
                else:
                    print(f"  ❌ 请求失败")
                
                # 验证删除结果
                if del_res.status_code == 200:
                    print(f"\n验证删除结果:")
                    verify_res = requests.get(f'{BASE_URL}/admin/registrations/{test_reg_id}', headers=headers)
                    if verify_res.status_code == 404:
                        print(f"  ✅ 报名记录已删除（404 Not Found）")
                    elif verify_res.status_code == 200:
                        print(f"  ❌ 报名记录仍然存在")
                    else:
                        print(f"  状态码: {verify_res.status_code}")
            else:
                print("⚠️  没有可测试的草稿报名")
        else:
            print(f"❌ 查询报名失败: {reg_data.get('message')}")
    else:
        print(f"❌ 查询报名失败: {reg_res.status_code}")
    
    print()  # 分隔不同账号的测试

# 总结
print_section("测试总结")

print("""
预期结果：

1️⃣ 密码重置功能：
   ✅ OPS角色：可以重置密码，返回6位新密码
   ⚠️  其他角色：权限不足（403）

2️⃣ 报名删除功能：
   ✅ OPS角色：可以删除报名，级联删除相关数据
   ⚠️  其他角色：权限不足（403）

3️⃣ 级联删除顺序：
   ReviewScore → ReviewTask → MaterialFile(+MinIO清理) → 
   RegistrationMember → ActivityInfo → ProjectSummary → Registration
""")
