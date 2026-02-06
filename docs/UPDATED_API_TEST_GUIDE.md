# 更新后的API测试指南

## 测试时间
2026-02-06

## API更新汇总

### 评委端API (4个)

| 接口 | 方法 | 说明 | 状态 |
|-----|------|------|------|
| `/api/reviews/my-tasks` | GET | 获取我的评审任务列表 | ✅ 可用 |
| `/api/registrations/{id}` | GET | 查看项目详情 | ✅ 可用 |
| `/api/reviews/scores` | POST | 提交评审评分 | ✅ 已更新 |
| `/api/reviews/scores/{taskId}` | GET | 查看已提交的评分 | ✅ 新增 |

### 参赛者端API (10个)

| 接口 | 方法 | 说明 | 状态 |
|-----|------|------|------|
| `/api/registrations/my` | GET | 我的报名列表 | ✅ 可用 |
| `/api/registrations` | POST | 创建报名 | ✅ 可用 |
| `/api/registrations/{id}` | PUT | 更新基本信息 | ✅ 新增 |
| `/api/registrations/{id}/members` | PUT | 更新成员信息 | ✅ 新增 |
| `/api/registrations/{id}/activity` | PUT | 更新活动说明 | ✅ 新增 |
| `/api/registrations/{id}/summary` | PUT | 更新项目总结 | ✅ 新增 |
| `/api/registrations/{id}/materials` | POST | 上传材料 | ✅ 新增 |
| `/api/registrations/{id}/submit` | POST | 提交审核 | ✅ 可用 |
| `/api/registrations/{id}` | GET | 查看详情 | ✅ 可用 |
| `/api/registrations/{id}/review-results` | GET | 查看评审结果 | ✅ 新增 |

---

## 测试脚本更新

### 1. 评委端测试 (`scripts/test_reviewer_workflow.py`)

#### 更新内容
```python
# ❌ 旧接口
POST /api/reviews/tasks/{taskId}/score
GET /api/reviews/results/{registrationId}

# ✅ 新接口
POST /api/reviews/scores
GET /api/reviews/scores/{taskId}
```

#### 测试流程
```
1. 评委登录
   └─> 获取 token

2. 获取我的任务列表
   GET /api/reviews/my-tasks
   └─> 返回分配给我的任务

3. 查看项目详情
   GET /api/registrations/{id}
   └─> 查看完整的项目信息

4. 提交评审评分
   POST /api/reviews/scores
   {
     "taskId": 115,
     "registrationId": 106,
     "planScore": 15,
     "problemAnalysisScore": 20,
     ...
   }

5. 查看已提交的评分
   GET /api/reviews/scores/{taskId}
   └─> 返回我提交的评分详情
```

### 2. 参赛者端测试 (`scripts/test_contestant_registration.py`)

#### 更新内容
```python
# ❌ 旧方式：一次性更新所有信息
PUT /api/registrations/{id}
{
  "projectName": "...",
  "groupType": "...",
  "activityInfo": {...},
  "members": [...]
}

# ✅ 新方式：分步更新
PUT /api/registrations/{id}          # 基本信息
PUT /api/registrations/{id}/members  # 成员信息
PUT /api/registrations/{id}/activity # 活动说明
PUT /api/registrations/{id}/summary  # 项目总结
```

#### 测试流程
```
1. 参赛者登录
   └─> 获取 token

2. 获取我的报名列表
   GET /api/registrations/my
   └─> 返回我创建的所有报名

3. 创建报名
   POST /api/registrations
   {
     "competitionId": 21,
     "institutionId": 1,
     "projectName": "测试项目",
     "groupType": "BASIC"
   }

4. 更新基本信息
   PUT /api/registrations/{id}
   {
     "projectName": "测试项目-已更新",
     "groupType": "BASIC"
   }

5. 更新成员信息
   PUT /api/registrations/{id}/members
   {
     "members": [
       {
         "name": "张三",
         "title": "主管护师",
         "department": "内科",
         "role": "PARTICIPANT"
       }
     ]
   }

6. 更新活动说明
   PUT /api/registrations/{id}/activity
   {
     "theme": "护理质量改进",
     "keywords": "护理, 质量, 改进",
     "subjectTypeCode": "PATIENT_CARE",
     "methodCode": "PDCA",
     "averageWorkYears": 8,
     "averageAge": 35
   }

7. 提交报名
   POST /api/registrations/{id}/submit
   └─> 状态变为 SUBMITTED

8. 尝试修改已提交的报名 (应被拒绝)
   PUT /api/registrations/{id}
   └─> 应返回错误

9. 再次查看报名列表
   GET /api/registrations/my
   └─> 确认状态为 SUBMITTED
```

---

## 运行测试

### 评委端测试
```bash
python scripts/test_reviewer_workflow.py
```

### 参赛者端测试
```bash
python scripts/test_contestant_registration.py
```

---

## API使用示例

### 评委端

