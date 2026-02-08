#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试统计页面的数据处理
验证地区分布中是否还会出现"其他"分类
"""

import sys
import io
import requests
import json

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = 'http://localhost:6031'

# 测试用户（组委会管理员）
TEST_USER = {
    'phone': '13800000041',
    'password': '123456',
    'name': 'CommitteeAdmin A',
    'title': '主任',
    'role': 'COMMITTEE_ADMIN',
    'institutionId': 1
}

def login():
    """登录并获取token"""
    print('🔐 正在登录...')
    
    response = requests.post(
        f'{BASE_URL}/api/auth/login',
        json=TEST_USER,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            token = result.get('data', {}).get('token')
            print(f'✅ 登录成功！Token: {token[:20]}...')
            return token
        else:
            print(f'❌ 登录失败: {result.get("message")}')
            return None
    else:
        print(f'❌ 登录请求失败: {response.status_code}')
        return None

def test_filter_registrations(token, competition_id=21):
    """测试 filterRegistrations 接口"""
    print(f'\n📊 测试 filterRegistrations 接口 (赛事ID={competition_id})')
    print('=' * 80)
    
    response = requests.get(
        f'{BASE_URL}/api/admin/registrations/filter',
        params={'competitionId': competition_id},
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            registrations = result.get('data', [])
            print(f'✅ 获取到 {len(registrations)} 条报名数据')
            
            # 检查字段
            if registrations:
                sample = registrations[0]
                print(f'\n📝 第一条数据的字段:')
                print(f'   institutionName: {sample.get("institutionName")}')
                print(f'   institutionRegion: {sample.get("institutionRegion")} ', end='')
                if sample.get("institutionRegion"):
                    print('✅ 有地区字段')
                else:
                    print('❌ 缺少地区字段')
                print(f'   subjectTypeLabel: {sample.get("subjectTypeLabel")}')
                print(f'   groupType: {sample.get("groupType")}')
            
            # 统计地区分布（模拟前端逻辑）
            print(f'\n📍 地区分布统计:')
            print('-' * 80)
            
            region_counts = {}
            city_keywords = ['杭州', '宁波', '温州', '绍兴', '嘉兴', '湖州', 
                           '金华', '衢州', '台州', '丽水', '舟山']
            
            # 省级医院白名单（这些医院虽然不包含城市名，但都在杭州）
            province_hospitals = [
                '浙江大学医学院附属第一医院', '浙一医院',
                '浙江大学医学院附属第二医院', '浙二医院',
                '浙江大学医学院附属邵逸夫医院', '邵逸夫医院',
                '浙江大学医学院附属儿童医院', '浙江省儿童医院',
                '浙江大学医学院附属口腔医院', '浙江省口腔医院',
                '浙江大学医学院附属妇产科医院', '浙江省妇产科医院',
                '浙江省人民医院', '浙江医院', '浙江省中医院',
                '浙江省立同德医院', '浙江省肿瘤医院', '浙江省新华医院',
                '浙江中医药大学附属第一医院', '浙江省中医院',
                '浙江中医药大学附属第二医院', '新华医院',
                '浙江中医药大学附属第三医院', '中山医院'
            ]
            
            no_region_count = 0
            for r in registrations:
                region = None
                
                # 1. 优先使用后端的 institutionRegion
                if r.get('institutionRegion'):
                    region = r.get('institutionRegion')
                else:
                    # 2. 识别地区
                    institution_name = r.get('institutionName', '')
                    
                    # 2.1 检查是否为省级医院（归类到杭州）
                    is_province_hospital = any(keyword in institution_name 
                                              for keyword in province_hospitals)
                    
                    if is_province_hospital:
                        region = '杭州'
                    else:
                        # 2.2 城市关键词匹配
                        for city in city_keywords:
                            if city in institution_name:
                                region = city
                                break
                    
                    # 3. 无法识别
                    if not region and institution_name:
                        print(f'⚠️  无法识别地区: {institution_name}')
                        region = '未知地区'
                        no_region_count += 1
                
                if region:
                    region_counts[region] = region_counts.get(region, 0) + 1
            
            # 排序并显示
            sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
            total = len(registrations)
            
            print(f'\n地区名称            数量      占比')
            print('-' * 80)
            for region, count in sorted_regions:
                percentage = (count / total * 100) if total > 0 else 0
                marker = '⚠️' if region == '未知地区' else '  '
                print(f'{marker} {region:<15} {count:>3}      {percentage:>5.2f}%')
            print('-' * 80)
            print(f'总计                {total:>3}     100.00%')
            
            if no_region_count > 0:
                print(f'\n⚠️  有 {no_region_count} 条数据无法识别地区')
            else:
                print(f'\n✅ 所有数据都能识别地区')
            
            # 统计主题类型
            print(f'\n📚 主题类型分布统计:')
            print('-' * 80)
            
            subject_counts = {}
            for r in registrations:
                subject = r.get('subjectTypeLabel', '未知')
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
            
            sorted_subjects = sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)
            
            print(f'\n主题类型            数量      占比')
            print('-' * 80)
            for subject, count in sorted_subjects:
                percentage = (count / total * 100) if total > 0 else 0
                marker = '📌' if subject == '其他' else '  '
                print(f'{marker} {subject:<15} {count:>3}      {percentage:>5.2f}%')
            print('-' * 80)
            print(f'总计                {total:>3}     100.00%')
            
            # 组别统计
            print(f'\n🏆 竞赛组别统计:')
            print('-' * 80)
            
            group_counts = {}
            for r in registrations:
                group = r.get('groupType', '未知')
                group_counts[group] = group_counts.get(group, 0) + 1
            
            group_names = {
                'BASIC': '基层组',
                'COMPREHENSIVE': '综合组',
                'ADVANCED': '进阶组'
            }
            
            for group_type, group_name in group_names.items():
                count = group_counts.get(group_type, 0)
                percentage = (count / total * 100) if total > 0 else 0
                print(f'{group_name:<15} {count:>3}      {percentage:>5.2f}%')
            
            return True
        else:
            print(f'❌ 请求失败: {result.get("message")}')
            return False
    else:
        print(f'❌ HTTP 请求失败: {response.status_code}')
        return False

def test_stats_summary(token):
    """测试 getStatsSummary 接口"""
    print(f'\n📊 测试 getStatsSummary 接口')
    print('=' * 80)
    
    response = requests.get(
        f'{BASE_URL}/api/admin/stats/summary',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result.get('data', {})
            print(f'✅ 获取到统计数据')
            print(f'\n赛事信息:')
            print(f'   赛事ID: {data.get("competitionId")}')
            print(f'   赛事名称: {data.get("competitionName")}')
            print(f'   报名总数: {data.get("registrationCount")}')
            
            # 地区分布
            region_counts = data.get('regionCounts', {})
            print(f'\n📍 后端返回的地区分布:')
            print('-' * 80)
            if region_counts:
                total = sum(region_counts.values())
                sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
                
                print(f'地区名称            数量      占比')
                print('-' * 80)
                for region, count in sorted_regions:
                    percentage = (count / total * 100) if total > 0 else 0
                    marker = '⚠️' if region in ['其他', '未知地区'] else '  '
                    print(f'{marker} {region:<15} {count:>3}      {percentage:>5.2f}%')
                print('-' * 80)
                print(f'总计                {total:>3}     100.00%')
                
                if '其他' in region_counts:
                    print(f'\n⚠️  后端数据中包含"其他"分类: {region_counts["其他"]} 条')
                else:
                    print(f'\n✅ 后端数据中没有"其他"分类')
            else:
                print('⚠️  没有地区分布数据')
            
            # 主题类型分布
            subject_counts = data.get('subjectTypeCounts', {})
            print(f'\n📚 后端返回的主题类型分布:')
            print('-' * 80)
            if subject_counts:
                total = sum(subject_counts.values())
                sorted_subjects = sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)
                
                print(f'主题类型            数量      占比')
                print('-' * 80)
                for subject, count in sorted_subjects:
                    percentage = (count / total * 100) if total > 0 else 0
                    marker = '📌' if subject == '其他' else '  '
                    print(f'{marker} {subject:<15} {count:>3}      {percentage:>5.2f}%')
                print('-' * 80)
                print(f'总计                {total:>3}     100.00%')
            else:
                print('⚠️  没有主题类型分布数据')
            
            return True
        else:
            print(f'❌ 请求失败: {result.get("message")}')
            return False
    else:
        print(f'❌ HTTP 请求失败: {response.status_code}')
        return False

def main():
    print('🧪 测试统计页面数据处理')
    print('=' * 80)
    
    # 登录
    token = login()
    if not token:
        return
    
    # 测试最新赛事的统计接口
    test_stats_summary(token)
    
    # 测试赛事ID=21的详细数据
    test_filter_registrations(token, competition_id=21)
    
    print('\n' + '=' * 80)
    print('✅ 测试完成！')
    print('\n📝 总结：')
    print('   - 如果后端返回了 institutionRegion 字段，前端应该使用它')
    print('   - 如果后端没有返回 institutionRegion，前端会用关键词匹配')
    print('   - 无法匹配的医院会被标记为"未知地区"')
    print('   - 主题类型中的"其他"是后端数据，不是前端计算的')

if __name__ == '__main__':
    main()
