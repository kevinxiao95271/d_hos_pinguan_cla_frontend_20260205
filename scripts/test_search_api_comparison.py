# -*- coding: utf-8 -*-
import sys
import codecs
import requests
import json
from datetime import datetime

# 设置输出编码
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "http://localhost:6039"

def test_search_api(api_path, version_name):
    """测试搜索API"""
    print(f"\n{'='*80}")
    print(f"测试 {version_name}: {api_path}")
    print(f"{'='*80}")
    
    url = f"{BASE_URL}{api_path}"
    
    # 测试数据：搜索"杭州 人民"
    payload = {
        "keyword": "人民",
        "region": "杭州市",
        "page": 0,
        "size": 5  # 只取5条，便于对比
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\n📤 请求URL: {url}")
    print(f"📤 请求参数:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    
    try:
        start_time = datetime.now()
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds() * 1000
        
        print(f"\n✅ 响应状态码: {response.status_code}")
        print(f"⏱️  响应时间: {elapsed:.0f}ms")
        
        if response.status_code == 200:
            data = response.json()
            
            # 检查响应结构
            print(f"\n📊 响应数据结构:")
            print(f"  - success: {data.get('success')}")
            print(f"  - message: {data.get('message')}")
            print(f"  - data 类型: {type(data.get('data'))}")
            
            if data.get('success') and data.get('data'):
                result_data = data['data']
                
                # 检查是否是分页结构
                if isinstance(result_data, dict):
                    print(f"\n📋 分页信息:")
                    print(f"  - content: {type(result_data.get('content'))} (长度: {len(result_data.get('content', []))})")
                    print(f"  - totalElements: {result_data.get('totalElements')}")
                    print(f"  - totalPages: {result_data.get('totalPages')}")
                    print(f"  - pageNumber: {result_data.get('number')}")
                    print(f"  - pageSize: {result_data.get('size')}")
                    print(f"  - first: {result_data.get('first')}")
                    print(f"  - last: {result_data.get('last')}")
                    
                    content = result_data.get('content', [])
                else:
                    # 如果data直接是数组
                    content = result_data if isinstance(result_data, list) else []
                    print(f"\n⚠️  data 是数组，长度: {len(content)}")
                
                # 显示前5条数据
                if content and len(content) > 0:
                    print(f"\n📝 前{min(5, len(content))}条机构数据:")
                    for idx, inst in enumerate(content[:5], 1):
                        print(f"\n  [{idx}] {inst.get('name', 'N/A')}")
                        print(f"      - ID: {inst.get('id')}")
                        print(f"      - 地区: {inst.get('region', 'N/A')}")
                        print(f"      - 等级: {inst.get('level', 'N/A')}")
                        print(f"      - 代码: {inst.get('code', 'N/A')}")
                    
                    # 检查第一条数据的所有字段
                    print(f"\n🔍 第一条数据的所有字段:")
                    first_item = content[0]
                    for key in sorted(first_item.keys()):
                        value = first_item[key]
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"      - {key}: {value}")
                    
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "elapsed_ms": elapsed,
                        "structure": {
                            "success": data.get('success'),
                            "has_data": 'data' in data,
                            "data_type": type(data.get('data')).__name__,
                            "is_paginated": isinstance(result_data, dict) and 'content' in result_data
                        },
                        "pagination": {
                            "totalElements": result_data.get('totalElements') if isinstance(result_data, dict) else len(content),
                            "pageSize": result_data.get('size') if isinstance(result_data, dict) else len(content),
                            "content_length": len(content)
                        },
                        "first_item_fields": list(content[0].keys()) if content else [],
                        "sample_data": content[:3] if content else []
                    }
                else:
                    print(f"\n⚠️  没有返回任何机构数据")
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "elapsed_ms": elapsed,
                        "structure": {"empty": True}
                    }
            else:
                print(f"\n❌ API返回失败: {data.get('message')}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": data.get('message')
                }
        else:
            print(f"\n❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text[:200]
            }
    
    except requests.exceptions.Timeout:
        print(f"\n❌ 请求超时（10秒）")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        print(f"\n❌ 请求失败: {type(e).__name__}: {e}")
        return {"success": False, "error": str(e)}


