#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探测字典API返回数据，检查是否有重复项
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

# 4个字典类型
DICT_TYPES = [
    ('subject_type', '主题类型'),
    ('method', '运用手法'),
    ('experience_improve', '改善就医感受'),
    ('quality_topic', '医疗质量安全主题')
]

def test_dictionary_api(dict_type, dict_name):
    """测试字典API"""
    url = f"{BASE_URL}/dictionaries/{dict_type}"
    print(f"\n{'='*80}")
    print(f"[*] 测试字典类型: {dict_name} ({dict_type})")
    print(f"[*] API地址: GET {url}")
    print(f"{'='*80}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"[OK] HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # 打印响应结构
            print(f"\n[*] 响应结构:")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
            
            # 提取实际数据列表
            if isinstance(data, dict):
                items = data.get('data', [])
            elif isinstance(data, list):
                items = data
            else:
                print(f"[ERROR] 无法识别的数据格式")
                return
            
            print(f"\n[*] 数据统计:")
            print(f"   总条目数: {len(items)}")
            
            # 检查重复项
            if items:
                codes_list = []
                labels_list = []
                
                for idx, item in enumerate(items):
                    code = item.get('code', '')
                    label = item.get('label', '')
                    codes_list.append(code)
                    labels_list.append(label)
                    print(f"   [{idx+1}] code: {code:30s} label: {label}")
                
                # 检测重复的code
                duplicate_codes = [code for code in set(codes_list) if codes_list.count(code) > 1]
                if duplicate_codes:
                    print(f"\n[WARNING] 发现重复的code:")
                    for dup_code in duplicate_codes:
                        indices = [i+1 for i, c in enumerate(codes_list) if c == dup_code]
                        print(f"      code '{dup_code}' 出现在第 {indices} 条")
                
                # 检测重复的label
                duplicate_labels = [label for label in set(labels_list) if labels_list.count(label) > 1]
                if duplicate_labels:
                    print(f"\n[WARNING] 发现重复的label:")
                    for dup_label in duplicate_labels:
                        indices = [i+1 for i, l in enumerate(labels_list) if l == dup_label]
                        print(f"      label '{dup_label}' 出现在第 {indices} 条")
                
                if not duplicate_codes and not duplicate_labels:
                    print(f"\n[OK] 未发现重复项")
        else:
            print(f"[ERROR] 请求失败: {response.text}")
    
    except requests.exceptions.Timeout:
        print(f"[ERROR] 请求超时（30秒）")
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败，请确保后端服务运行在 {BASE_URL}")
    except Exception as e:
        print(f"[ERROR] 错误: {str(e)}")

def main():
    print("="*80)
    print("字典API重复数据检测工具")
    print("="*80)
    
    for dict_type, dict_name in DICT_TYPES:
        test_dictionary_api(dict_type, dict_name)
    
    print(f"\n{'='*80}")
    print("[OK] 检测完成")
    print("="*80)

if __name__ == '__main__':
    main()
