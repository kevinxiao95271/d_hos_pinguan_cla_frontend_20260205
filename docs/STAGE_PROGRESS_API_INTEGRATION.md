# 🎯 跑马灯阶段时间从API获取

## 问题描述

用户反馈：跑马灯没有显示各个阶段的起始时间，这些时间应该从后端API获取，而不是前端硬编码。每个赛事的阶段时间是必备信息。

## 解决方案

### 1. ✅ 后端API接口

**接口**: `GET /api/competitions/{id}`

**返回字段映射**:
```javascript
{
  registerStart,      // 报名开始时间
  registerEnd,        // 报名结束时间
  bookReviewStart,    // 书审开始时间
  bookReviewEnd,      // 书审结束时间
  interviewStart,     // 面谈开始时间
  interviewEnd,       // 面谈结束时间
  finalStart,         // 决赛开始时间
  finalEnd            // 决赛结束时间
}
```

### 2. ✅ 创建可复用 Composable

创建 `src/composables/useCompetitionStages.js`，统一管理赛事阶段信息：

```javascript
export function useCompetitionStages() {
  const competition = ref({})

  const stagesList = computed(() => {
    const comp = competition.value
    return [
      { 
        key: 'REGISTRATION', 
        title: '报名', 
        startDate: comp.registerStart || null, 
        endDate: comp.registerEnd || null
      },
      { 
        key: 'BOOK', 
        title: '书审', 
        startDate: comp.bookReviewStart || null, 
        endDate: comp.bookReviewEnd || null
      },
      { 
        key: 'INTERVIEW', 
        title: '面谈', 
        startDate: comp.interviewStart || null, 
        endDate: comp.interviewEnd || null
      },
      { 
        key: 'FINAL', 
        title: '决赛', 
        startDate: comp.finalStart || null, 
        endDate: comp.finalEnd || null
      }
    ]
  })

  const loadCompetition = async () => {
    const competitionId = localStorage.getItem('currentCompetitionId') || 21
    const res = await getCompetition(competitionId)
    if (res.success && res.data) {
      competition.value = res.data
    }
  }

  onMounted(() => {
    loadCompetition()
  })

  return { competition, stagesList, loadCompetition }
}
```

### 3. ✅ 更新 StageProgress 组件

修改时间格式化函数，处理时间为空的情况：

```javascript
const formatDateRange = (start, end) => {
  if (!start || !end) return '未设置'  // ← 时间为空显示"未设置"
  
  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }
  
  return `${formatDate(start)} - ${formatDate(end)}`
}
```

### 4. ✅ 更新所有子页面

所有使用跑马灯的页面都改为使用 `useCompetitionStages`：

**书审阶段** (4个页面):
- `src/views/committee/book/Registration.vue`
- `src/views/committee/book/Reviewer.vue`
- `src/views/committee/book/Score.vue`
- `src/views/committee/book/Feedback.vue`

**面谈阶段** (4个页面):
- `src/views/committee/interview/Group.vue`
- `src/views/committee/interview/Reviewer.vue`
- `src/views/committee/interview/Score.vue`
- `src/views/committee/interview/Shortlist.vue`

**决赛阶段** (4个页面):
- `src/views/committee/final/Group.vue`
- `src/views/committee/final/Reviewer.vue`
- `src/views/committee/final/Score.vue`
- `src/views/committee/final/Ranking.vue`

**使用方式**:
```vue
<script setup>
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'

const { stagesList } = useCompetitionStages()
</script>

<template>
  <stage-progress current-stage="BOOK" :stages="stagesList" />
</template>
```

## 字段映射关系

| 阶段 | 后端字段（开始） | 后端字段（结束） | 跑马灯 key |
|------|----------------|----------------|-----------|
| 报名 | `registerStart` | `registerEnd` | REGISTRATION |
| 书审 | `bookReviewStart` | `bookReviewEnd` | BOOK |
| 面谈 | `interviewStart` | `interviewEnd` | INTERVIEW |
| 决赛 | `finalStart` | `finalEnd` | FINAL |

## 展示规则

### 有时间数据
```
┌─────────────────────────────────────────────┐
│ [报名] ──→ [书审] ──→ [面谈] ──→ [决赛]     │
│ 1/1-1/31  2/1-2/28  3/1-3/31  4/1-4/30     │
└─────────────────────────────────────────────┘
```

### 时间未设置
```
┌─────────────────────────────────────────────┐
│ [报名] ──→ [书审] ──→ [面谈] ──→ [决赛]     │
│  未设置    未设置    未设置    未设置        │
└─────────────────────────────────────────────┘
```

## 数据流程

```
1. 页面加载
   ↓
2. useCompetitionStages() 自动调用
   ↓
3. 从 localStorage 获取 currentCompetitionId (默认21)
   ↓
4. 调用 GET /api/competitions/{id}
   ↓
5. 解析返回数据，提取阶段时间
   ↓
6. computed stagesList 自动更新
   ↓
7. StageProgress 组件接收新数据
   ↓
8. 格式化时间并显示（M/D - M/D 或 "未设置"）
```

## 优势

### ✅ 代码复用
- 12个页面共用一个 composable
- 避免重复的 API 调用逻辑
- 统一的数据格式和错误处理

### ✅ 数据准确
- 直接从后端获取真实的赛事时间
- 不再依赖前端硬编码
- 切换赛事时自动更新时间

### ✅ 易于维护
- 修改时间格式只需改一处
- 添加新字段只需更新 composable
- 清晰的职责分离

### ✅ 用户体验
- 显示真实的赛事阶段时间
- 时间未设置时友好提示"未设置"
- 自动适配不同赛事的时间安排

## 测试步骤

1. **确保后端返回时间数据**
   ```bash
   # 测试赛事详情API
   GET http://localhost:6031/api/competitions/21
   Authorization: Bearer {token}
   ```

2. **前端测试**
   - 刷新浏览器
   - 登录组委会账号
   - 进入任意书审/面谈/决赛子页面
   - 查看跑马灯是否显示时间

3. **验证点**
   - ✅ 跑马灯显示格式：`M/D - M/D`（如 `2/1 - 2/28`）
   - ✅ 时间为空时显示：`未设置`
   - ✅ 切换不同页面，时间保持一致
   - ✅ 控制台输出：`✅ 加载赛事信息: {赛事名称}`

## 后续优化建议

### 1. 缓存优化
当前每个页面都会调用一次 API，可以考虑：
- 使用 Pinia store 缓存赛事信息
- 只在首次加载或切换赛事时调用 API

### 2. 时间格式
如果需要更详细的时间显示（如包含时分秒），可以修改 `formatDateRange` 函数：
```javascript
return `${dayjs(start).format('MM-DD HH:mm')} ~ ${dayjs(end).format('MM-DD HH:mm')}`
```

### 3. 当前阶段高亮
可以根据当前时间自动判断并高亮当前阶段：
```javascript
const currentStage = computed(() => {
  const now = new Date()
  if (now >= new Date(comp.registerStart) && now <= new Date(comp.registerEnd)) {
    return 'REGISTRATION'
  }
  // ... 其他阶段判断
})
```

## ✅ 完成状态

- ✅ 创建 `useCompetitionStages` composable
- ✅ 更新 `StageProgress` 组件处理空时间
- ✅ 更新所有 12 个子页面使用 composable
- ✅ 字段映射正确（registerStart/End, bookReviewStart/End 等）
- ✅ 时间格式化（M/D - M/D）
- ✅ 空值处理（显示"未设置"）
- ✅ 无 linter 错误

跑马灯现在会从后端API获取真实的赛事阶段时间！🎉
