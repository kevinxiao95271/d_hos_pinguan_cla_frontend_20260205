#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取测试结果文件
with open('group_test_result.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找关键部分
sections = [
    "步骤3: 对基层组执行自动分组",
    "步骤4: 查询基层组分组后的结果",
    "步骤5: 对进阶组执行自动分组",
    "步骤6: 查询进阶组分组后的结果",
    "问题分析"
]

for section in sections:
    if section in content:
        start = content.index(section)
        # 找到下一个分隔符
        next_sep = content.find("=" * 80, start + 1)
        if next_sep == -1:
            next_sep = len(content)
        
        # 提取内容（包含下一节的标题前）
        section_content = content[start:next_sep].strip()
        
        print("=" * 80)
        print(section_content[:2000])  # 限制每节2000字符
        print()
