# 控制台错误分析报告

## 测试时间
2026-03-01

## 错误概览

从控制台日志中发现两个问题：

1. ❌ **书审得分API 404错误** - 影响功能使用
2. ⚠️ **滚动条初始化失败** - 不影响核心功能

---

## 问题1: 书审得分API不存在 (404)

### 错误信息
```
GET /api/admin/reviews/book-scores?competitionId=1 → 404 Not Found
位置: Score.vue:247
```

### 问题分析

#### 前端调用
- **文件:** `src/views/committee/book/Score.vue`
- **API函数:** `getBookScores(params)` from `@/api/review.js`
- **端点:** `GET /admin/reviews/book-scores`
- **参数:** `{ competitionId, groupType?, reviewerName?, institutionName? }`

#### 后端状态
通过测试脚本验证：

| API端点 | 状态 | 说明 |
|---------|------|------|
| `/admin/reviews/book-scores` | ❌ 404 | 不存在 |
| `/admin/reviews/scores` | ❌ 404 | 不存在 |
| `/admin/reviews/summary` | ✅ 200 | 存在，但需要 `stage` 参数 |
| `/admin/reviews/tasks` | ✅ 200 | 存在，返回任务列表 |

#### 关键发现

1. **`/admin/reviews/summary` 必须带 `stage` 参数**
   - 不带参数: 400 Bad Request
   - 带 `stage=BOOK`: 200 OK，返回空数组

2. **当前系统中没有书审评分数据**
   - `/admin/reviews/summary?stage=BOOK` 返回空数组
   - `/admin/reviews/tasks?stage=BOOK` 返回空数组
   - 可能是因为还没有评委提交评分

### 前端期望的数据结构

根据 `Score.vue` 代码，前端期望返回：

```javascript
{
  success: true,
  data: [
    {
      scoreId: number,              // 评分ID（用于驳回）
      projectName: string,          // 项目名称
      institutionName: string,      // 医疗机构
      institutionLevel: string,     // 机构等级
      groupType: string,            // 组别 (BASIC/COMPREHENSIVE/ADVANCED)
      groupCode: string,            // 分组代码
      reviewerName: string,         // 评委姓名
      reviewerInstitutionName: string, // 评委机构
      
      // 分项评分 (7项)
      plan: number,                 // 计划
      problem: number,              // 问题
      action: number,               // 行动
      success: number,              // 成效
      review: number,               // 回顾
      operation: number,            // 运作
      presentation: number,         // 展示
      
      total: number,                // 总分
      submittedAt: string           // 提交时间
    }
  ]
}
```

### 解决方案

#### 方案A: 使用现有API `/admin/reviews/summary` (推荐)

**前提条件:** 需要确认该API返回的数据结构是否包含所需字段

**修改方案:**
```javascript
// src/api/review.js
export function getBookScores(params) {
  return request({
    url: '/admin/reviews/summary',
    method: 'get',
    params: {
      ...params,
      stage: 'BOOK'  // 固定添加stage参数
    }
  })
}
```

**优点:**
- 无需后端开发
- 立即可用

**缺点:**
- 需要确认数据结构是否完全匹配
- 如果字段不匹配，需要前端做数据转换

#### 方案B: 后端实现新API (如果方案A不可行)

**后端需要实现:**
```
GET /api/admin/reviews/book-scores
参数: competitionId, groupType?, reviewerName?, institutionName?
返回: 包含完整评分详情的数组
```

**功能要求:**
1. 查询指定赛事的所有书审评分记录
2. 支持按组别、评委姓名、机构名称筛选
3. 返回7个分项评分 + 总分
4. 包含项目信息、评委信息、机构信息
5. 支持驳回功能（需要scoreId）

### 下一步行动

1. **测试 `/admin/reviews/summary` 的实际数据结构**
   - 需要等待系统中有评分数据后测试
   - 或者询问后端该API返回的字段列表

2. **根据测试结果选择方案**
   - 如果字段匹配 → 使用方案A
   - 如果字段不匹配 → 使用方案B

3. **反馈给后端**
   - 如果选择方案B，需要提供详细的API需求文档

---

## 问题2: 滚动条初始化失败

### 错误信息
```
Group.vue:764 updateTopScrollbarWidth 被调用
Group.vue:777 ❌ 找不到 ref 元素: { topScrollbar: null, tableContainer: null }
```

### 问题分析

#### 代码位置
- **文件:** `src/views/committee/interview/Group.vue`
- **函数:** `updateTopScrollbarWidth()`
- **调用时机:** `onMounted` 中使用 `setTimeout(..., 0)` 延迟调用

#### 问题原因

