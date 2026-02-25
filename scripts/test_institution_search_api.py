#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试机构搜索API - 探测后端是否支持地区筛选和模糊搜索
POST /api/institutions/search
"""

import sys
import codecs
import requests
import json
import time

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = 'http://localhost:6031/api'

def login():
    """登录获取token"""
    url = f'{BASE_URL}/auth/login'
    
    # 使用OPS账号，包含完整参数
    data = {
        'phone': '13800000005',
        'name': 'OPS User 1',
        'title': 'Test Title',
        'role': 'OPS',
        'institutionId': None
    }
    
    try:
        print(f'   尝试登录: {data["name"]} ({data["role"]})')
        start = time.time()
        response = requests.post(url, json=data, timeout=60)
        elapsed = time.time() - start
        print(f'   响应时间: {elapsed:.2f}秒')
        print(f'   状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data', {}).get('token'):
                return result['data']['token']
            else:
                print(f'   失败原因: {result.get("message")}')
                print(f'   完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}')
        else:
            print(f'   HTTP错误: {response.text[:500]}')
    except requests.exceptions.Timeout:
        print(f'   ❌ 登录超时（60秒）')
    except Exception as e:
        print(f'   ❌ 登录异常: {e}')
    return None


def test_institution_search(params, description, token=None):
    """测试机构搜索API"""
    url = f'{BASE_URL}/institutions/search'
    
    print('=' * 80)
    print(f'📊 测试场景: {description}')
    print('=' * 80)
    print(f'URL: {url}')
    print(f'Method: POST')
    print(f'参数: {json.dumps(params, ensure_ascii=False, indent=2)}\n')
    
    try:
        start_time = time.time()
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        response = requests.post(url, json=params, headers=headers, timeout=30)
        elapsed = time.time() - start_time
        
        print(f'⏱️  响应时间: {elapsed:.3f}秒')
        print(f'Status Code: {response.status_code}\n')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API调用成功\n')
            
            if data.get('success'):
                institutions = data.get('data', [])
                
                # 处理分页数据
                if isinstance(institutions, dict):
                    total = institutions.get('total', 0)
                    content = institutions.get('content', [])
                    page = institutions.get('page', 0)
                    size = institutions.get('size', 20)
                    
                    print(f'📈 总记录数: {total}')
                    print(f'📄 当前页: {page + 1}')
                    print(f'📦 每页大小: {size}')
                    print(f'📋 返回数量: {len(content)}\n')
                    
                    institutions = content
                else:
                    print(f'📋 返回数量: {len(institutions)}\n')
                
                if institutions:
                    print('=' * 80)
                    print('📦 第一条机构数据:')
                    print('=' * 80)
                    print(json.dumps(institutions[0], ensure_ascii=False, indent=2))
                    
                    print('\n' + '=' * 80)
                    print('🔍 字段检查:')
                    print('=' * 80)
                    first = institutions[0]
                    fields = ['id', 'name', 'code', 'region', 'level', 'uscc']
                    for field in fields:
                        value = first.get(field)
                        status = '✅' if value is not None else '❌'
                        value_str = str(value)[:50] if value else 'null'
                        print(f'   {status} {field}: {value_str}')
                    
                    # 显示前5条
                    if len(institutions) > 1:
                        print('\n' + '=' * 80)
                        print(f'📋 前5条机构数据:')
                        print('=' * 80)
                        for i, inst in enumerate(institutions[:5], 1):
                            print(f'{i}. {inst.get("name")} - {inst.get("region")} - {inst.get("level")}')
                else:
                    print('⚠️ 未找到匹配的机构')
            else:
                print(f'⚠️ 业务失败: {data.get("message")}')
        elif response.status_code == 401:
            print('⚠️ 需要登录认证（401）')
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            print(f'响应: {response.text[:500]}')
    except requests.exceptions.Timeout:
        print(f'❌ 请求超时（30秒）')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    print()


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 24 + '机构搜索API探测' + ' ' * 24 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    # 先登录
    print('🔐 登录获取Token...')
    token = login()
    if not token:
        print('❌ 登录失败，无法继续测试')
        return 1
    print('✅ 登录成功\n')
    
    print('🎯 测试目标:')
    print('   1. 是否支持按地区筛选？')
    print('   2. 是否支持模糊搜索？')
    print('   3. 是否支持分页（三万多家机构）？')
    print('   4. 响应速度如何？')
    print('   5. 返回字段是否完整？\n')
    
    # 测试场景1: 不带任何参数（可能返回所有或报错）
    test_institution_search({}, '场景1: 不带参数（查看是否需要必填参数）', token)
    
    # 测试场景2: 按地区筛选
    test_institution_search(
        {'region': '杭州'},
        '场景2: 按地区筛选（region=杭州）',
        token
    )
    
    # 测试场景3: 按机构名称模糊搜索
    test_institution_search(
        {'name': '浙江'},
        '场景3: 按名称模糊搜索（name=浙江）',
        token
    )
    
    # 测试场景4: 地区+名称组合搜索
    test_institution_search(
        {'region': '杭州', 'name': '医院'},
        '场景4: 地区+名称组合（region=杭州 & name=医院）',
        token
    )
    
    # 测试场景5: 分页参数
    test_institution_search(
        {'region': '杭州', 'page': 0, 'size': 10},
        '场景5: 带分页参数（page=0, size=10）',
        token
    )
    
    # 测试场景6: 按等级筛选
    test_institution_search(
        {'level': '三级甲等'},
        '场景6: 按等级筛选（level=三级甲等）',
        token
    )
    
    # 测试场景7: 多条件组合
    test_institution_search(
        {'region': '杭州', 'level': '三级甲等', 'name': '浙江', 'page': 0, 'size': 5},
        '场景7: 多条件组合（地区+等级+名称+分页）',
        token
    )
    
    print('=' * 80)
    print('✅ 探测完成')
    print('=' * 80)
    print('\n📝 总结:')
    print('   - 请查看上方测试结果')
    print('   - 确认API是否支持所需的筛选条件')
    print('   - 确认是否支持分页（处理三万多家机构）')
    print('   - 确认响应速度是否可接受')
    print('   - 根据测试结果制定前端实现方案\n')
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
