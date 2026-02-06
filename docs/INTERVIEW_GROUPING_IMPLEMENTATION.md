# 🎯 面谈阶段分组功能实现

## 功能概述

面谈阶段**仅针对进阶组**报名项目进行分组管理，支持手动分组、批量分组和自动分组。

## 核心逻辑

### 📋 面谈分组规则
- ✅ **仅进阶组参与**：只有 `groupType=ADVANCED` 的报名项目进入面谈池
- ✅ **分组代码**：使用 I1、I2、I3... I10 等面谈专用组码
- ✅ **两种视图**：面谈池（待分组）+ 分组视图（已分组）

## API 接口

### 1. 获取面谈池（进阶组报名列表）
```http
GET /api/admin/registrations/filter?competitionId=21&groupType=ADVANCED
```
**作用**：获取所有进阶组的报名项目，作为面谈分组的候选池

### 2. 获取分组视图
```http
GET /api/admin/registrations/interview-groups?competitionId=21
```
**作用**：获取已按 groupCode 分组的报名列表  
**前端处理**：过滤只显示 `groupType=ADVANCED` 的项目

### 3. 批量分组
```http
POST /api/admin/registrations/batch-classify
Content-Type: application/json

{
  "registrationIds": [101, 102, 103],
  "groupCode": "I1"
}
```
**作用**：将指定的报名项目批量分配到某个面谈组

### 4. 自动分配评委（后续使用）
```http
POST /api/admin/reviews/auto-assign
Content-Type: application/json

{
  "competitionId": 21,
  "stage": "INTERVIEW"
}
```
**作用**：自动为面谈阶段分配评委（仅对进阶组生效）

## 页面功能

### 📊 视图模式切换

#### 1. **面谈池视图**（默认）
- 显示所有进阶组报名项目
- 支持筛选：医疗机构、分组状态、项目名称
- 支持多选、单个分组、批量分组、自动分组

#### 2. **分组视图**
- 以卡片形式展示各个面谈组（I1、I2、I3...）
- 每个卡片显示该组的所有项目
- 仅显示进阶组的分组数据

### 🔧 操作功能

#### 1. **查询筛选**
```vue
<el-form-item label="医疗机构">
  <el-input v-model="filters.institutionName" />
</el-form-item>
<el-form-item label="分组状态">
  <el-select v-model="filters.groupCode">
    <el-option label="未分组" value="" />
    <el-option label="I1" value="I1" />
    ...
  </el-select>
</el-form-item>
```

#### 2. **单个分组**
- 点击某个项目的"分组"按钮
- 弹出对话框，选择目标面谈组（I1-I10）
- 调用 `batch-classify` API 完成分组

#### 3. **批量分组**
- 勾选多个项目（多选框）
- 点击"批量分组"按钮
- 弹出对话框，选择目标面谈组
- 批量调用 `batch-classify` API

#### 4. **自动分组** ⭐
```javascript
const autoGroupInterview = async () => {
  // 1. 提示输入每组人数（默认6人）
  const groupSize = parseInt(value)
  
  // 2. 筛选未分组的进阶组项目
  const ungroupedItems = poolData.value.filter(item => !item.groupCode)
  
  // 3. 前端计算分桶
  const totalGroups = Math.ceil(ungroupedItems.length / groupSize)
  
  // 4. 循环调用 batch-classify
  for (let i = 0; i < totalGroups; i++) {
    const batch = ungroupedItems.slice(i * groupSize, (i + 1) * groupSize)
    await batchClassifyRegistrations({
      registrationIds: batch.map(item => item.id),
      groupCode: `I${i + 1}`
    })
  }
}
```

**为什么前端计算分桶？**
- 后端 `auto-group` 接口当前不支持按 `groupType` 过滤
- 前端先获取进阶组数据，再按 `groupSize` 分桶，确保只对进阶组分组

## 数据流程

```
1. 页面加载
   ↓
2. 调用 filter API (groupType=ADVANCED)
   ↓
3. 获取所有进阶组报名项目
   ↓
4. 显示面谈池列表
   ↓
5. 用户操作：
   ├─ 单个分组 → batch-classify (1个项目)
   ├─ 批量分组 → batch-classify (多个项目)
   └─ 自动分组 → 前端分桶 → 多次 batch-classify
   ↓
6. 切换到"分组视图"
   ↓
7. 调用 interview-groups API
   ↓
8. 前端过滤 groupType=ADVANCED
   ↓
9. 按组码展示卡片
```

## 界面布局

### 面谈池视图
```
┌─────────────────────────────────────────────────────┐
│ [面谈池(待分组)]  [分组视图(已分组)]              │
├─────────────────────────────────────────────────────┤
│ 医疗机构：[____] 分组状态：[全部▼] 项目名称：[____]│
│ [查询] [重置] [自动分组] [批量分组]                 │
├─────────────────────────────────────────────────────┤
│ ☑  编号  项目名称     机构名称    面谈分组  操作    │
│ ☑  101   质量改进A    xx医院      I1      [详情][分组]│
│ ☑  102   流程优化B    yy医院      未分组  [详情][分组]│
│ ☑  103   标杆学习C    zz医院      I2      [详情][分组]│
└─────────────────────────────────────────────────────┘
```

