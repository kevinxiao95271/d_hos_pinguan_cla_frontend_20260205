#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浙江省品管大赛管理系统 - API测试脚本
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:6031/api"

class APITester:
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
    
    def test_get_competitions(self):
        """测试获取赛事列表"""
        test_name = "获取赛事列表"
        
        response = self.request('GET', '/competitions')
        
        if response['status_code'] == 200 and response['data'].get('success'):
            data = response['data']['data']
            self.log(test_name, True, f"获取成功，共 {len(data) if data else 0} 个赛事", data)
            return data
        else:
            self.log(test_name, False, "获取失败", response.get('data'))
            return None
    
    def test_get_institutions(self):
        """测试获取机构列表"""
        test_name = "获取机构列表"
        
        response = self.request('GET', '/institutions')
        
        if response['status_code'] == 200 and response['data'].get('success'):
            data = response['data']['data']
            self.log(test_name, True, f"获取成功，共 {len(data) if data else 0} 个机构", data)
            return data
        else:
            self.log(test_name, False, "获取失败", response.get('data'))
            return None
    
    def test_get_dictionaries(self, dict_type: str):
        """测试获取字典"""
        test_name = f"获取字典 - {dict_type}"
        
        response = self.request('GET', f'/dictionaries/{dict_type}')
        
        if response['status_code'] == 200 and response['data'].get('success'):
            data = response['data']['data']
            self.log(test_name, True, f"获取成功，共 {len(data) if data else 0} 项", data)
            return data
        else:
            self.log(test_name, False, "获取失败", response.get('data'))
            return None
    
    def test_contestant_flow(self):
        """测试参赛者流程"""
        print("\n=== 参赛者流程测试 ===")
        
        # 登录
        if not self.test_login("13800000011", "Contestant A", "CONTESTANT", 1):
            return
        
        # 获取赛事列表
        competitions = self.test_get_competitions()
        
        # 获取我的报名
        if self.user_info:
            test_name = "获取我的报名"
            response = self.request('GET', '/registrations/by-applicant', 
                                  params={'applicantId': self.user_info['id']})
            
            if response['status_code'] == 200 and response['data'].get('success'):
                data = response['data']['data']
                self.log(test_name, True, f"获取成功，共 {len(data) if data else 0} 个报名", data)
            else:
                self.log(test_name, False, "获取失败", response.get('data'))
    
    def test_reviewer_flow(self):
        """测试评审专家流程"""
        print("\n=== 评审专家流程测试 ===")
        
        # 登录
        if not self.test_login("13800000021", "Reviewer A", "REVIEWER", 2):
            return
        
        # 获取评审任务
        if self.user_info:
            test_name = "获取评审任务"
            response = self.request('GET', '/reviews/tasks', 
                                  params={'reviewerId': self.user_info['id']})
            
            if response['status_code'] == 200 and response['data'].get('success'):
                data = response['data']['data']
                self.log(test_name, True, f"获取成功，共 {len(data) if data else 0} 个任务", data)
            else:
                self.log(test_name, False, "获取失败", response.get('data'))
    
    def test_committee_flow(self):
        """测试赛事组委会流程"""
        print("\n=== 赛事组委会流程测试 ===")
        
        # 登录
        if not self.test_login("13800000041", "CommitteeAdmin A", "COMMITTEE_ADMIN"):
            return
        
        # 获取赛事列表
        competitions = self.test_get_competitions()
        
        # 获取统计数据
        test_name = "获取统计数据"
        response = self.request('GET', '/admin/stats/summary')
        
        if response['status_code'] == 200 and response['data'].get('success'):
            data = response['data']['data']
            self.log(test_name, True, "获取成功", data)
        else:
            self.log(test_name, False, "获取失败", response.get('data'))
    
    def test_ops_flow(self):
        """测试系统运维流程"""
        print("\n=== 系统运维流程测试 ===")
        
        # 登录
        if not self.test_login("13800000051", "Ops A", "OPS"):
            return
        
        # 获取机构列表
        self.test_get_institutions()
        
        # 获取字典
        dict_types = ['subject_type', 'method', 'experience_improve', 'quality_topic']
        for dict_type in dict_types:
            self.test_get_dictionaries(dict_type)
        
        # 获取数据源信息
        test_name = "获取数据源信息"
        response = self.request('GET', '/admin/datasource')
        
        if response['status_code'] == 200 and response['data'].get('success'):
            data = response['data']['data']
            self.log(test_name, True, "获取成功", data)
        else:
            self.log(test_name, False, "获取失败", response.get('data'))
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("浙江省品管大赛管理系统 - API测试")
        print("=" * 60)
        
        self.test_contestant_flow()
        self.test_reviewer_flow()
        self.test_committee_flow()
        self.test_ops_flow()
        
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
    tester = APITester()
    success = tester.run_all_tests()
    
    exit(0 if success else 1)
