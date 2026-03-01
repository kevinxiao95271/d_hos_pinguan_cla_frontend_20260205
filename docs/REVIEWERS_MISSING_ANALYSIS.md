# 评审专家缺失问题分析

## 测试时间
2026-03-01

## 问题描述

用户提供了105位评审专家名单，但在任务分配界面拉取评委列表时，发现有8位评委缺失。

## 测试结果

### API调用情况

**使用的API:** `GET /api/admin/reviewers`

**前端调用位置:** `src/views/committee/interview/Reviewer.vue:290`

```javascript
import { getReviewers } from '@/api/admin'

// 加载评委列表
const loadReviewers = async () => {
  const res = await getReviewers({
    competitionId: competitionId.value,
    ...revGetPaginationParams()
  })
}
```

### API返回数据

| 项目 | 数值 |
|------|------|
| API状态 | 200 OK ✅ |
| 返回格式 | 数组格式 |
| 返回评委总数 | 127 位 |
| 有姓名的评委数 | 122 位 |
| 期望评委数 | 105 位 |

### 缺失的评委 (8位)

1. 冯玉权
2. 刘彩霞
3. 张雪霞
4. 朱军梅
5. 秦刚
6. 胡斌春
7. 陈俊航
8. 黄丽华

### 额外的评委 (26位)

系统中还有26位不在用户提供名单中的评委：

何研究员、冯博士、冯院长、刘主任、刘研究员、吴专家、周院长、孙主任、孙丽娟、张研究员、徐教授、曹研究员、朱研究员、李院长、杨专家、梁主任、梁教授、胡主任、许专家、许主任、许研究员、郑教授、郭博士、陈博士、陈教授、高专家

## 数据结构分析

### 评委对象字段

```json
{
  "id": 5,
  "phone": "13800002569",
  "name": "孙丽娟",
  "title": "Test Title",
  "institutionId": 36232,
  "institutionName": "绍兴市第七人民医院",
  "reviewerGroupCode": "A1",
  "interviewGroupCode": "A1",
  "expertBackground": "MEDICAL"
}
```

### 字段说明

- `id` - 评委ID
- `phone` - 手机号
- `name` - 姓名
- `title` - 职称
- `institutionId` - 机构ID
- `institutionName` - 机构名称
- `reviewerGroupCode` - 书审分组代码
- `interviewGroupCode` - 面谈分组代码
- `expertBackground` - 专家背景

## 问题原因分析

### 可能的原因

1. **数据未录入**
   - 这8位评委可能还没有在系统中创建
   - 需要在"系统管理 → 评审专家管理"中添加

2. **数据录入错误**
   - 姓名可能录入错误（如多空格、错别字）
   - 需要检查数据库中的实际姓名

3. **关联关系缺失**
   - 评委已创建但未关联到当前赛事
   - 需要检查评委的competitionId关联

4. **数据被删除**
   - 评委曾经存在但被删除了
   - 需要检查操作日志

## 验证方法

### 方法1: 在前端界面检查

1. 登录组委会账号
2. 进入"系统管理 → 评审专家管理"
3. 搜索缺失的评委姓名
4. 查看是否存在

### 方法2: 使用测试脚本

```bash
python scripts/check_reviewers_list.py
```

该脚本会：
- 调用评委列表API
- 对比期望名单和实际返回
- 列出缺失和额外的评委

### 方法3: 检查数据库

直接查询数据库中的reviewer表：

```sql
-- 查找缺失的评委
SELECT * FROM reviewer 
WHERE name IN ('冯玉权', '刘彩霞', '张雪霞', '朱军梅', '秦刚', '胡斌春', '陈俊航', '黄丽华');

-- 查看所有评委
SELECT id, name, phone, institution_name 
FROM reviewer 
ORDER BY name;
```

## 解决方案

### 方案A: 添加缺失的评委

如果评委确实不存在，需要在系统中添加：

1. 登录组委会账号
2. 进入"系统管理 → 评审专家管理"
3. 点击"新增评委"
4. 填写评委信息：
   - 姓名
   - 手机号
   - 职称
   - 所属机构
   - 专家背景
5. 保存

### 方案B: 修正姓名错误

如果评委存在但姓名有误：

1. 在评审专家管理页面搜索相似姓名
2. 找到对应评委
3. 点击"编辑"
4. 修正姓名
5. 保存

### 方案C: 批量导入

如果需要添加多个评委，可以使用批量导入功能（如果有）：

1. 准备Excel文件，包含评委信息
2. 使用导入功能批量添加
3. 验证导入结果

## 前端API使用情况

### 评委列表API

**文件:** `src/api/admin.js`

```javascript
/**
 * 获取评委列表
 */
export function getReviewers(params) {
  return request({
    url: '/admin/reviewers',
    method: 'get',
    params
  })
}
```

### 调用位置

1. **面谈评委分配页面**
   - 文件: `src/views/committee/interview/Reviewer.vue`
   - 用途: 显示可分配的评委列表

2. **书审评委分配页面**
   - 文件: `src/views/committee/book/Reviewer.vue`
   - 用途: 显示可分配的评委列表

3. **决赛评委分配页面**
   - 文件: `src/views/committee/final/Reviewer.vue`
   - 用途: 显示可分配的评委列表

4. **评审专家管理页面**
   - 文件: `src/views/ops/Reviewers.vue`
   - 用途: 管理评委信息

### API特点

- ✅ 支持按competitionId筛选
- ✅ 支持分页参数（page, size）
- ✅ 返回完整的评委信息
- ✅ 包含机构信息和分组信息
- ⚠️ 不支持按姓名模糊搜索（前端参数）

## 数据统计

### 当前系统状态

- 系统中评委总数: 127 位
- 有姓名的评委: 122 位
- 无姓名的评委: 5 位（可能是测试数据）

### 与期望名单对比

- 期望评委数: 105 位
- 匹配的评委: 97 位 (92.4%)
- 缺失的评委: 8 位 (7.6%)
- 额外的评委: 26 位

### 结论

系统中大部分评委数据是正确的，只有8位评委缺失。这些评委可能：
1. 还未录入系统
2. 姓名录入有误
3. 被误删除

## 建议行动

### 立即行动

1. **核对缺失评委**
   - 在评审专家管理页面搜索这8位评委
   - 确认是否存在但姓名有误

2. **添加缺失评委**
   - 如果确实不存在，立即添加
   - 确保信息准确（姓名、手机号、机构）

3. **验证结果**
   - 添加后重新运行测试脚本
   - 确认所有评委都能正常显示

### 后续优化

1. **添加姓名搜索功能**
   - 在评委列表API中支持姓名模糊搜索
   - 方便快速查找特定评委

2. **数据导入导出**
   - 支持批量导入评委信息
   - 支持导出评委名单进行核对

3. **数据验证**
   - 添加评委姓名唯一性检查
   - 防止重复录入

## 相关文件

### 测试脚本
- `scripts/check_reviewers_list.py` - 评委列表检查脚本

### 前端文件
- `src/api/admin.js` - 评委API定义
- `src/views/committee/interview/Reviewer.vue` - 面谈评委分配页面
- `src/views/ops/Reviewers.vue` - 评审专家管理页面

### 文档
- `docs/REVIEWERS_MISSING_ANALYSIS.md` - 本文档

## 缺失评委名单

为方便添加，这里列出缺失的8位评委：

1. 冯玉权
2. 刘彩霞
3. 张雪霞
4. 朱军梅
5. 秦刚
6. 胡斌春
7. 陈俊航
8. 黄丽华

**建议:** 将这些评委信息补充到系统中，确保任务分配时能够正常显示。
