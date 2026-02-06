# 评审专家查看项目详情 - 修复说明

## 问题描述
评审专家在评分页面看不到项目的详细信息。

## 根本原因
Review.vue 页面只显示了项目名称和评审阶段，**没有显示项目的完整内容**，包括：
- 成员信息
- 活动说明
- 项目总结

## 修复内容

### 1. 添加项目详情展示区域

在评分表单上方添加了一个可折叠的详情面板，包含：

#### 项目基本信息
- 项目名称
- 医疗机构
- 评审阶段
- 竞赛组别

#### 项目成员（表格展示）
- 姓名
- 职称
- 科室
- 角色（参与人员/辅导员）

#### 活动说明
- 活动主题
- 关键词
- 主题类型
- 运用手法
- 平均工作年限
- 平均年龄

#### 项目总结
- 计划
- 问题分析
- 实施过程
- 成果表现
- 讨论总结

### 2. 更新数据加载逻辑

```javascript
// 保存完整的项目详情
const projectDetail = ref(null)

// 在loadData中保存完整数据
projectDetail.value = detailRes.data

// 添加详细的日志
console.log('项目详情加载成功:', {
  projectName: data.projectName,
  members: data.members?.length,
  hasActivity: !!data.activityInfo,
  hasSummary: !!data.summary
})
```

### 3. 添加错误提示

```javascript
// 如果缺少registrationId
if (!registrationId.value) {
  console.warn('缺少 registrationId，无法加载项目详情')
  ElMessage.warning('缺少项目ID，无法加载详情')
}
```

---

## 完整流程验证

### 前端流程
```
1. 评委登录
   ↓
2. 进入任务列表 (/reviewer/tasks)
   API: GET /api/reviews/my-tasks
   ↓
3. 点击"评分"按钮
   跳转: /reviewer/review/{taskId}?registrationId=xxx&projectName=xxx
   ↓
4. Review.vue 页面
   - 从 route.params.taskId 获取任务ID
   - 从 route.query.registrationId 获取项目ID
   - 调用 GET /api/registrations/{registrationId} 获取项目详情
   ↓
5. 显示项目完整信息
   - 基本信息（卡片顶部）
   - 项目详情（折叠面板）
   - 评分表单
```

### API调用链
```javascript
// 1. 获取任务列表
GET /api/reviews/my-tasks
返回: [
  {
    id: 115,                      // taskId
    registrationId: 106,          // 项目ID ⚠️ 必须有值
    projectName: "护理交接班规范化-1",
    stage: "BOOK",
    status: "PENDING"
  }
]

// 2. 获取项目详情
GET /api/registrations/106
返回: {
  id: 106,
  projectName: "护理交接班规范化-1",
  institutionName: "浙江省中医院",
  groupType: "BASIC",
  members: [...],
  activityInfo: {...},
  summary: {...}
}
```

---

## 调试方法

### 1. 检查 URL 参数
打开评分页面，在浏览器控制台输入：
```javascript
console.log('URL:', window.location.href)
console.log('taskId:', this.$route.params.taskId)
console.log('registrationId:', this.$route.query.registrationId)
```

**预期结果**:
```
URL: http://localhost:6039/reviewer/review/115?registrationId=106&projectName=...
taskId: 115
registrationId: 106  ⚠️ 必须有值
```

### 2. 检查 API 调用
打开浏览器开发者工具 → Network 标签，查看：

```
请求: GET /api/registrations/106
状态: 200
响应: {
  "success": true,
  "data": {
    "id": 106,
    "projectName": "护理交接班规范化-1",
    "institutionName": "浙江省中医院",
    "members": [...],
    "activityInfo": {...},
    "summary": {...}
  }
}
```

### 3. 检查控制台日志
在 Review.vue 页面，控制台应该显示：

```
项目详情加载成功: {
  projectName: "护理交接班规范化-1",
  members: 5,
  hasActivity: true,
  hasSummary: true
}
```

### 4. 检查页面显示
- ✅ 项目名称显示正确
- ✅ 医疗机构显示正确
- ✅ 可以展开"查看项目详情"面板
- ✅ 成员表格有数据
- ✅ 活动说明有数据
- ✅ 项目总结有数据

---

## 常见问题排查

### 问题1: registrationId 为空
**症状**: 无法加载项目详情，提示"缺少项目ID"

**排查**:
```javascript
// 检查任务列表API返回
GET /api/reviews/my-tasks
// 确认返回的任务中 registrationId 不为 null
```

**解决**: 
- 如果 registrationId 为 null，这是后端数据问题
- 需要后端确保任务创建时正确保存 registrationId

### 问题2: API返回404
**症状**: GET /api/registrations/{id} 返回 404

**排查**:
```javascript
// 确认 registrationId 是否正确
console.log('registrationId:', route.query.registrationId)
```

**解决**:
- 确认该项目在数据库中存在
- 确认 registrationId 值正确

### 问题3: 项目详情为空
**症状**: API返回200，但页面显示为空

**排查**:
```javascript
// 检查返回的数据结构
console.log('projectDetail:', projectDetail.value)
```

**解决**:
- 确认 API 返回的数据结构正确
- 确认 members、activityInfo、summary 字段存在
- 检查 Vue 数据绑定是否正确

---

## 测试步骤

### 手动测试
1. 登录评委账号: `13800000021`
2. 进入"评审任务"菜单
3. 找到待评审任务，点击"评分"
4. **检查点1**: URL中是否有 `registrationId` 参数
5. **检查点2**: 页面顶部是否显示项目名称和医疗机构
6. **检查点3**: 点击"查看项目详情"，是否显示完整信息
7. **检查点4**: 成员表格是否有数据
8. **检查点5**: 活动说明是否有数据
9. **检查点6**: 项目总结是否有数据

### API测试脚本
```bash
python scripts/test_reviewer_view_detail.py
```

---

## 修复后的预期效果

### 评分页面布局
```
┌─────────────────────────────────────┐
│ 评分 - 护理交接班规范化-1            │
├─────────────────────────────────────┤
│ 项目信息                            │
│   项目名称: 护理交接班规范化-1      │
│   医疗机构: 浙江省中医院            │
│   评审阶段: 书审                    │
│   竞赛组别: 基层组                  │
│                                     │
│ [▼ 查看项目详情]                    │
│   ┌───────────────────────────┐     │
│   │ 项目成员                  │     │
│   │ [表格: 姓名|职称|科室|角色]│     │
│   │                           │     │
│   │ 活动说明                  │     │
│   │ 主题: xxx                 │     │
│   │ 手法: xxx                 │     │
│   │                           │     │
│   │ 项目总结                  │     │
│   │ 计划: xxx                 │     │
│   │ 问题分析: xxx             │     │
│   └───────────────────────────┘     │
│                                     │
│ 评分                                │
│   计划: [15分]                      │
│   问题分析: [20分]                  │
│   ...                               │
│   亮点: [文本框]                    │
│   不足: [文本框]                    │
│                                     │
│ [提交评分] [返回]                   │
└─────────────────────────────────────┘
```

---

## 总结

✅ 已添加完整的项目详情展示
✅ 添加了折叠面板，默认展开
✅ 包含成员、活动说明、项目总结所有内容
✅ 添加了详细的错误提示和日志
✅ 提供了完整的调试方法

现在评审专家可以：
1. 看到项目的完整信息
2. 了解成员构成
3. 了解活动背景
4. 阅读项目总结
5. 基于完整信息进行评分

**请刷新页面测试！**
