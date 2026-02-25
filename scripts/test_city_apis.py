# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json
import time

BASE_URL = 'http://localhost:6031/api'

def test_cities():
    """测试城市列表API"""
    url = f'{BASE_URL}/institutions/cities'
    
    print(f'\n{"="*80}')
    print(f'📊 测试1: 获取城市列表')
    print(f'{"="*80}')
    print(f'URL: {url}')
    
    try:
        start = time.time()
        response = requests.get(url, timeout=30)
        elapsed = time.time() - start
        
        print(f'\n⏱️  响应时间: {elapsed:.3f}秒')
        print(f'📊 状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                cities = result.get('data', [])
                print(f'✅ 成功!')
                print(f'📦 城市数量: {len(cities)}')
                print(f'📋 城市列表: {cities}')
                return cities
        else:
            print(f'❌ 失败: {response.text[:200]}')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    return []


def test_districts(city):
    """测试区县列表API"""
    url = f'{BASE_URL}/institutions/districts'
    
    print(f'\n{"="*80}')
    print(f'📊 测试2: 获取{city}的区县列表')
    print(f'{"="*80}')
    print(f'URL: {url}?city={city}')
    
    try:
        start = time.time()
        response = requests.get(url, params={'city': city}, timeout=30)
        elapsed = time.time() - start
        
        print(f'\n⏱️  响应时间: {elapsed:.3f}秒')
        print(f'📊 状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                districts = result.get('data', [])
                print(f'✅ 成功!')
                print(f'📦 区县数量: {len(districts)}')
                print(f'📋 区县列表: {districts}')
                return districts
        else:
            print(f'❌ 失败: {response.text[:200]}')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    return []


def test_search_by_city(city):
    """测试按市级别搜索"""
    url = f'{BASE_URL}/institutions/search'
    
    print(f'\n{"="*80}')
    print(f'📊 测试3: 按{city}搜索机构')
    print(f'{"="*80}')
    
    data = {'region': city, 'page': 0, 'size': 10}
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
                print(f'📦 总机构数: {data_obj.get("totalElements", 0)}')
                print(f'📦 当前页记录数: {len(data_obj.get("content", []))}')
                
                # 显示前3条
                content = data_obj.get('content', [])
                if content:
                    print(f'\n📋 前3条数据:')
                    for i, item in enumerate(content[:3], 1):
                        print(f'   {i}. {item.get("name")} - {item.get("region")} - {item.get("level", "N/A")}')
                
                return data_obj.get("totalElements", 0)
        else:
            print(f'❌ 失败: {response.text[:200]}')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    return 0


def test_search_by_keyword(keyword):
    """测试按关键词"杭州"搜索"""
    url = f'{BASE_URL}/institutions/search'
    
    print(f'\n{"="*80}')
    print(f'📊 测试4: 按关键词"{keyword}"搜索（测试智能识别）')
    print(f'{"="*80}')
    
    data = {'keyword': keyword, 'page': 0, 'size': 10}
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
                print(f'📦 总机构数: {data_obj.get("totalElements", 0)}')
                
                content = data_obj.get('content', [])
                if content:
                    print(f'\n📋 前3条数据:')
                    for i, item in enumerate(content[:3], 1):
                        print(f'   {i}. {item.get("name")} - {item.get("region")}')
        else:
            print(f'❌ 失败: {response.text[:200]}')
    except Exception as e:
        print(f'❌ 异常: {e}')


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 25 + '城市级别地区API测试' + ' ' * 26 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    print('🎯 测试目标:')
    print('   1. 验证城市列表API（/institutions/cities）')
    print('   2. 验证区县列表API（/institutions/districts）')
    print('   3. 验证按市级别搜索（region=杭州市）')
    print('   4. 验证智能识别（keyword=杭州）')
    
    # 测试1: 获取城市列表
    cities = test_cities()
    
    if not cities:
        print('\n❌ 无法获取城市列表，停止测试')
        return 1
    
    # 测试2: 获取杭州市的区县
    if '杭州市' in cities:
        districts = test_districts('杭州市')
    
    # 测试3: 按"杭州市"搜索
    hangzhou_count = test_search_by_city('杭州市')
    
    # 测试4: 按关键词"杭州"搜索（测试智能识别）
    test_search_by_keyword('杭州')
    
    # 测试5: 按"温州市"搜索
    test_search_by_city('温州市')
    
    # 测试6: 按"上城区"搜索（测试区县级别仍然有效）
    test_search_by_city('上城区')
    
    print('\n' + '='*80)
    print('✅ 测试完成')
    print('='*80)
    print('\n📝 总结:')
    print(f'   1. 城市列表API: {"✅ 可用" if cities else "❌ 不可用"}')
    print(f'   2. 区县列表API: 需查看测试结果')
    print(f'   3. 按市搜索: {"✅ 可用" if hangzhou_count > 0 else "❌ 不可用"}')
    print(f'   4. 智能识别: 需查看测试结果')
    print()


if __name__ == '__main__':
    exit(main())
