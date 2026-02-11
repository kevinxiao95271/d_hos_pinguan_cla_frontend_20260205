# 赛事API字段映射表

## API端点
```
GET /api/competitions/{id}
```

## 字段对照表

| 前端期望字段名 | 后端实际字段名 | 字段说明 | 状态 |
|---|---|---|---|
| `currentStage` | `stage` | 当前阶段 | ✅ 已适配 |
| `registrationStartTime` | `registerStart` | 报名开始时间 | ✅ 已适配 |
| `registrationEndTime` | `registerEnd` | 报名结束时间 | ✅ 已适配 |
| `bookStartTime` | `bookReviewStart` | 书审开始时间 | ✅ 已适配 |
| `bookEndTime` | `bookReviewEnd` | 书审结束时间 | ✅ 已适配 |
| `interviewStartTime` | `interviewStart` | 面谈开始时间 | ✅ 已适配 |
| `interviewEndTime` | `interviewEnd` | 面谈结束时间 | ✅ 已适配 |
| `finalStartTime` | `finalStart` | 决赛开始时间 | ✅ 已适配 |
| `finalEndTime` | `finalEnd` | 决赛结束时间 | ✅ 已适配 |

## 后端实际返回结构

```json
{
  "id": 21,
  "name": "2026浙江品管大赛",
  "stage": "REGISTER",                  
  "registerStart": "2026-02-01T23:48:02.070734",
  "registerEnd": "2026-02-26T23:48:02.070734",
  "bookReviewStart": "2026-02-21T00:00:00",
  "bookReviewEnd": "2026-02-28T23:59:59",
  "interviewStart": "2026-03-01T00:00:00",
  "interviewEnd": "2026-03-05T23:59:59",
  "finalStart": "2026-03-10T00:00:00",
  "finalEnd": "2026-03-12T23:59:59",
  "createdAt": "2026-02-05T10:05:06.699"
}
```

## 前端适配方案

### 已修改的文件
- `src/views/contestant/MyCompetition.vue`

### 修改内容

```javascript
// 修改前（期望字段名）
const stagesList = computed(() => {
  return [
    {
      key: 'REGISTRATION',
      title: '报名',
      description: formatDateRange(
        competition.value.registrationStartTime,  // ❌ 字段不存在
        competition.value.registrationEndTime      // ❌ 字段不存在
      )
    },
    // ...
  ]
})

// 修改后（实际字段名）
const stagesList = computed(() => {
  return [
    {
      key: 'REGISTRATION',
      title: '报名',
      description: formatDateRange(
        competition.value.registerStart,   // ✅ 使用后端实际字段
        competition.value.registerEnd      // ✅ 使用后端实际字段
      )
    },
    // ...
  ]
})

// currentStage 改为 stage
<stage-progress
  :current-stage="competition.stage"  // ✅ 改为 stage
  :stages="stagesList"
/>
```

## 阶段代码映射

| 阶段 | 后端代码 | 前端显示 |
|---|---|---|
| 报名阶段 | `REGISTER` | 报名 |
| 书审阶段 | `BOOK_REVIEW` | 书审 |
| 面谈阶段 | `INTERVIEW` | 面谈 |
| 决赛阶段 | `FINAL` | 决赛 |

## 其他可能受影响的页面

需要检查以下页面是否使用了旧的字段名：

- [ ] `src/views/committee/Statistics.vue` - 报名统计
- [ ] `src/views/committee/CreateCompetition.vue` - 创建赛事
- [ ] `src/views/committee/SwitchCompetition.vue` - 切换赛事
- [ ] `src/components/StageProgress.vue` - 阶段进度组件

## 测试脚本

已提供测试脚本：`scripts/test_competition_api.py`

运行命令：
```bash
python scripts/test_competition_api.py
```

## 建议

### 选项1：前端适配（已实施）✅
- 优点：快速修复，不需要等待后端
- 缺点：字段名不统一，增加维护成本

### 选项2：后端统一字段名（建议）
- 优点：字段名统一，更符合前端习惯
- 缺点：需要后端修改，影响已有API

### 建议的后端字段名
```json
{
  "currentStage": "REGISTER",
  "registrationStartTime": "2026-02-01T23:48:02.070734",
  "registrationEndTime": "2026-02-26T23:48:02.070734",
  "bookStartTime": "2026-02-21T00:00:00",
  "bookEndTime": "2026-02-28T23:59:59",
  "interviewStartTime": "2026-03-01T00:00:00",
  "interviewEndTime": "2026-03-05T23:59:59",
  "finalStartTime": "2026-03-10T00:00:00",
  "finalEndTime": "2026-03-12T23:59:59"
}
```

---

**文档版本**: 1.0  
**更新时间**: 2026-02-11  
**状态**: ✅ 前端已适配后端字段
