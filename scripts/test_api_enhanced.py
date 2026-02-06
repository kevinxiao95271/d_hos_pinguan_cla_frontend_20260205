#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浙江省品管大赛管理系统 - 增强版API测试脚本
包含针对后端反馈的专项测试
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:6031/api"

class EnhancedAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_info = None
        self.test_results = []
        
    def log(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """记录测试结果"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "data": data
        }
        self.test_results.append(result)
        
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {test_name}: {message}", flush=True)
        if data and not success:
            print(f"  Response: {json.dumps(data, indent=2, ensure_ascii=False)}", flush=True)
    
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get('headers', {})
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        kwargs['headers'] = headers
        
        try:
            response = requests.request(method, url, **kwargs)
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else None
            }
        except Exception as e:
            return {
                "status_code": 0,
                "error": str(e)
            }
    
    def test_login(self, phone: str, name: str, role: str, institution_id: int = None):
        """测试登录"""
        test_name = f"登录测试 - {role}"
        
        login_data = {
            "phone": phone,
            "name": name,
            "title": "Test Title",
            "role": role,
            "institutionId": institution_id,
            "reviewerGroupCode": "A1" if role == "REVIEWER" else None,
            "interviewGroupCode": "A1" if role == "REVIEWER" else None,
            "expertBackground": "MEDICAL" if role == "REVIEWER" else None
        }
        
        response = self.request('POST', '/auth/login', json=login_data)
        
        if response['status_code'] == 200 and response['data'].get('success'):
            data = response['data']['data']
            self.token = data.get('token')
            self.user_info = data
            self.log(test_name, True, f"登录成功，用户: {name}", data)
            return True
        else:
            self.log(test_name, False, "登录失败", response.get('data'))
            return False
    
    def test_registration_members(self, registration_id: int):
        """测试报名成员数据"""
        test_name = "获取报名成员数据"
        
        response = self.request('GET', f'/registrations/{registration_id}')
        
        if response['status_code'] == 200 and response['data'].get('success'):
            data = response['data']['data']
            members = data.get('members', [])
            
            # 按角色统计
            participants = [m for m in members if m.get('role') == 'PARTICIPANT']
            mentors = [m for m in members if m.get('role') == 'MENTOR']
            
            # 验证字段完整性
            all_participants_valid = all(
                all(key in p for key in ['name', 'title', 'department', 'role'])
                for p in participants
            )
            all_mentors_valid = all(
                all(key in m for key in ['name', 'title', 'role'])
                for m in mentors
            )
            
            if all_participants_valid and all_mentors_valid:
                self.log(test_name, True, 
                        f"获取成功，参与人员{len(participants)}人，辅导员{len(mentors)}人，字段完整",
                        {"participants": participants, "mentors": mentors})
            else:
                self.log(test_name, False,
                        f"字段不完整，参与人员{len(participants)}人，辅导员{len(mentors)}人",
                        {"participants": participants, "mentors": mentors})
            
            return data
        else:
            self.log(test_name, False, "获取失败", response.get('data'))
            return None
    
    def test_filter_with_dictionary(self, competition_id: int):
        """测试字典筛选功能"""
        print("\n=== 字典筛选功能测试 ===")
        
        # 1. 获取品管工具字典
        test_name = "获取品管工具字典"
        response = self.request('GET', '/dictionaries/method')
        
        if response['status_code'] == 200 and response['data'].get('success'):
            methods = response['data']['data']
            self.log(test_name, True, f"获取成功，共{len(methods)}项", methods[:3])
            
            # 2. 测试筛选
            if methods and len(methods) > 0:
                test_code = methods[0]['code']
                test_name = f"使用品管工具筛选 - {test_code}"
                
                response = self.request('GET', '/admin/registrations/filter', params={
                    'competitionId': competition_id,
                    'methodCode': test_code
                })
                
                if response['status_code'] == 200 and response['data'].get('success'):
                    data = response['data']['data']
                    
                    # 检查是否包含 methodLabel
                    has_label = all('methodLabel' in item for item in data) if data else True
                    has_subject_label = all('subjectTypeLabel' in item for item in data) if data else True
                    
                    if has_label and has_subject_label:
                        self.log(test_name, True,
                                f"筛选成功，共{len(data)}项，包含methodLabel和subjectTypeLabel",
                                data[:2] if data else [])
                    else:
                        self.log(test_name, False,
                                f"筛选成功但缺少Label字段，共{len(data)}项",
                                data[:2] if data else [])
                else:
                    self.log(test_name, False, "筛选失败", response.get('data'))
        else:
            self.log(test_name, False, "获取字典失败", response.get('data'))
    
    def test_registration_detail_display(self, registration_id: int):
        """测试报名详情显示逻辑"""
        print("\n=== 报名详情显示逻辑测试 ===")
        
        # 1. 获取报名详情
        test_name = "获取报名详情"
        response = self.request('GET', f'/registrations/{registration_id}')
        
        if response['status_code'] == 200 and response['data'].get('success'):
            data = response['data']['data']
            
            # 检查必要字段
            required_fields = ['institutionName', 'institutionId', 'projectName', 'members']
            has_all_fields = all(field in data for field in required_fields)
            
            if has_all_fields:
                self.log(test_name, True,
                        f"详情获取成功，包含所有必要字段",
                        {
                            "institutionName": data.get('institutionName'),
                            "projectName": data.get('projectName'),
                            "membersCount": len(data.get('members', []))
                        })
                
                # 2. 获取机构详情（用于获取code和uscc）
                institution_id = data.get('institutionId')
                if institution_id:
                    test_name = "获取机构详情"
                    inst_response = self.request('GET', f'/institutions/{institution_id}')
                    
                    if inst_response['status_code'] == 200 and inst_response['data'].get('success'):
                        inst_data = inst_response['data']['data']
                        self.log(test_name, True,
                                f"机构详情获取成功",
                                {
                                    "code": inst_data.get('code'),
                                    "uscc": inst_data.get('uscc')
                                })
                    else:
                        self.log(test_name, False, "获取失败", inst_response.get('data'))
            else:
                missing_fields = [f for f in required_fields if f not in data]
                self.log(test_name, False,
                        f"缺少字段: {', '.join(missing_fields)}",
                        data)
        else:
            self.log(test_name, False, "获取失败", response.get('data'))
    
    def run_enhanced_tests(self):
        """运行增强测试"""
        print("=" * 60)
        print("浙江省品管大赛管理系统 - 增强版API测试")
        print("=" * 60)
        
        # 1. 登录组委会账号
        if not self.test_login("13800000041", "CommitteeAdmin A", "COMMITTEE_ADMIN", None):
            print("\n登录失败，终止测试")
            return
        
        # 2. 测试字典筛选功能
        self.test_filter_with_dictionary(competition_id=1)
        
        # 3. 切换到参赛者账号测试详情显示
        if self.test_login("13800000011", "Contestant A", "CONTESTANT", 1):
            # 假设registration_id为1，实际应该从列表获取
            self.test_registration_members(registration_id=1)
            self.test_registration_detail_display(registration_id=1)
        
        # 统计结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        
        total = len(self.test_results)
        success = sum(1 for r in self.test_results if r['success'])
        failed = total - success
        
        print(f"总测试数: {total}")
        print(f"成功: {success}")
        print(f"失败: {failed}")
        print(f"成功率: {success/total*100:.1f}%")
        
        if failed > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        return success == total

if __name__ == '__main__':
    tester = EnhancedAPITester()
    success = tester.run_enhanced_tests()
    
    print("\n" + "=" * 60)
    print("测试说明")
    print("=" * 60)
    print("本测试脚本验证以下功能:")
    print("1. 报名成员数据（参与人员和辅导员）")
    print("2. 字典筛选功能（methodLabel和subjectTypeLabel）")
    print("3. 报名详情显示逻辑（优先使用列表数据）")
    print("\n建议:")
    print("- 如果参赛者登录失败，请使用其他角色测试")
    print("- 如果某个registration_id不存在，请修改脚本中的ID")
    print("- 查看浏览器Network标签验证前端是否按预期调用API")
    
    exit(0 if success else 1)
