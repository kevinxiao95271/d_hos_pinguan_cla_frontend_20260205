#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
入围管理API测试 - 综合书审和面谈排名
测试核心API是否满足前端需求
"""

import requests
import json
from typing import Dict, List, Optional

BASE_URL = "http://localhost:6031"

class ShortlistAPITester:
    def __init__(self):
        self.token = None
        self.competition_id = 21
        
    def login(self) -> bool:
        """登录获取token"""
        print("=" * 80)
        print("[STEP 1] 登录组委会账号")
        print("=" * 80)
        
        login_data = {
            "phone": "13800000041",
            "name": "CommitteeAdmin A",
            "title": "Admin",
            "role": "COMMITTEE_ADMIN"
        }
        
        try:
            resp = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data,
                timeout=10
            )
            resp.raise_for_status()
            result = resp.json()
            
            if result.get('success'):
                self.token = result['data']['token']
                print(f"✅ 登录成功！")
                return True
            else:
                print(f"❌ 登录失败: {result.get('message')}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def get_headers(self) -> Dict:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_book_rankings(self) -> Optional[List]:
        """测试书审排名API"""
        print("\n" + "=" * 80)
        print("[STEP 2] 测试书审排名API")
        print("=" * 80)
        print(f"接口: GET /api/admin/reviews/rankings")
        print(f"参数: competitionId={self.competition_id}, stage=BOOK")
        
        try:
            resp = requests.get(
                f"{BASE_URL}/api/admin/reviews/rankings",
                params={
                    "competitionId": self.competition_id,
                    "stage": "BOOK"
                },
                headers=self.get_headers(),
                timeout=10
            )
            
            print(f"\n状态码: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"❌ 请求失败: {resp.status_code}")
                try:
                    error = resp.json()
                    print(f"错误信息: {json.dumps(error, ensure_ascii=False, indent=2)}")
                except:
                    print(f"错误信息: {resp.text}")
                return None
            
            result = resp.json()
            
            if not result.get('success'):
                print(f"❌ 接口返回失败: {result.get('message')}")
                return None
            
            data = result.get('data', [])
            print(f"✅ 成功获取书审排名数据")
            print(f"📊 数据数量: {len(data)} 个项目")
            
            if data:
                print(f"\n数据结构示例（第1个项目）:")
                sample = data[0]
                print(json.dumps(sample, ensure_ascii=False, indent=2))
                
                # 检查必需字段
                print(f"\n必需字段检查:")
                required_fields = [
                    'registrationId', 'projectName', 'institutionName', 
                    'groupType', 'avgTotal', 'avgPlan', 'avgProblem', 
                    'avgAction', 'avgSuccess', 'avgReview', 'avgOperation', 
                    'avgPresentation', 'highlights', 'weaknesses'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field in sample:
                        print(f"  ✅ {field}: {type(sample[field]).__name__}")
                    else:
                        print(f"  ❌ {field}: 缺失")
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"\n⚠️ 缺失字段: {', '.join(missing_fields)}")
                    return None
                
                print(f"\n✅ 所有必需字段都存在")
                
            return data
            
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None
    
    def test_interview_rankings(self) -> Optional[List]:
        """测试面谈排名API"""
        print("\n" + "=" * 80)
        print("[STEP 3] 测试面谈排名API")
        print("=" * 80)
        print(f"接口: GET /api/admin/reviews/rankings")
        print(f"参数: competitionId={self.competition_id}, stage=INTERVIEW")
        
        try:
            resp = requests.get(
                f"{BASE_URL}/api/admin/reviews/rankings",
                params={
                    "competitionId": self.competition_id,
                    "stage": "INTERVIEW"
                },
                headers=self.get_headers(),
                timeout=10
            )
            
            print(f"\n状态码: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"❌ 请求失败: {resp.status_code}")
                try:
                    error = resp.json()
                    print(f"错误信息: {json.dumps(error, ensure_ascii=False, indent=2)}")
                except:
                    print(f"错误信息: {resp.text}")
                return None
            
            result = resp.json()
            
            if not result.get('success'):
                print(f"❌ 接口返回失败: {result.get('message')}")
                return None
            
            data = result.get('data', [])
            print(f"✅ 成功获取面谈排名数据")
            print(f"📊 数据数量: {len(data)} 个项目")
            
            if data:
                print(f"\n数据结构示例（第1个项目）:")
                sample = data[0]
                print(json.dumps(sample, ensure_ascii=False, indent=2))
                
                # 检查必需字段
                print(f"\n必需字段检查:")
                required_fields = [
                    'registrationId', 'projectName', 'institutionName', 
                    'groupType', 'avgTotal'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field in sample:
                        print(f"  ✅ {field}: {type(sample[field]).__name__}")
                    else:
                        print(f"  ❌ {field}: 缺失")
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"\n⚠️ 缺失字段: {', '.join(missing_fields)}")
                
            else:
                print(f"\n⚠️ 暂无面谈数据（可能面谈阶段未开始）")
                
            return data
            
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None
    
    def test_review_details(self, registration_id: int):
        """测试评审详情API"""
        print("\n" + "=" * 80)
        print(f"[STEP 4] 测试评审详情API")
        print("=" * 80)
        print(f"接口: GET /api/registrations/{registration_id}/review-details")
        
        try:
            resp = requests.get(
                f"{BASE_URL}/api/registrations/{registration_id}/review-details",
                headers=self.get_headers(),
                timeout=10
            )
            
            print(f"\n状态码: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"❌ 请求失败: {resp.status_code}")
                try:
                    error = resp.json()
                    print(f"错误信息: {json.dumps(error, ensure_ascii=False, indent=2)}")
                except:
                    print(f"错误信息: {resp.text}")
                return None
            
            result = resp.json()
            
            if not result.get('success'):
                print(f"❌ 接口返回失败: {result.get('message')}")
                return None
            
            data = result.get('data', [])
            print(f"✅ 成功获取评审详情")
            print(f"📊 数据数量: {len(data)} 个阶段")
            
            if data:
                print(f"\n详情数据:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                
                # 检查是否包含书审和面谈
                stages = [item.get('stage') for item in data]
                print(f"\n包含的阶段: {stages}")
                
                if 'BOOK' in stages:
                    print(f"  ✅ 包含书审数据")
                else:
                    print(f"  ❌ 缺少书审数据")
                
                if 'INTERVIEW' in stages:
                    print(f"  ✅ 包含面谈数据")
                else:
                    print(f"  ⚠️ 暂无面谈数据")
            
            return data
            
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None
    
    def test_merge_logic(self, book_data: List, interview_data: List):
        """测试前端合并逻辑"""
        print("\n" + "=" * 80)
        print("[STEP 5] 模拟前端合并逻辑")
        print("=" * 80)
        
        if not book_data:
            print("❌ 缺少书审数据，无法合并")
            return
        
        print(f"输入数据:")
        print(f"  - 书审项目数: {len(book_data)}")
        print(f"  - 面谈项目数: {len(interview_data) if interview_data else 0}")
        
        # 创建项目映射
        project_map = {}
        
        # 添加书审数据
        for item in book_data:
            reg_id = item.get('registrationId')
            project_map[reg_id] = {
                'registrationId': reg_id,
                'projectName': item.get('projectName'),
                'institutionName': item.get('institutionName'),
                'groupType': item.get('groupType'),
                'bookScore': item.get('avgTotal'),
                'interviewScore': None,
                'compositeScore': None
            }
        
        # 添加面谈数据
        if interview_data:
            for item in interview_data:
                reg_id = item.get('registrationId')
                if reg_id in project_map:
                    project_map[reg_id]['interviewScore'] = item.get('avgTotal')
                else:
                    project_map[reg_id] = {
                        'registrationId': reg_id,
                        'projectName': item.get('projectName'),
                        'institutionName': item.get('institutionName'),
                        'groupType': item.get('groupType'),
                        'bookScore': None,
                        'interviewScore': item.get('avgTotal'),
                        'compositeScore': None
                    }
        
        # 计算综合得分（权重各50%）
        book_weight = 50
        interview_weight = 50
        
        for project in project_map.values():
            if project['bookScore'] is not None and project['interviewScore'] is not None:
                project['compositeScore'] = (
                    project['bookScore'] * book_weight / 100 +
                    project['interviewScore'] * interview_weight / 100
                )
        
        # 按综合得分排序
        projects = list(project_map.values())
        projects_with_score = [p for p in projects if p['compositeScore'] is not None]
        projects_without_score = [p for p in projects if p['compositeScore'] is None]
        
        projects_with_score.sort(key=lambda x: x['compositeScore'], reverse=True)
        
        # 分配排名
        for idx, project in enumerate(projects_with_score, 1):
            project['rank'] = idx
        
        final_projects = projects_with_score + projects_without_score
        
        print(f"\n合并结果:")
        print(f"  - 总项目数: {len(final_projects)}")
        print(f"  - 有综合得分: {len(projects_with_score)}")
        print(f"  - 待面谈: {len(projects_without_score)}")
        
        print(f"\n前5名项目:")
        for project in final_projects[:5]:
            rank = project.get('rank', '-')
            name = project['projectName']
            book = project['bookScore']
            interview = project['interviewScore']
            composite = project['compositeScore']
            
            book_str = f"{book:.1f}" if book is not None else "-"
            interview_str = f"{interview:.1f}" if interview is not None else "-"
            composite_str = f"{composite:.1f}" if composite is not None else "待面谈"
            
            print(f"  {rank}. {name}")
            print(f"     书审: {book_str} | 面谈: {interview_str} | 综合: {composite_str}")
        
        print(f"\n✅ 前端合并逻辑模拟成功")
        
        return final_projects
    
    def generate_summary(self, book_data, interview_data, merged_data):
        """生成测试总结"""
        print("\n" + "=" * 80)
        print("[SUMMARY] 测试总结")
        print("=" * 80)
        
        print(f"\n1. API可用性:")
        print(f"   {'✅' if book_data else '❌'} 书审排名API - GET /api/admin/reviews/rankings?stage=BOOK")
        print(f"   {'✅' if interview_data is not None else '❌'} 面谈排名API - GET /api/admin/reviews/rankings?stage=INTERVIEW")
        print(f"   {'⚠️' if not interview_data and interview_data is not None else '✅'} 面谈数据 - {len(interview_data) if interview_data else 0} 个项目")
        
        print(f"\n2. 数据完整性:")
        if book_data:
            sample = book_data[0]
            has_all_fields = all(
                field in sample for field in [
                    'registrationId', 'projectName', 'institutionName',
                    'groupType', 'avgTotal'
                ]
            )
            print(f"   {'✅' if has_all_fields else '❌'} 书审数据包含所有必需字段")
        else:
            print(f"   ❌ 无法检查书审数据字段")
        
        print(f"\n3. 合并逻辑:")
        if merged_data:
            print(f"   ✅ 前端可以成功合并书审和面谈数据")
            print(f"   ✅ 综合得分计算正常")
            print(f"   ✅ 排名生成正常")
        else:
            print(f"   ❌ 合并逻辑测试失败")
        
        print(f"\n4. 建议:")
        if not book_data:
            print(f"   ⚠️ 后端需要实现书审排名API")
        
        if interview_data is None:
            print(f"   ⚠️ 后端需要实现面谈排名API")
        elif not interview_data:
            print(f"   ℹ️ 面谈数据为空可能是正常的（面谈阶段未开始）")
        
        print(f"\n5. 前端可以开始开发:")
        can_start = book_data is not None
        if can_start:
            print(f"   ✅ 可以开始前端开发（至少书审API可用）")
            print(f"   ✅ 前端可以先处理只有书审数据的情况")
            print(f"   ✅ 面谈数据可以后续补充")
        else:
            print(f"   ❌ 建议等待后端完善API后再开始")

def main():
    """主测试流程"""
    print("\n")
    print("=" * 80)
    print("入围管理API完整测试")
    print("测试目标：验证综合排名所需的所有API是否可用")
    print("=" * 80)
    print("\n")
    
    tester = ShortlistAPITester()
    
    # 1. 登录
    if not tester.login():
        print("\n❌ 登录失败，无法继续测试")
        return
    
    # 2. 测试书审排名
    book_data = tester.test_book_rankings()
    
    # 3. 测试面谈排名
    interview_data = tester.test_interview_rankings()
    
    # 4. 测试评审详情（使用第一个项目）
    if book_data:
        first_reg_id = book_data[0].get('registrationId')
        tester.test_review_details(first_reg_id)
    
    # 5. 测试前端合并逻辑
    merged_data = None
    if book_data:
        merged_data = tester.test_merge_logic(book_data, interview_data or [])
    
    # 6. 生成总结
    tester.generate_summary(book_data, interview_data, merged_data)
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
