# -*- coding: utf-8 -*-
import sys
import codecs
import requests
import json

# 设置输出编码
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_levels_api():
    """探测等级API - 找出"三甲"、"二甲"数据的来源"""
    
    base_url = "http://localhost:6031"
    api_url = f"{base_url}/api/institutions/levels"
    
    print("="*80)
    print("🔍 探测等级下拉框数据来源")
    print("="*80)
    print("")
    print(f"📍 前端调用位置:")
    print(f"   文件: src/components/InstitutionSelector.vue")
    print(f"   代码行: 第283行")
    print(f"   代码: allLevels.value = levelsRes.data")
    print("")
    print(f"📍 API定义位置:")
    print(f"   文件: src/api/institution.js")
    print(f"   代码行: 第139-145行")
    print(f"   函数: getAllLevels()")
    print("")
    print("="*80)
    print(f"🌐 API地址: {api_url}")
    print(f"📝 请求方法: GET")
    print(f"🔓 访问权限: 公开（skipAuth: true，无需Token）")
    print("="*80)
    print("")
    
    try:
        print("⏳ 正在调用API...")
        response = requests.get(api_url, timeout=30)
        
        print(f"✅ HTTP状态码: {response.status_code}")
        print("")
        
        if response.status_code == 200:
            # 解析JSON
            data = response.json()
            
            print("📦 完整响应数据:")
            print("-"*80)
            print(json.dumps(data, ensure_ascii=False, indent=2))
            print("-"*80)
            print("")
            
            # 分析响应结构
            print("🔍 响应结构分析:")
            print(f"   类型: {type(data)}")
            
            if isinstance(data, dict):
                print(f"   包含字段: {list(data.keys())}")
                
                if 'success' in data:
                    print(f"   success: {data.get('success')}")
                
                if 'data' in data:
                    levels_data = data.get('data')
                    print(f"   data 类型: {type(levels_data)}")
                    print(f"   data 内容: {levels_data}")
                    
                    if isinstance(levels_data, list):
                        print(f"   data 长度: {len(levels_data)} 条")
                        print("")
                        print("📋 等级列表详情:")
                        for idx, level in enumerate(levels_data, 1):
                            print(f"      {idx}. {level}")
                
                if 'message' in data:
                    print(f"   message: {data.get('message')}")
            
            elif isinstance(data, list):
                print(f"   直接返回数组，长度: {len(data)}")
                print(f"   内容: {data}")
            
            print("")
            print("="*80)
            print("🎯 问题分析")
            print("="*80)
            
            levels_list = []
            if isinstance(data, dict) and 'data' in data:
                levels_list = data.get('data', [])
            elif isinstance(data, list):
                levels_list = data
            
            if levels_list:
                print(f"✅ 后端返回了 {len(levels_list)} 个等级选项")
                print("")
                print("📊 返回的等级列表:")
                for level in levels_list:
                    print(f"   • {level}")
                print("")
                
                # 检查是否包含"三甲"、"二甲"等
                problematic = []
                if any('三甲' in str(level) or '3' in str(level).upper() for level in levels_list):
                    problematic.append('三甲')
                if any('二甲' in str(level) or '2' in str(level).upper() for level in levels_list):
                    problematic.append('二甲')
                if any('一甲' in str(level) or '1' in str(level).upper() for level in levels_list):
                    problematic.append('一甲')
                
                if problematic:
                    print("❌ 问题发现:")
                    print(f"   后端返回的等级列表包含了医院分级（如：{', '.join(problematic)}）")
                    print("")
                    print("⚠️ 这些是医院的三级甲等、二级甲等分类，不应该出现在机构等级筛选中！")
                else:
                    print("✅ 未发现明显的医院分级数据")
            else:
                print("⚠️ 后端返回的等级列表为空")
            
            print("")
            print("="*80)
            print("📋 需要反馈给后端的信息")
            print("="*80)
            print("")
            print("📍 API地址: GET /api/institutions/levels")
            print("")
            print("❌ 问题描述:")
            print("   前端注册报名页面的机构搜索中，等级下拉框出现了")
            print("   \"三甲\"、\"二甲\" 等医院分级选项，这些数据不正确。")
            print("")
            print("📦 当前API返回数据:")
            if isinstance(data, dict) and 'data' in data:
                print(f"   {json.dumps(data['data'], ensure_ascii=False)}")
            else:
                print(f"   {json.dumps(data, ensure_ascii=False)}")
            print("")
            print("✅ 期望的正确数据:")
            print("   应该返回机构的行政级别，例如：")
            print("   [\"省级\", \"市级\", \"区县级\"] 或者 []（空数组）")
            print("")
            print("💡 建议:")
            print("   1. 如果机构没有等级分类，应该返回空数组 []")
            print("   2. 如果有等级分类，应该是行政级别，而不是医院的三级甲等分类")
            print("   3. 前端会使用这个数据填充等级下拉框，用于筛选机构")
            print("")
            
            return True
        else:
            print(f"❌ API返回非200状态码")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到服务器，请确认后端服务是否运行")
        print(f"   后端地址: {base_url}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_levels_api()
    sys.exit(0 if success else 1)