### 分组视图
```
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ I1 组 (6个)    │ │ I2 组 (6个)    │ │ I3 组 (5个)    │
├────────────────┤ ├────────────────┤ ├────────────────┤
│ 质量改进A      │ │ 流程优化D      │ │ 标杆学习G      │
│ xx医院         │ │ yy医院         │ │ zz医院         │
├────────────────┤ ├────────────────┤ ├────────────────┤
│ PDCA实践B      │ │ 六西格玛E      │ │ 循证医学H      │
│ aa医院         │ │ bb医院         │ │ cc医院         │
└────────────────┘ └────────────────┘ └────────────────┘
```

## 关键代码

### 固定筛选进阶组
```javascript
const filters = reactive({
  competitionId: getCurrentCompetitionId(),
  groupType: 'ADVANCED', // ← 固定为进阶组
  institutionName: '',
  groupCode: null,
  projectName: ''
})
```

### 面谈分组代码生成
```javascript
const interviewGroupCodes = computed(() => {
  return Array.from({ length: 10 }, (_, i) => `I${i + 1}`)
  // 生成：['I1', 'I2', 'I3', ..., 'I10']
})
```

### 分组视图过滤
```javascript
const loadGroupedData = async () => {
  const res = await getInterviewGroups({ competitionId })
  
  // 只显示进阶组的分组
  const allGroups = res.data || {}
  const advancedGroups = {}
  
  Object.keys(allGroups).forEach(groupCode => {
    const items = allGroups[groupCode].filter(
      item => item.groupType === 'ADVANCED' // ← 过滤进阶组
    )
    if (items.length > 0) {
      advancedGroups[groupCode] = items
    }
  })
  
  groupedData.value = advancedGroups
}
```

## 数据字段

### 面谈池列表项
```javascript
{
  id: 101,
  registrationId: "REG001",
  projectName: "质量改进项目A",
  institutionName: "杭州市第一人民医院",
  groupType: "ADVANCED",      // 固定为进阶组
  groupCode: "I1",            // 面谈分组代码（I1-I10）
  methodLabel: "PDCA",
  applicantName: "张三"
}
```

### 分组视图数据结构
```javascript
{
  "I1": [
    { projectName: "质量改进A", institutionName: "xx医院", groupType: "ADVANCED" },
    { projectName: "PDCA实践B", institutionName: "yy医院", groupType: "ADVANCED" }
  ],
  "I2": [
    { projectName: "流程优化C", institutionName: "zz医院", groupType: "ADVANCED" }
  ]
}
```

## 测试步骤

### 1. 进入面谈分组页面
```
登录 → 面谈阶段 → 面谈分组
```

### 2. 测试面谈池视图
- ✅ 查看进阶组报名列表
- ✅ 筛选未分组项目
- ✅ 单个项目分组到 I1
- ✅ 多选项目批量分组到 I2
- ✅ 自动分组（每组6人）

### 3. 测试分组视图
- ✅ 切换到"分组视图"
- ✅ 查看各组卡片（I1、I2、I3...）
- ✅ 验证每组只显示进阶组项目
- ✅ 刷新按钮更新数据

### 4. 验证点
- ✅ 只显示进阶组（groupType=ADVANCED）
- ✅ 分组代码为 I1-I10
- ✅ 未分组显示"未分组"标签
- ✅ 已分组显示组码标签（橙色）
- ✅ 自动分组按每组人数均匀分配

## 与书审阶段的区别

| 对比项 | 书审阶段 | 面谈阶段 |
|--------|---------|---------|
| 参与组别 | 基层组、综合组、进阶组 | **仅进阶组** |
| 分组代码 | A1-A10, B1-B10, C1-C10 | **I1-I10** |
| 获取接口 | filter (不限groupType) | **filter (groupType=ADVANCED)** |
| 分组视图 | 无（直接在列表展示） | **interview-groups API** |
| 自动分组 | 后端 auto-group | **前端分桶 + 批量调用** |

## 后续扩展

### 1. 评委分配
在面谈分组完成后，可以调用：
```javascript
await autoAssignReviewers({
  competitionId: 21,
  stage: 'INTERVIEW'
})
```
后端会自动为进阶组的面谈项目分配评委。

### 2. 评委规避规则
- 同一机构规避
- 背景搭配（管理、医疗、护理）
- 评审负荷均衡

### 3. 面谈得分
评委分配后，评委可进入"面谈得分"页面进行打分。

## ✅ 完成状态

- ✅ 添加 `getInterviewGroups` 和 `autoAssignReviewers` API
- ✅ 实现面谈池视图（仅进阶组）
- ✅ 实现分组视图（卡片展示）
- ✅ 支持单个分组
- ✅ 支持批量分组
- ✅ 支持自动分组（前端分桶）
- ✅ 支持查看详情
- ✅ 筛选功能（机构、分组状态、项目名）
- ✅ 视图切换（面谈池 ↔ 分组视图）
- ✅ 无 linter 错误

面谈分组功能已完整实现，可进行测试！🎉
