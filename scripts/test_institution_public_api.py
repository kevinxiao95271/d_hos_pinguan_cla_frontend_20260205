# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json
import time

BASE_URL = 'http://localhost:6031/api'

def test_api(method, endpoint, params=None, data=None, description=''):
    """测试API"""
    url = f'{BASE_URL}{endpoint}'
    
    print(f'\n{"="*80}')
    print(f'📊 测试: {description}')
    print(f'{"="*80}')
    print(f'URL: {url}')
    print(f'Method: {method}')
    if params:
        print(f'参数: {json.dumps(params, indent=2, ensure_ascii=False)}')
    if data:
        print(f'请求体: {json.dumps(data, indent=2, ensure_ascii=False)}')
    
    try:
        start = time.time()
        
        if method == 'GET':
            response = requests.get(url, params=params, timeout=30)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=30)
        
        elapsed = time.time() - start
        
        print(f'\n⏱️  响应时间: {elapsed:.3f}秒')
        print(f'📊 状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'✅ 成功!')
            
            if result.get('success'):
                data_obj = result.get('data', {})
                
                # 如果是分页数据
                if isinstance(data_obj, dict) and 'content' in data_obj:
                    print(f'📦 返回数据:')
                    print(f'   - 总记录数: {data_obj.get("totalElements", 0)}')
                    print(f'   - 总页数: {data_obj.get("totalPages", 0)}')
                    print(f'   - 当前页: {data_obj.get("number", 0) + 1}')
                    print(f'   - 页大小: {data_obj.get("size", 0)}')
                    print(f'   - 当前页记录数: {len(data_obj.get("content", []))}')
                    
                    # 显示前3条数据示例
                    content = data_obj.get('content', [])
                    if content:
                        print(f'\n📋 前3条数据示例:')
                        for i, item in enumerate(content[:3], 1):
                            print(f'   {i}. {item.get("name", "N/A")} - {item.get("region", "N/A")} - {item.get("level", "N/A")}')
                            if 'displayText' in item:
                                print(f'      显示文本: {item["displayText"]}')
                
                # 如果是列表数据
                elif isinstance(data_obj, list):
                    print(f'📦 返回列表，共 {len(data_obj)} 项')
                    if data_obj:
                        print(f'\n📋 前10项:')
                        for i, item in enumerate(data_obj[:10], 1):
                            if isinstance(item, dict):
                                print(f'   {i}. {json.dumps(item, ensure_ascii=False)}')
                            else:
                                print(f'   {i}. {item}')
                
                else:
                    print(f'📦 返回数据: {json.dumps(data_obj, indent=2, ensure_ascii=False)[:500]}')
            else:
                print(f'⚠️  API返回success=false')
                print(f'消息: {result.get("message")}')
        else:
            print(f'❌ 失败')
            print(f'错误: {response.text[:500]}')
            
    except requests.exceptions.Timeout:
        print(f'❌ 请求超时（30秒）')
    except Exception as e:
        print(f'❌ 异常: {e}')


def main():
    print('╔' + '═' * 78 + '╗')
    print('║' + ' ' * 20 + '机构搜索API探测（公开接口，无需Token）' + ' ' * 20 + '║')
    print('╚' + '═' * 78 + '╝\n')
    
    print('🎯 测试目标:')
    print('   1. 验证机构搜索API是否公开（不需要Token）')
    print('   2. 是否支持按地区筛选')
    print('   3. 是否支持模糊搜索')
    print('   4. 是否支持分页')
    print('   5. 响应速度和返回字段')
    print('   6. 辅助接口（热门地区、地区列表、等级列表）')
    
    # 测试1: 热门地区
    test_api('GET', '/institutions/hot-regions', params={'limit': 10}, 
             description='1. 热门地区接口（推荐）')
    
    # 测试2: 地区列表
    test_api('GET', '/institutions/regions', 
             description='2. 地区列表接口（筛选器）')
    
    # 测试3: 等级列表
    test_api('GET', '/institutions/levels', 
             description='3. 等级列表接口（筛选器）')
    
    # 测试4: POST搜索（空参数）
    test_api('POST', '/institutions/search', data={}, 
             description='4. 搜索接口 - 不带参数（查看默认行为）')
    
    # 测试5: 按地区筛选
    test_api('POST', '/institutions/search', 
             data={'region': '杭州市', 'page': 0, 'size': 10}, 
             description='5. 搜索接口 - 按地区筛选（杭州市）')
    
    # 测试6: 按名称模糊搜索
    test_api('POST', '/institutions/search', 
             data={'keyword': '人民医院', 'page': 0, 'size': 10}, 
             description='6. 搜索接口 - 名称模糊搜索（人民医院）')
    
    # 测试7: 地区+名称组合
    test_api('POST', '/institutions/search', 
             data={'region': '杭州市', 'keyword': '浙江', 'page': 0, 'size': 10}, 
             description='7. 搜索接口 - 地区+名称组合')
    
    # 测试8: 按等级筛选
    test_api('POST', '/institutions/search', 
             data={'level': '三级甲等', 'page': 0, 'size': 10}, 
             description='8. 搜索接口 - 按等级筛选（三级甲等）')
    
    # 测试9: 多条件组合
    test_api('POST', '/institutions/search', 
             data={
                 'region': '杭州市', 
                 'level': '三级甲等', 
                 'keyword': '浙江',
                 'page': 0, 
                 'size': 5
             }, 
             description='9. 搜索接口 - 多条件组合（地区+等级+名称）')
    
    # 测试10: 自动完成
    test_api('GET', '/institutions/autocomplete', 
             params={'prefix': '浙江'}, 
             description='10. 自动完成接口（实时提示）')
    
    # 测试11: 分页测试（第2页）
    test_api('POST', '/institutions/search', 
             data={'region': '杭州市', 'page': 1, 'size': 10}, 
             description='11. 搜索接口 - 分页测试（第2页）')
    
    print('\n' + '='*80)
    print('✅ 探测完成')
    print('='*80)
    print('\n📝 总结:')
    print('   - 机构搜索API支持的筛选条件')
    print('   - 是否需要Token认证')
    print('   - 分页参数（page, size）')
    print('   - 响应速度')
    print('   - 返回数据格式和字段')
    print()


if __name__ == '__main__':
    main()
