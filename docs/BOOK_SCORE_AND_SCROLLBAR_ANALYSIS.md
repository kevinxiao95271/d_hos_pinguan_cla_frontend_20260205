# 书审得分页面和分组页面问题分析

## 测试时间
2026-03-01

## 问题概述

从控制台日志发现两个问题：

### 问题1: 书审得分API 404错误
```
GET /api/admin/reviews/book-scores?competitionId=1 → 404 Not Found
```

### 问题2: 面谈分组页面滚动条初始化失败
```
Group.vue:777 ❌ 找不到 ref 元素
```

---

## 问题1: 书审得分API不存在

### 当前状态

**前端调用:**
- 文件: `src/views/committee/book/Score.vue:239`
- API函数: `getBookScores(params)` from `@/api/review.js`
- 端点: `GET /admin/reviews/book-scores`
- 参数: `{ competitionId, groupType?, reviewerName?, institutionName? }`

**后端状态:**
- ❌ `GET /admin/reviews/book-scores` - 404 不存在
- ❌ `GET /admin/reviews/scores` - 404 不存在

### 可用的替代API

测试发现以下API可用：

#### 1. GET /admin/reviews/summary
```json
参数: { competitionId: 1, stage: "BOOK" }
状态: 200 OK
返回: { success: true, data: [], message: null }
```

**特点:**
- 返回评审汇总数据（数组格式）
- 支持按阶段筛选
- 当前返回空数组（可能是因为没有评分数据）

#### 2. GET /admin/reviews/tasks
```json
参数: { competitionId: 1, stage: "BOOK" }
状态: 200 OK
返回: { success: true, data: [], message: null }
```

**特点:**
- 返回评审任务列表
- 包含任务分配信息
- 当前返回空数组

### 前端期望的数据结构

根据 `Score.vue` 代码分析，前端期望返回：

```javascript
{
  success: true,
  data: [
    {
      scoreId: number,           // 评分ID（用于驳回）
      projectName: string,       // 项目名称
      institutionName: string,   // 医疗机构
      institutionLevel: string,  // 机构等级
      groupType: string,         // 组别 (BASIC/COMPREHENSIVE/ADVANCED)
      groupCode: string,         // 分组代码
      reviewerName: string,      // 评委姓名
      reviewerInstitutionName: string, // 评委机构
      
      // 分项评分
      plan: number,              // 计划
      problem: number,           // 问题
      action: number,            // 行动
      success: number,           // 成效
      review: number,            // 回顾
      operation: number,         // 运作
      presentation: number,      // 展示
      
      total: number,             // 总分
      submittedAt: string        // 提交时间
    }
  ]
}
```

### 解决方案建议

#### 方案A: 使用 /admin/reviews/summary（推荐）

如果 `/admin/reviews/summary` 返回的数据结构包含所需字段，可以直接使用：

```javascript
// src/api/review.js
export function getBookScores(params) {
  return request({
    url: '/admin/reviews/summary',
    method: 'get',
    params: {
      ...params,
      stage: 'BOOK'  // 固定为书审阶段
    }
  })
}
```

#### 方案B: 等待后端实现

如果现有API不满足需求，需要后端实现 `GET /admin/reviews/book-scores` 端点。

**后端需要实现的功能:**
1. 查询指定赛事的所有书审评分记录
2. 支持按组别、评委姓名、机构名称筛选
3. 返回完整的评分详情（包含7个分项评分）
4. 包含项目信息、评委信息、机构信息

---

## 问题2: 滚动条初始化时机问题

### 问题描述

**文件:** `src/views/committee/interview/Group.vue:777`

**错误信息:**
```
updateTopScrollbarWidth 被调用
❌ 找不到 ref 元素: { topScrollbar: null, tableContainer: null }
```

### 代码分析

```javascript
// Group.vue:764-783
const updateTopScrollbarWidth = () => {
  console.log('updateTopScrollbarWidth 被调用')
  if (topScrollbar.value && tableContainer.value) {
    const tableBody = tableContainer.value.querySelector('.el-table__body-wrapper')
    console.log('找到的元素:', tableBody)
    if (tableBody) {
      const scrollContent = topScrollbar.value.querySelector('.top-scrollbar-content')
      if (scrollContent) {
        const tableWidth = tableBody.scrollWidth
        scrollContent.style.width = `${tableWidth}px`
        console.log('✅ 更新顶部滚动条宽度:', tableWidth, 'px')
      }
    }
  } else {
    console.log('❌ 找不到 ref 元素:', { 
      topScrollbar: topScrollbar.value, 
      tableContainer: tableContainer.value 
    })
  }
}

onMounted(async () => {
  // ... 其他初始化代码
  
  // 初始化顶部滚动条 - 延迟确保表格渲染完成
  setTimeout(() => {
    updateTopScrollbarWidth()
    // ...
  }, 0)
})
```

### 问题原因

1. **时机问题:** `setTimeout(..., 0)` 延迟不够，DOM元素可能还未渲染完成
2. **异步加载:** `onMounted` 中有异步操作（`getCurrentCompetitionId`, `loadDictionaries`, `loadPoolData`），表格数据可能还在加载中
3. **条件渲染:** 如果表格使用了 `v-if` 或 `v-loading`，在数据加载完成前元素不存在

### 影响评估

- ⚠️ 不影响页面功能，只是顶部滚动条宽度未正确初始化
- 用户可以正常使用表格的原生滚动条
- 这是一个UI优化功能的小问题

### 解决方案

#### 方案A: 增加延迟时间（临时方案）

```javascript
onMounted(async () => {
  // ... 其他初始化代码
  
  // 等待数据加载完成后再初始化滚动条
  setTimeout(() => {
    updateTopScrollbarWidth()
  }, 500)  // 增加到500ms
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

#### 方案C: 使用 nextTick + watch（最佳）

```javascript
import { nextTick, watch } from 'vue'

// 监听数据变化
watch(() => poolData.value, () => {
  nextTick(() => {
    updateTopScrollbarWidth()
  })
}, { deep: true })

// 监听loading状态
watch(loading, (newVal) => {
  if (!newVal) {  // loading完成
    nextTick(() => {
      updateTopScrollbarWidth()
    })
  }
})
```

---

## 优先级建议

### 高优先级
- ✅ **问题1 - 书审得分API:** 影响功能使用，需要尽快解决
  - 先确认 `/admin/reviews/summary` 是否返回所需数据
  - 如果不满足，需要后端实现新API

### 低优先级
- ⚠️ **问题2 - 滚动条初始化:** 不影响核心功能，可以后续优化
  - 建议使用方案B或方案C
  - 可以在其他功能完成后再处理

---

## 下一步行动

1. **确认数据结构:** 测试 `/admin/reviews/summary` 返回的实际数据结构（需要有评分数据时）
2. **决定方案:** 根据数据结构决定使用方案A还是方案B
3. **修改前端:** 如果使用方案A，修改 `getBookScores` 函数
4. **测试验证:** 确保筛选功能和驳回功能正常工作
5. **优化滚动条:** 在主要功能完成后，修复滚动条初始化问题

---

## 测试脚本

已创建测试脚本: `scripts/test_book_scores_api.py`

**运行命令:**
```bash
python scripts/test_book_scores_api.py
```

**测试结果:**
- ❌ `/admin/reviews/book-scores` - 404
- ❌ `/admin/reviews/scores` - 404
- ✅ `/admin/reviews/summary` - 200 (返回空数组)
- ✅ `/admin/reviews/tasks` - 200 (返回空数组)