1. **时机问题**
   - `setTimeout(..., 0)` 延迟不够
   - DOM元素可能还未渲染完成

2. **异步加载**
   - `onMounted` 中有异步操作（加载赛事信息、字典、数据）
   - 表格数据可能还在加载中

3. **条件渲染**
   - 如果表格使用了 `v-if` 或 `v-loading`
   - 在数据加载完成前元素不存在

#### 影响评估

- ⚠️ **不影响核心功能**
- 用户可以正常使用表格的原生滚动条
- 只是顶部自定义滚动条宽度未正确初始化
- 这是一个UI优化功能的小问题

### 解决方案

#### 方案A: 增加延迟时间（临时方案）
```javascript
onMounted(async () => {
  // ... 其他初始化代码
  
  setTimeout(() => {
    updateTopScrollbarWidth()
  }, 500)  // 从0改为500ms
})
```

#### 方案B: 在数据加载完成后调用（推荐）
```javascript
const loadPoolData = async () => {
  loading.value = true
  try {
    // ... 加载数据
  } finally {
    loading.value = false
    
    // 数据加载完成后初始化滚动条
    nextTick(() => {
      updateTopScrollbarWidth()
    })
  }
}
```

#### 方案C: 使用 watch 监听（最佳）
```javascript
import { nextTick, watch } from 'vue'

// 监听loading状态
watch(loading, (newVal) => {
  if (!newVal) {  // loading完成
    nextTick(() => {
      updateTopScrollbarWidth()
    })
  }
})
```

### 建议

- 优先级: 低
- 可以在主要功能完成后再处理
- 推荐使用方案B或方案C

---

## 优先级总结

### 🔴 高优先级 - 需要立即处理

**问题1: 书审得分API 404**
- 影响: 书审得分页面无法加载数据
- 用户: 组委会管理员
- 功能: 查看评分、驳回评分

**行动:**
1. 测试 `/admin/reviews/summary` 的数据结构
2. 决定使用方案A还是方案B
3. 修改前端代码或反馈后端

### 🟡 低优先级 - 可以后续优化

**问题2: 滚动条初始化失败**
- 影响: 自定义滚动条显示不正确
- 用户: 所有使用分组页面的用户
- 功能: UI优化，不影响核心功能

**行动:**
1. 在主要功能完成后处理
2. 使用方案B或方案C修复

---

## 测试脚本

已创建以下测试脚本：

1. **`scripts/test_book_scores_api.py`**
   - 测试书审得分API是否存在
   - 检查可能的替代API

2. **`scripts/check_book_review_data.py`**
   - 检查系统中是否有书审评分数据
   - 验证API的数据结构

**运行命令:**
```bash
python scripts/test_book_scores_api.py
python scripts/check_book_review_data.py
```

---

## 反馈给后端

### 问题描述

前端调用 `GET /api/admin/reviews/book-scores` 返回404，该API不存在。

### 需求说明

**功能:** 组委会查看书审得分列表

**页面:** 赛事管理 → 书审管理 → 得分列表

**API需求:**
```
GET /api/admin/reviews/book-scores
```

**请求参数:**
```javascript
{
  competitionId: number,      // 必填
  groupType?: string,         // 可选: BASIC/COMPREHENSIVE/ADVANCED
  reviewerName?: string,      // 可选: 评委姓名（模糊搜索）
  institutionName?: string    // 可选: 机构名称（模糊搜索）
}
```

**响应格式:**
```javascript
{
  success: true,
  data: [
    {
      scoreId: number,              // 评分ID（用于驳回）
      projectName: string,          // 项目名称
      institutionName: string,      // 医疗机构
      institutionLevel: string,     // 机构等级
      groupType: string,            // 组别
      groupCode: string,            // 分组代码
      reviewerName: string,         // 评委姓名
      reviewerInstitutionName: string, // 评委机构
      plan: number,                 // 计划得分
      problem: number,              // 问题得分
      action: number,               // 行动得分
      success: number,              // 成效得分
      review: number,               // 回顾得分
      operation: number,            // 运作得分
      presentation: number,         // 展示得分
      total: number,                // 总分
      submittedAt: string           // 提交时间
    }
  ]
}
```

### 替代方案

如果 `GET /api/admin/reviews/summary?stage=BOOK` 已经返回上述数据结构，可以告知前端直接使用该API。

---

## 总结

1. **书审得分API不存在** - 需要确认使用现有API还是开发新API
2. **滚动条初始化失败** - 低优先级，不影响核心功能
3. **已创建测试脚本** - 可用于验证API和数据结构
4. **已创建分析文档** - 供团队参考和决策
