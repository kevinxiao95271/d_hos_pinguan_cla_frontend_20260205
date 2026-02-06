# 评委分配冲突检测功能

## 实现状态

### ✅ 已完成
- **书审评委分配** (`src/views/committee/book/Reviewer.vue`)
  - 同机构回避检测
  - 重复分配检测（已分配过）
  - 评委列表自动禁用
  - 分配前完整检查

### ⏸️ 待完成
- **面谈评委分配** (`src/views/committee/interview/Reviewer.vue`)
- **决赛评委分配** (`src/views/committee/final/Reviewer.vue`)

## 核心功能

### 1. 同机构回避
- 检测评委与项目是否同机构
- 自动禁用同机构评委
- 分配前阻止

### 2. 重复分配检测 ⭐ 新增
- 当选择报名项目时，自动查询已分配的任务
- 标识哪些评委已经分配过这些项目
- 自动禁用已分配的评委
- 分配前阻止

## 技术实现

### API调用
```javascript
// 获取已分配的任务
const res = await getReviewTasksByStage({
  competitionId: 21,
  stage: 'BOOK' // 或 'INTERVIEW', 'FINAL'
})

// 返回数据结构
{
  success: true,
  data: [
    {
      registrationId: 106,
      reviewerId: 3,
      stage: 'BOOK',
      status: 'PENDING'
    },
    ...
  ]
}
```

### 数据结构
```javascript
// 已分配任务映射
assignedTasks = {
  106: [3, 6, 7],      // 报名ID: [评委ID数组]
  107: [3, 8],
  108: [6, 7, 9]
}
```

### 判断逻辑
```javascript
// 1. 同机构判断
isSameInstitution(reviewer) {
  return selectedRegistrations.some(
    reg => reg.institutionId === reviewer.institutionId
  )
}

// 2. 已分配判断
isAlreadyAssigned(reviewer) {
  return selectedRegistrations.some(reg => {
    const assigned = assignedTasks[reg.registrationId] || []
    return assigned.includes(reviewer.id)
  })
}

// 3. 可选判断
isReviewerSelectable(reviewer) {
  return !isSameInstitution(reviewer) && 
         !isAlreadyAssigned(reviewer)
}
```

### 状态标签
```javascript
<el-tag v-if="isSameInstitution(row)" type="danger">同机构</el-tag>
<el-tag v-else-if="isAlreadyAssigned(row)" type="warning">已分配</el-tag>
<el-tag v-else type="success">可分配</el-tag>
```

### 分配前检查
```javascript
// 收集所有冲突
const conflicts = []

selectedRegistrations.forEach(reg => {
  selectedReviewers.forEach(reviewer => {
    if (reg.institutionId === reviewer.institutionId) {
      conflicts.push({ reason: '同机构回避' })
    } else if (assignedTasks[reg.id]?.includes(reviewer.id)) {
      conflicts.push({ reason: '已分配过' })
    }
  })
})

// 如果有冲突，阻止并提示
if (conflicts.length > 0) {
  ElMessageBox.alert('检测到分配冲突，无法分配...')
  return  // 不发送任何请求
}
```

## 用户体验

### 界面效果

#### 评委列表
```
□ 姓名  职称    机构        状态
☑ 张三  主任    邵逸夫医院  ✅ 可分配
□ 李四  副主任  浙大一院    🚫 同机构 (禁用)
□ 王五  主任    中医院      ⚠️  已分配 (禁用)
☑ 赵六  主任    省人民      ✅ 可分配
```

#### 分配冲突提示
```
┌────────────────────────────────────┐
│ 分配冲突                            │
├────────────────────────────────────┤
│ 检测到分配冲突，无法分配：         │
│                                    │
│ • 项目A ← 李四 (同机构回避)        │
│ • 项目B ← 王五 (已分配过)          │
│ • 项目C ← 李四 (同机构回避)        │
│                                    │
│ 请重新选择其他评委。               │
│                                    │
│                   [知道了]         │
└────────────────────────────────────┘
```

### 操作流程
```
1. 用户勾选 3 个报名项目
   ↓
2. 系统自动查询已分配的任务
   ↓
3. 评委列表自动更新状态：
   - 同机构 → 禁用 (灰色背景)
   - 已分配 → 禁用 (灰色背景)
   - 可分配 → 可选
   ↓
4. 用户勾选评委
   ↓
5. 点击"分配评委"
   ↓
6. 系统检测冲突
   - 有冲突 → 弹窗提示，返回
   - 无冲突 → 确认对话框 → 提交
```

## 优势

### 1. 零后端错误
- ✅ 不会再有 400 错误
- ✅ 不会有无效请求
- ✅ 前端完全拦住

### 2. 清晰的用户反馈
- ✅ 视觉上清楚哪些评委不可选
- ✅ 明确的冲突原因
- ✅ 引导用户正确操作

### 3. 性能优化
- ✅ 减少无效的API请求
- ✅ 批量查询，一次到位
- ✅ 客户端缓存已分配任务

## 待完成任务

需要将书审页面的实现复制到面谈和决赛页面：

1. **面谈评委分配** (`src/views/committee/interview/Reviewer.vue`)
   - 添加 `assignedTasks` ref
   - 添加 `loadAssignedTasks` 函数 (stage='INTERVIEW')
   - 修改 `handleRegistrationSelectionChange`
   - 添加 `isAlreadyAssigned` 函数
   - 修改 `isReviewerSelectable` 函数
   - 修改状态标签
   - 修改 `handleManualAssign` 函数
   - 导入 `getReviewTasksByStage`

2. **决赛评委分配** (`src/views/committee/final/Reviewer.vue`)
   - 同上，stage='FINAL'

## 测试验证

### 测试场景1: 同机构冲突
```
选择项目: 护理A (浙大一院)
选择评委: 李四 (浙大一院)
预期: 评委被禁用，无法勾选
```

### 测试场景2: 已分配冲突
```
选择项目: 护理A (已分配给张三)
选择评委: 张三
预期: 评委显示"已分配"，无法勾选
```

### 测试场景3: 多重冲突
```
选择项目: 护理A, 护理B, 护理C
选择评委: 李四 (同机构), 王五 (已分配)
预期: 弹窗显示所有冲突，不提交请求
```

### 测试场景4: 无冲突
```
选择项目: 护理A, 护理B
选择评委: 赵六, 孙七 (都可分配)
预期: 正常分配，全部成功
```
