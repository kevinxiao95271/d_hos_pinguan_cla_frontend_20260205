# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json
import random

BASE_URL = 'http://localhost:6031'

print('='*80)
print('探测项目总结API的Swagger文档')
print('='*80)

# 1. 获取swagger文档
print('\n[步骤1] 获取Swagger JSON')
print('-'*80)

try:
    response = requests.get(f'{BASE_URL}/v3/api-docs', timeout=10)
    if response.status_code == 200:
        swagger_data = response.json()
        print('✅ Swagger文档获取成功')
        
        # 查找ProjectSummaryRequest相关的schema
        print('\n[步骤2] 查找 ProjectSummaryRequest 定义')
        print('-'*80)
        
        if 'components' in swagger_data and 'schemas' in swagger_data['components']:
            schemas = swagger_data['components']['schemas']
            
            if 'ProjectSummaryRequest' in schemas:
                schema = schemas['ProjectSummaryRequest']
                print('\n✅ 找到 ProjectSummaryRequest 定义:')
                print(json.dumps(schema, indent=2, ensure_ascii=False))
                
                # 提取字段信息
                if 'properties' in schema:
                    print('\n[步骤3] 字段详细信息')
                    print('-'*80)
                    properties = schema['properties']
                    required = schema.get('required', [])
                    
                    print('\n| 字段名 | 类型 | 必填 | 说明 |')
                    print('|--------|------|------|------|')
                    
                    for field_name, field_info in properties.items():
                        field_type = field_info.get('type', 'unknown')
                        is_required = '✅ 是' if field_name in required else '❌ 否'
                        description = field_info.get('description', '-')
                        example = field_info.get('example', '')
                        
                        desc_full = f"{description}"
                        if example:
                            desc_full += f" (示例: {example})"
                        
                        print(f'| {field_name} | {field_type} | {is_required} | {desc_full} |')
                    
                    print('\n[步骤4] 必填字段列表')
                    print('-'*80)
                    print('必填字段:')
                    for field in required:
                        print(f'  ✅ {field}')
                    
                    print('\n可选字段:')
                    for field_name in properties.keys():
                        if field_name not in required:
                            print(f'  ⚪ {field_name}')
                            
            else:
                print('❌ 未找到 ProjectSummaryRequest 定义')
                print('\n可用的schemas:')
                for schema_name in schemas.keys():
                    if 'Summary' in schema_name or 'Project' in schema_name:
                        print(f'  - {schema_name}')
        
        # 查找相关的API端点
        print('\n[步骤5] 查找项目总结相关的API端点')
        print('-'*80)
        
        if 'paths' in swagger_data:
            for path, methods in swagger_data['paths'].items():
                if 'summary' in path.lower():
                    print(f'\n路径: {path}')
                    for method, details in methods.items():
                        print(f'  方法: {method.upper()}')
                        print(f'  说明: {details.get("summary", "-")}')
                        
                        # 查看requestBody
                        if 'requestBody' in details:
                            request_body = details['requestBody']
                            if 'content' in request_body:
                                content = request_body['content']
                                if 'application/json' in content:
                                    schema_ref = content['application/json'].get('schema', {})
                                    if '$ref' in schema_ref:
                                        ref_name = schema_ref['$ref'].split('/')[-1]
                                        print(f'  请求体类型: {ref_name}')
    else:
        print(f'❌ 无法获取Swagger文档: HTTP {response.status_code}')
        print(f'响应: {response.text[:200]}')

except Exception as e:
    print(f'❌ 异常: {e}')

# 2. 测试实际的API
print('\n' + '='*80)
print('[步骤6] 测试实际API调用（获取token）')
print('='*80)

# 先注册获取token
phone = f'138{random.randint(10000000, 99999999)}'
try:
    response = requests.post(
        f'{BASE_URL}/api/auth/register',
        json={
            'phone': phone,
            'password': 'Test1234',
            'confirmPassword': 'Test1234',
            'name': 'Test User',
            'title': 'Test',
            'role': 'CONTESTANT',
            'institutionId': 57548
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            token = result['data']['token']
            print('✅ 获取token成功')
            
            # 尝试发送错误格式的数据，看后端返回什么错误信息
            print('\n[步骤7] 测试错误的数据格式（查看验证错误信息）')
            print('-'*80)
            
            test_data = {
                "plan": "测试计划",
                "problemAnalysis": "测试问题",  # 错误的字段名
                "implementation": "测试实施",   # 错误的字段名
                "result": "测试结果",           # 错误的字段名
                "review": "测试总结"            # 错误的字段名
            }
            
            # 创建一个报名先
            reg_response = requests.post(
                f'{BASE_URL}/api/registrations',
                json={
                    'competitionId': 1,
                    'projectName': 'Test Project',
                    'groupType': 'RESIDENT'
                },
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            
            if reg_response.status_code == 200:
                reg_result = reg_response.json()
                if reg_result.get('success'):
                    registration_id = reg_result['data']['id']
                    print(f'✅ 创建报名成功，ID: {registration_id}')
                    
                    # 尝试保存项目总结（错误格式）
                    print('\n发送错误格式的数据:')
                    print(json.dumps(test_data, indent=2, ensure_ascii=False))
                    
                    summary_response = requests.put(
                        f'{BASE_URL}/api/registrations/{registration_id}/summary',
                        json=test_data,
                        headers={'Authorization': f'Bearer {token}'},
                        timeout=10
                    )
                    
                    print(f'\n响应状态码: {summary_response.status_code}')
                    
                    try:
                        result_data = summary_response.json()
                        print('\n响应内容:')
                        print(json.dumps(result_data, indent=2, ensure_ascii=False))
                        
                        if not result_data.get('success'):
                            print('\n❌ 后端返回的错误信息:')
                            print(f'   {result_data.get("message")}')
                    except:
                        print(f'响应文本: {summary_response.text}')
                        
except Exception as e:
    print(f'❌ 测试异常: {e}')

print('\n' + '='*80)
print('探测完成')
print('='*80)