def compare_apis(result1, result2):
    """对比两个API的结果"""
    print(f"\n{'='*80}")
    print(f"对比分析")
    print(f"{'='*80}")
    
    print(f"\n📊 响应性能对比:")
    print(f"  旧接口响应时间: {result1.get('elapsed_ms', 'N/A'):.0f}ms")
    print(f"  新接口响应时间: {result2.get('elapsed_ms', 'N/A'):.0f}ms")
    
    print(f"\n📋 数据结构对比:")
    s1 = result1.get('structure', {})
    s2 = result2.get('structure', {})
    
    print(f"  旧接口:")
    print(f"    - success字段: {s1.get('success')}")
    print(f"    - 有data字段: {s1.get('has_data')}")
    print(f"    - data类型: {s1.get('data_type')}")
    print(f"    - 是否分页: {s1.get('is_paginated')}")
    
    print(f"  新接口:")
    print(f"    - success字段: {s2.get('success')}")
    print(f"    - 有data字段: {s2.get('has_data')}")
    print(f"    - data类型: {s2.get('data_type')}")
    print(f"    - 是否分页: {s2.get('is_paginated')}")
    
    # 对比字段
    fields1 = set(result1.get('first_item_fields', []))
    fields2 = set(result2.get('first_item_fields', []))
    
    print(f"\n🔍 机构对象字段对比:")
    print(f"  旧接口字段数量: {len(fields1)}")
    print(f"  新接口字段数量: {len(fields2)}")
    
    common_fields = fields1 & fields2
    only_in_old = fields1 - fields2
    only_in_new = fields2 - fields1
    
    print(f"  共同字段 ({len(common_fields)}): {sorted(common_fields)}")
    if only_in_old:
        print(f"  ⚠️  只在旧接口: {sorted(only_in_old)}")
    if only_in_new:
        print(f"  ⚠️  只在新接口: {sorted(only_in_new)}")
    
    # 对比数据内容
    print(f"\n📝 数据内容对比（前3条）:")
    
    sample1 = result1.get('sample_data', [])
    sample2 = result2.get('sample_data', [])
    
    print(f"\n旧接口返回顺序:")
    for idx, inst in enumerate(sample1, 1):
        print(f"  [{idx}] {inst.get('name')} - 等级: {inst.get('level', 'N/A')}")
    
    print(f"\n新接口返回顺序:")
    for idx, inst in enumerate(sample2, 1):
        print(f"  [{idx}] {inst.get('name')} - 等级: {inst.get('level', 'N/A')}")
    
    # 判断兼容性
    print(f"\n✅ 兼容性评估:")
    
    compatible = True
    issues = []
    
    # 检查响应结构
    if s1.get('data_type') != s2.get('data_type'):
        compatible = False
        issues.append(f"❌ data类型不一致: {s1.get('data_type')} vs {s2.get('data_type')}")
    else:
        issues.append(f"✅ data类型一致: {s1.get('data_type')}")
    
    if s1.get('is_paginated') != s2.get('is_paginated'):
        compatible = False
        issues.append(f"❌ 分页结构不一致")
    else:
        issues.append(f"✅ 分页结构一致")
    
    # 检查字段
    if only_in_old:
        issues.append(f"⚠️  旧接口有{len(only_in_old)}个新接口没有的字段")
    if only_in_new:
        issues.append(f"⚠️  新接口有{len(only_in_new)}个旧接口没有的字段")
    if not only_in_old and not only_in_new:
        issues.append(f"✅ 字段完全一致")
    
    for issue in issues:
        print(f"  {issue}")
    
    if compatible and not only_in_old and not only_in_new:
        print(f"\n🎉 结论: 两个接口完全兼容，可以安全切换！")
        return True
    elif compatible:
        print(f"\n⚠️  结论: 基本兼容，但字段有差异，需要确认是否影响业务")
        return True
    else:
        print(f"\n❌ 结论: 不兼容，切换前需要修改前端代码！")
        return False


def main():
    print("🔍 机构搜索API对比测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试旧接口
    result_old = test_search_api("/api/institutions/search", "旧接口 (search)")
    
    # 测试新接口
    result_new = test_search_api("/api/institutions/search-v2", "新接口 (search-v2)")
    
    # 对比分析
    if result_old.get('success') and result_new.get('success'):
        is_compatible = compare_apis(result_old, result_new)
        
        print(f"\n{'='*80}")
        print(f"📋 最终建议")
        print(f"{'='*80}")
        
        if is_compatible:
            print(f"\n✅ 可以安全切换到新接口 /api/institutions/search-v2")
            print(f"\n修改位置: src/api/institution.js 第78行")
            print(f"修改内容: url: '/institutions/search-v2'")
        else:
            print(f"\n❌ 不建议直接切换，需要先调整前端代码")
    else:
        print(f"\n❌ 测试失败，无法完成对比")
        if not result_old.get('success'):
            print(f"  - 旧接口测试失败")
        if not result_new.get('success'):
            print(f"  - 新接口测试失败")
    
    print(f"\n{'='*80}")
    print(f"测试完成")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
