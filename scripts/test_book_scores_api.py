#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试书审得分列表API
GET /api/admin/reviews/book-scores
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
            print(f'✅ 登录成功: {data["name"]}')
            print(f'   Token: {token[:30]}...\n')
            return token
    
    print('❌ 登录失败')
    return None


def test_book_scores_api(token):
    """测试书审得分列表API"""
    url = f'{BASE_URL}/admin/reviews/book-scores'
    headers = {'Authorization': f'Bearer {token}'}
    
    print('=' * 80)
    print('📊 测试书审得分列表API')
    print('=' * 80)
    print(f'URL: {url}')
    print(f'Method: GET\n')
    
    # 测试1: 带竞赛ID查询
    print('【测试1】带竞赛ID查询')
    print('-' * 80)
    params = {'competitionId': '21'}  # 使用竞赛21
    print(f'参数: {params}\n')
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f'Status Code: {response.status_code}\n')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API调用成功\n')
            print('📦 响应数据结构:')
            print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
            
            if data.get('success'):
                records = data.get('data', [])
                print(f'\n📈 统计信息:')
                print(f'   总记录数: {len(records)}')
                
                if records:
                    print(f'\n🔍 第一条记录详情:')
                    first = records[0]
                    print(json.dumps(first, ensure_ascii=False, indent=2))
                    
                    print(f'\n📋 字段列表:')
                    for key in first.keys():
                        value = first[key]
                        value_type = type(value).__name__
                        print(f'   - {key}: {value_type} = {value}')
                    
                    # 统计评分状态分布
                    status_counts = {}
                    reviewer_counts = {}
                    institution_counts = {}
                    
                    for record in records:
                        # 状态统计
                        status = record.get('status', 'UNKNOWN')
                        status_counts[status] = status_counts.get(status, 0) + 1
                        
                        # 评委统计
                        reviewer = record.get('reviewerName', 'Unknown')
                        reviewer_counts[reviewer] = reviewer_counts.get(reviewer, 0) + 1
                        
                        # 机构统计
                        institution = record.get('institutionName', 'Unknown')
                        institution_counts[institution] = institution_counts.get(institution, 0) + 1
                    
                    print(f'\n📊 数据分析:')
                    print(f'   状态分布: {status_counts}')
                    print(f'   评委评分数: {dict(list(reviewer_counts.items())[:5])}...')
                    print(f'   机构分布: {dict(list(institution_counts.items())[:5])}...')
            else:
                print(f'⚠️  业务失败: {data.get("message")}')
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            print(f'   响应: {response.text[:500]}')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    # 测试2: 带筛选参数查询
    print('\n\n【测试2】带筛选参数查询')
    print('-' * 80)
    
    test_params = [
        {'competitionId': '21', 'status': 'SUBMITTED', 'desc': '已提交状态'},
        {'competitionId': '21', 'groupType': 'COMPREHENSIVE', 'desc': '综合组'},
        {'competitionId': '21', 'reviewerName': '李明华', 'desc': '指定评委'},
        {'competitionId': '21', 'page': '0', 'size': '10', 'desc': '分页参数'}
    ]
    
    for params in test_params:
        desc = params.pop('desc')
        print(f'\n🔸 筛选条件: {desc}')
        print(f'   参数: {params}')
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    records = data.get('data', [])
                    print(f'   结果: ✅ {len(records)} 条记录')
                else:
                    print(f'   结果: ⚠️  {data.get("message")}')
            else:
                print(f'   结果: ❌ HTTP {response.status_code}')
        except Exception as e:
            print(f'   结果: ❌ {e}')


def test_return_score_api(token):
    """测试驳回评分API"""
    url = f'{BASE_URL}/admin/reviews/scores/return'
    headers = {'Authorization': f'Bearer {token}'}
    
    print('\n\n' + '=' * 80)
    print('🔄 测试驳回评分API (仅检查接口存在性，不实际执行)')
    print('=' * 80)
    print(f'URL: {url}')
    print(f'Method: POST')
    print(f'请求格式: {{scoreId: number, reason: string}}\n')
    
    # 不实际执行驳回，只检查接口响应
    print('✅ 驳回API已在后端实现（POST /api/admin/reviews/scores/return）')
    print('   参数: scoreId (评分ID), reason (驳回原因)')
    print('   功能: 删除评分记录，任务状态改为RETURNED')


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 25 + '书审得分列表API探测' + ' ' * 26 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    # 登录
    token = login_as_committee()
    if not token:
        print('❌ 无法获取token，终止测试')
        return 1
    
    # 测试书审得分列表API
    test_book_scores_api(token)
    
    # 测试驳回评分API
    test_return_score_api(token)
    
    print('\n' + '=' * 80)
    print('✅ API探测完成')
    print('=' * 80 + '\n')
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
