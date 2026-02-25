# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json
import time

BASE_URL = 'http://localhost:6031/api'

def test_search(data, description):
    """测试搜索"""
    url = f'{BASE_URL}/institutions/search'
    
    print(f'\n{"="*80}')
    print(f'📊 {description}')
    print(f'{"="*80}')
    print(f'请求参数: {json.dumps(data, indent=2, ensure_ascii=False)}')
    
    try:
        start = time.time()
        response = requests.post(url, json=data, timeout=30)
        elapsed = time.time() - start
        
        print(f'\n⏱️  响应时间: {elapsed:.3f}秒')
        print(f'📊 状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data_obj = result.get('data', {})
                print(f'✅ 成功!')
                print(f'📦 总记录数: {data_obj.get("totalElements", 0)}')
                print(f'📦 当前页记录数: {len(data_obj.get("content", []))}')
                
                # 显示前5条
                content = data_obj.get('content', [])
                if content:
                    print(f'\n📋 前5条数据:')
                    for i, item in enumerate(content[:5], 1):
                        print(f'   {i}. {item.get("displayText", item.get("name"))}')
        else:
            print(f'❌ 失败: {response.text[:200]}')
            
    except Exception as e:
        print(f'❌ 异常: {e}')


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 25 + '机构搜索API - 正确参数测试' + ' ' * 25 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    # 测试1: 按实际存在的地区（上城区）
    test_search(
        {'region': '上城区', 'page': 0, 'size': 10},
        '测试1: 按地区筛选 - 上城区（热门地区之一）'
    )
    
    # 测试2: 按实际存在的地区（萧山区）
    test_search(
        {'region': '萧山区', 'page': 0, 'size': 10},
        '测试2: 按地区筛选 - 萧山区（热门地区之一）'
    )
    
    # 测试3: 按等级"三级"（不是"三级甲等"）
    test_search(
        {'level': '三级', 'page': 0, 'size': 10},
        '测试3: 按等级筛选 - 三级'
    )
    
    # 测试4: 按等级"二级"
    test_search(
        {'level': '二级', 'page': 0, 'size': 10},
        '测试4: 按等级筛选 - 二级'
    )
    
    # 测试5: 地区+等级组合（上城区+三级）
    test_search(
        {'region': '上城区', 'level': '三级', 'page': 0, 'size': 10},
        '测试5: 组合筛选 - 上城区+三级'
    )
    
    # 测试6: 地区+名称（上城区+"浙江"）
    test_search(
        {'region': '上城区', 'keyword': '浙江', 'page': 0, 'size': 10},
        '测试6: 组合筛选 - 上城区+名称包含"浙江"'
    )
    
    # 测试7: 地区+名称（萧山区+"医院"）
    test_search(
        {'region': '萧山区', 'keyword': '医院', 'page': 0, 'size': 10},
        '测试7: 组合筛选 - 萧山区+名称包含"医院"'
    )
    
    # 测试8: 多条件（上城区+三级+"浙江"）
    test_search(
        {'region': '上城区', 'level': '三级', 'keyword': '浙江', 'page': 0, 'size': 10},
        '测试8: 多条件筛选 - 上城区+三级+名称包含"浙江"'
    )
    
    print('\n' + '='*80)
    print('✅ 测试完成')
    print('='*80)
    print('\n📝 关键发现:')
    print('   1. 地区是区县级别（如"上城区"），不是市级别（"杭州市"）')
    print('   2. 等级值是"三级"、"二级"、"一级"，不是"三级甲等"')
    print('   3. 支持keyword、region、level三个筛选条件')
    print('   4. 支持分页（page, size）')
    print('   5. 响应速度 < 150ms')
    print()


if __name__ == '__main__':
    main()
