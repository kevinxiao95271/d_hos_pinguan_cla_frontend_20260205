# 入围管理-API错误修复报告

## 📝 问题描述

用户反馈：入围管理页面点击"查看详情"时会报错。

**具体现象**:
- 页面：http://localhost:6039/committee/interview/shortlist
- 操作：点击项目列表中的"查看详情"按钮
- 结果：控制台报错，详情对话框无法正常加载

## 🔍 问题排查

### 1. API测试

运行测试脚本 `scripts/test_shortlist_apis.py` 发现：

| API | 路径 | 状态 | 说明 |
|-----|------|------|------|
| rankings | `/api/admin/reviews/rankings` | ✅ 200 | 正常工作 |
| review-details | `/api/registrations/{id}/review-details` | ✅ 200 | 正常工作 |
| reviewer-scores (书审) | `/api/registrations/{id}/reviewer-scores?stage=BOOK` | ❌ **404** | **接口不存在** |
| reviewer-scores (面谈) | `/api/registrations/{id}/reviewer-scores?stage=INTERVIEW` | ❌ **404** | **接口不存在** |

### 2. 错误原因

在 `src/views/committee/interview/Shortlist.vue` 的 `viewDetail` 函数中，使用了 `Promise.all` 并行调用3个API：

```javascript
// ❌ 问题代码
const [detailsResponse, bookReviewersResponse, interviewReviewersResponse] = await Promise.all([
  getRegistrationReviewDetails(project.registrationId),  // ✅ 200
  getReviewerScores(project.registrationId, 'BOOK'),     // ❌ 404
  getReviewerScores(project.registrationId, 'INTERVIEW') // ❌ 404
])
```

由于 `getReviewerScores` 接口返回404，导致 `Promise.all` 抛出异常，整个详情加载流程失败。

### 3. 根本原因

**后端接口 `/api/registrations/{id}/reviewer-scores` 尚未实现**

这个接口应该返回每个评委的详细评分，但后端还没有开发这个功能。

## ✅ 解决方案

### 修改内容

**文件**: `src/views/committee/interview/Shortlist.vue`

**修改位置**: `viewDetail` 函数（第1042-1104行）

**修改策略**:
1. 移除对不存在接口的并行调用
2. 只调用已实现的 `getRegistrationReviewDetails` 接口
3. 暂时清空评委详细评分数据（显示"暂无评委评分记录"）
4. 添加TODO注释，等待后端实现接口后再启用

### 修改前

```javascript
try {
  // 并行调用评审详情API和评委评分API
  const [detailsResponse, bookReviewersResponse, interviewReviewersResponse] = await Promise.all([
    getRegistrationReviewDetails(project.registrationId),
    getReviewerScores(project.registrationId, 'BOOK'),      // ❌ 404错误
    getReviewerScores(project.registrationId, 'INTERVIEW')  // ❌ 404错误
  ])
  
  // ... 数据处理
} catch (error) {
  console.error('加载详情失败:', error)  // ❌ 会捕获404错误
  ElMessage.error('加载详情失败')
}
```

### 修改后

```javascript
try {
  // 只调用已实现的评审详情API
  const detailsResponse = await getRegistrationReviewDetails(project.registrationId)
  
  // 处理汇总平均分（正常工作）
  if (detailsResponse.success && detailsResponse.data) {
    // ... 数据处理
  }
  
  // TODO: 等待后端实现 /api/registrations/{id}/reviewer-scores 接口后再启用
  // 暂时清空评委详细评分数据
  bookReviewers.value = []
  interviewReviewers.value = []
  
  /* 预留代码（已注释）
  try {
    const bookReviewersResponse = await getReviewerScores(project.registrationId, 'BOOK')
    if (bookReviewersResponse.success && bookReviewersResponse.data) {
      bookReviewers.value = bookReviewersResponse.data
    }
  } catch (err) {
    console.warn('获取书审评委详细评分失败（接口可能未实现）:', err)
  }
  */
  
} catch (error) {
  console.error('加载详情失败:', error)
  ElMessage.error('加载详情失败')
}
```

## 📊 修复效果

### 修复前
```
❌ 点击"查看详情"
   → 调用3个API
   → 2个返回404
   → Promise.all抛出异常
   → 详情对话框加载失败
   → 显示错误提示
```

### 修复后
```
✅ 点击"查看详情"
   → 调用1个API（review-details）
   → 返回200，数据正常
   → 详情对话框正常打开
   → 显示汇总平均分、分项得分、亮点、改进建议
   → 评委详细评分部分显示"暂无评委评分记录"
```