#### 1. 获取我的任务
```javascript
// 前端调用
const res = await fetch('/api/reviews/my-tasks', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})

// 返回数据
{
  "success": true,
  "data": [
    {
      "id": 115,
      "registrationId": 106,
      "projectName": "护理交接班规范化-1",
      "stage": "BOOK",
      "status": "PENDING"
    }
  ]
}
```

#### 2. 提交评分
```javascript
// 前端调用
const res = await fetch('/api/reviews/scores', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    taskId: 115,
    registrationId: 106,
    planScore: 15,
    problemAnalysisScore: 20,
    implementationScore: 25,
    resultScore: 20,
    reviewScore: 10,
    operationScore: 5,
    presentationScore: 5,
    highlights: "亮点描述",
    shortcomings: "不足之处"
  })
})
```

#### 3. 查看评分
```javascript
// 前端调用
const res = await fetch('/api/reviews/scores/115', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})

// 返回数据
{
  "success": true,
  "data": {
    "taskId": 115,
    "planScore": 15,
    "problemAnalysisScore": 20,
    "totalScore": 100,
    "highlights": "亮点描述",
    "shortcomings": "不足之处"
  }
}
```

### 参赛者端

#### 1. 创建报名
```javascript
// 前端调用
const res = await fetch('/api/registrations', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    competitionId: 21,
    institutionId: 1,
    projectName: "测试项目",
    groupType: "BASIC"
  })
})

// 返回数据
{
  "success": true,
  "data": {
    "id": 140,
    "projectName": "测试项目",
    "status": "DRAFT"
  }
}
```

#### 2. 更新成员
```javascript
// 前端调用
const res = await fetch('/api/registrations/140/members', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    members: [
      {
        name: "张三",
        title: "主管护师",
        department: "内科",
        role: "PARTICIPANT"
      },
      {
        name: "李四",
        title: "副主任护师",
        role: "MENTOR"
      }
    ]
  })
})
```

#### 3. 提交报名
```javascript
// 前端调用
const res = await fetch('/api/registrations/140/submit', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
})

// 返回数据
{
  "success": true,
  "data": {
    "id": 140,
    "status": "SUBMITTED",
    "submittedAt": "2026-02-06T20:39:04.693"
  }
}
```

---

## 前端需要实现的功能

### 评委端 (待实现)

#### 1. 任务列表页 (`src/views/reviewer/Tasks.vue`)
- ✅ 调用 `GET /api/reviews/my-tasks`
- 显示待评审和已评审任务
- 区分不同阶段（书审/面谈/决赛）
- 点击"评审"进入评分页

#### 2. 评分页 (`src/views/reviewer/ReviewForm.vue`)
- ✅ 调用 `GET /api/registrations/{id}` 查看项目详情
- 显示评分表单（7个维度）
- 填写亮点和不足
- ✅ 调用 `POST /api/reviews/scores` 提交评分
- 提交成功后返回任务列表

#### 3. 我的评审页 (`src/views/reviewer/MyReviews.vue`)
- ✅ 调用 `GET /api/reviews/my-tasks` 筛选已完成任务
- 显示已评审的项目列表
- ✅ 调用 `GET /api/reviews/scores/{taskId}` 查看评分详情

### 参赛者端 (需完善)

#### 1. 报名列表页 (待实现)
- ✅ 调用 `GET /api/registrations/my`
- 显示所有报名记录
- 区分草稿和已提交
- 草稿显示"编辑"和"提交"按钮
- 已提交显示为灰色，只能查看

#### 2. 报名编辑页 (待实现)
- 分步表单（跑马灯）
  - 步骤1: 基本信息 → `PUT /api/registrations/{id}`
  - 步骤2: 成员信息 → `PUT /api/registrations/{id}/members`
  - 步骤3: 活动说明 → `PUT /api/registrations/{id}/activity`
  - 步骤4: 项目总结 → `PUT /api/registrations/{id}/summary`
  - 步骤5: 材料上传 → `POST /api/registrations/{id}/materials`
- 草稿自动保存
- 最后提交 → `POST /api/registrations/{id}/submit`

#### 3. 报名详情页 (已有 `MyCompetition.vue`)
- ✅ 调用 `GET /api/registrations/{id}`
- 显示完整的报名信息
- ✅ 调用 `GET /api/registrations/{id}/review-results` 查看评审结果

---

## 下一步工作

### 1. 测试验证 (优先)
- ⏸️ 等待后端稳定后运行测试脚本
- 验证所有API是否按预期工作
- 记录测试结果

### 2. 前端实现 (后续)
- 实现评委端完整页面
- 完善参赛者报名流程
- 实现分步表单
- 实现草稿保存和已提交保护

### 3. 端到端测试
- 完整走通评委评审流程
- 完整走通参赛者报名流程
- 测试各种边界情况

---

## 相关文件

- 评委端测试脚本: `scripts/test_reviewer_workflow.py`
- 参赛者端测试脚本: `scripts/test_contestant_registration.py`
- API测试报告: `docs/API_WORKFLOW_TEST_REPORT.md`
