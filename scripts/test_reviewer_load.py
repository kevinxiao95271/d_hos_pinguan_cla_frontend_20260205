#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试评委列表API - 检查负荷（currentLoad）字段
GET /api/admin/reviewers
"""

import sys
import codecs
import requests
import json

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = 'http://localhost:6031/api'

def login_as_committee():
    """以组委会管理员身份登录"""
    url = f'{BASE_URL}/auth/login'
    data = {
        'phone': '13800000127',
        'name': 'CommitteeAdmin A',
        'role': 'COMMITTEE_ADMIN'
    }
    
    print('🔐 登录组委会管理员账号...')
    response = requests.post(url, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and result.get('data', {}).get('token'):
            token = result['data']['token']
            print(f'✅ 登录成功: {data["name"]}\n')
            return token
    
    print('❌ 登录失败')
    return None


def test_reviewers_api(token):
    """测试评委列表API并检查负荷字段"""
    url = f'{BASE_URL}/admin/reviewers'
    headers = {'Authorization': f'Bearer {token}'}
    
    print('=' * 80)
    print('📊 测试评委列表API - 负荷字段检查')
    print('=' * 80)
    print(f'API端点: {url}')
    print(f'Method: GET')
    print(f'前端显示字段: row.currentLoad\n')
    
    # 使用竞赛21
    params = {'competitionId': '21'}
    print(f'请求参数: {params}\n')
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f'Status Code: {response.status_code}\n')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API调用成功\n')
            
            if data.get('success'):
                # 后端返回可能是列表或带content的对象
                data_payload = data.get('data', [])
                if isinstance(data_payload, dict):
                    reviewers = data_payload.get('content', [])
                else:
                    reviewers = data_payload
                
                print(f'📈 评委总数: {len(reviewers)}\n')
                
                if reviewers:
                    print('=' * 80)
                    print('🔍 第一条评委数据详情:')
                    print('=' * 80)
                    first = reviewers[0]
                    print(json.dumps(first, ensure_ascii=False, indent=2))
                    
                    print('\n' + '=' * 80)
                    print('📋 所有字段列表:')
                    print('=' * 80)
                    for key in sorted(first.keys()):
                        value = first[key]
                        value_type = type(value).__name__
                        print(f'   {key}: {value_type} = {value}')
                    
                    # 重点检查负荷相关字段
                    print('\n' + '=' * 80)
                    print('🎯 负荷相关字段检查:')
                    print('=' * 80)
                    
                    load_fields = ['currentLoad', 'load', 'taskCount', 'reviewCount', 'workload']
                    found_fields = []
                    
                    for field in load_fields:
                        if field in first:
                            found_fields.append(field)
                            print(f'   ✅ 找到字段: {field} = {first[field]} (类型: {type(first[field]).__name__})')
                        else:
                            print(f'   ❌ 未找到字段: {field}')
                    
                    if not found_fields:
                        print('\n   ⚠️  警告: 未找到任何负荷相关字段!')
                        print('   建议检查后端API是否正确返回负荷数据')
                    
                    # 统计所有评委的负荷
                    print('\n' + '=' * 80)
                    print('📊 所有评委负荷统计:')
                    print('=' * 80)
                    print(f'   {"姓名":<10} {"职称":<15} {"负荷(currentLoad)":<15} {"状态":<10}')
                    print('   ' + '-' * 60)
                    
                    total_load = 0
                    zero_load_count = 0
                    
                    for idx, reviewer in enumerate(reviewers[:21], 1):  # 只显示前21个
                        name = reviewer.get('name', 'N/A')
                        title = reviewer.get('title', 'N/A')
                        current_load = reviewer.get('currentLoad', 0)
                        status = reviewer.get('status', 'N/A')
                        
                        total_load += current_load
                        if current_load == 0:
                            zero_load_count += 1
                        
                        print(f'   {name:<10} {title:<15} {current_load:<15} {status:<10}')
                    
                    print('   ' + '-' * 60)
                    print(f'   总计: {len(reviewers)} 位评委')
                    print(f'   总负荷: {total_load}')
                    print(f'   平均负荷: {total_load / len(reviewers):.2f}')
                    print(f'   零负荷评委: {zero_load_count} 位')
                    
                    if zero_load_count == len(reviewers):
                        print('\n   🚨 严重问题: 所有评委的负荷都是0！')
                        print('   这很可能是后端API的问题，请检查：')
                        print('   1. 后端是否正确统计已分配的任务数')
                        print('   2. currentLoad字段是否正确计算')
                        print('   3. 是否包含了"已评分"的任务')
                    
                    # 查询某个具体评委的任务详情
                    print('\n' + '=' * 80)
                    print('🔎 查询具体评委的任务数 (以第一个评委为例):')
                    print('=' * 80)
                    
                    if reviewers:
                        first_reviewer = reviewers[0]
                        reviewer_id = first_reviewer.get('id')
                        reviewer_name = first_reviewer.get('name')
                        
                        print(f'   评委ID: {reviewer_id}')
                        print(f'   评委姓名: {reviewer_name}')
                        print(f'   当前负荷: {first_reviewer.get("currentLoad", 0)}')
                        
                        # 尝试查询该评委的任务列表
                        tasks_url = f'{BASE_URL}/admin/reviews/tasks'
                        tasks_params = {
                            'competitionId': '21',
                            'reviewerId': reviewer_id
                        }
                        
                        print(f'\n   查询任务列表: {tasks_url}')
                        print(f'   参数: {tasks_params}')
                        
                        try:
                            tasks_res = requests.get(tasks_url, headers=headers, params=tasks_params, timeout=30)
                            if tasks_res.status_code == 200:
                                tasks_data = tasks_res.json()
                                if tasks_data.get('success'):
                                    tasks = tasks_data.get('data', [])
                                    print(f'\n   ✅ 该评委实际任务数: {len(tasks)} 个')
                                    
                                    # 统计任务状态
                                    status_count = {}
                                    for task in tasks:
                                        status = task.get('status', 'UNKNOWN')
                                        status_count[status] = status_count.get(status, 0) + 1
                                    
                                    print(f'   任务状态分布: {status_count}')
                                    
                                    if len(tasks) > 0 and first_reviewer.get('currentLoad', 0) == 0:
                                        print('\n   🚨 发现问题: 该评委有任务，但负荷显示为0！')
                                else:
                                    print(f'   ⚠️  查询任务失败: {tasks_data.get("message")}')
                            else:
                                print(f'   ❌ HTTP {tasks_res.status_code}')
                        except Exception as e:
                            print(f'   ❌ 查询任务异常: {e}')
                
                else:
                    print('⚠️  未返回评委数据')
            else:
                print(f'⚠️  业务失败: {data.get("message")}')
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            print(f'   响应: {response.text[:500]}')
    except Exception as e:
        print(f'❌ 异常: {e}')


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 22 + '评委负荷字段问题排查' + ' ' * 23 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    # 登录
    token = login_as_committee()
    if not token:
        print('❌ 无法获取token，终止测试')
        return 1
    
    # 测试评委列表API
    test_reviewers_api(token)
    
    print('\n' + '=' * 80)
    print('✅ 排查完成')
    print('=' * 80)
    print('\n📝 问题反馈给后端：')
    print('   API端点: GET /api/admin/reviewers?competitionId=21')
    print('   问题字段: currentLoad (评委负荷)')
    print('   期望值: 统计该评委的任务总数（包括已评分的任务）')
    print('   实际值: 全部为0')
    print('   建议检查: 后端如何计算currentLoad字段\n')
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