## 🎯 测试验证

### 功能测试

1. **打开入围管理页面**
   - [ ] 页面正常加载，无控制台错误
   - [ ] 项目列表正常显示

2. **查看详情（基层组项目）**
   - [ ] 点击"查看详情"按钮
   - [ ] 详情对话框正常打开
   - [ ] ✅ 显示综合得分、书审得分
   - [ ] ✅ 显示分项得分（计划、问题、行动等）
   - [ ] ✅ 显示亮点和改进建议
   - [ ] ✅ 评委详细评分部分显示"暂无评委评分记录"

3. **查看详情（进阶组项目）**
   - [ ] 书审评分tab正常显示
   - [ ] 面谈评分tab正常显示
   - [ ] 两个tab都显示汇总数据
   - [ ] 两个tab都显示"暂无评委评分记录"

### 数据准确性

- [ ] 书审得分与列表中显示一致
- [ ] 面谈得分与列表中显示一致
- [ ] 综合得分计算正确
- [ ] 分项得分显示完整

## 📋 API数据示例

### review-details API（正常工作）

```json
{
  "success": true,
  "data": [
    {
      "stage": "BOOK",
      "taskCount": 2,
      "scoredCount": 1,
      "avgPlan": 18.0,
      "avgProblem": 17.0,
      "avgAction": 19.0,
      "avgSuccess": 18.0,
      "avgReview": 16.0,
      "avgOperation": 0.0,
      "avgPresentation": 0.0,
      "avgTotal": 88.0,
      "highlights": [
        "项目主题明确，改进措施得当，成效显著..."
      ],
      "weaknesses": [
        "建议进一步量化成本效益分析..."
      ]
    }
  ]
}
```

## ⚠️ 待办事项

### 1. 后端开发任务

**需要实现的接口**:
```
GET /api/registrations/{id}/reviewer-scores?stage={BOOK|INTERVIEW|FINAL}
```

**应返回数据格式**:
```json
{
  "success": true,
  "data": [
    {
      "reviewerId": 41,
      "reviewerName": "张三",
      "reviewerTitle": "主任",
      "reviewerInstitutionName": "浙江省人民医院",
      "reviewerInstitutionLevel": "三级甲等",
      "scores": {
        "plan": 18,
        "problem": 17,
        "action": 19,
        "success": 18,
        "review": 16,
        "operation": 0,
        "presentation": 0,
        "total": 88
      },
      "highlight": "项目主题明确...",
      "weakness": "建议进一步...",
      "submittedAt": "2026-02-07T10:30:00"
    }
  ]
}
```

### 2. 前端恢复代码

当后端接口实现后，需要：

1. 在 `src/views/committee/interview/Shortlist.vue` 中
2. 找到 `viewDetail` 函数
3. 取消注释评委详细评分API调用代码
4. 删除 `bookReviewers.value = []` 等清空代码

```javascript
// 恢复这段代码
try {
  const bookReviewersResponse = await getReviewerScores(project.registrationId, 'BOOK')
  if (bookReviewersResponse.success && bookReviewersResponse.data) {
    bookReviewers.value = bookReviewersResponse.data
  }
} catch (err) {
  console.warn('获取书审评委详细评分失败:', err)
}
```

## 📝 相关文件

- `src/views/committee/interview/Shortlist.vue` - 入围管理页面（已修改）
- `src/api/registration.js` - API定义（无需修改）
- `scripts/test_shortlist_apis.py` - API测试脚本（新增）

## 🔄 版本对比

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| 详情加载是否正常 | ❌ 报错 | ✅ 正常 |
| 汇总平均分显示 | ❌ 无法显示 | ✅ 正常显示 |
| 分项得分显示 | ❌ 无法显示 | ✅ 正常显示 |
| 亮点和建议显示 | ❌ 无法显示 | ✅ 正常显示 |
| 评委详细评分 | ❌ 报错 | ⚠️ 显示"暂无记录" |

## 📅 更新日志

**2026-02-08**:
- ✅ 诊断API问题（reviewer-scores接口404）
- ✅ 修改前端代码移除失败的API调用
- ✅ 测试修复效果
- ✅ 创建测试脚本 `test_shortlist_apis.py`
- ✅ 编写修复文档

---

**报告生成时间**: 2026-02-08  
**问题状态**: ✅ 已修复（临时方案）  
**完整方案**: ⏳ 待后端实现 reviewer-scores 接口
