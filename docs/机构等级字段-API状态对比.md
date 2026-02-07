# 机构等级字段 - API状态对比报告

**检测时间**: 2026-02-07  
**后端声明**: 已添加部分字段  
**前端测试**: 尚未检测到字段（可能需要重启后端服务）

---

## ✅ 后端已声明添加的API（10个）

| API | 字段路径 | 字段名 | 前端测试状态 |
|-----|---------|--------|------------|
| `POST /api/auth/login` | `data.institutionRegion` | institutionRegion | ⏳ 待验证 |
| `POST /api/auth/login` | `data.institutionLevel` | institutionLevel | ⏳ 待验证 |
| `GET /api/registrations/{id}` | `data.institution.level` | level | ⏳ 待验证 |
| `GET /api/institutions` | `data[i].level` | level | ⏳ 待验证 |
| `GET /api/institutions/{id}` | `data.level` | level | ⏳ 待验证 |
| `GET /api/admin/institutions/export` | `data[i].level` | level | ⏳ 待验证 |
| `GET /api/reviews/my-tasks` | `data[i].institutionLevel` | institutionLevel | ⏳ 待验证 |
| `GET /api/admin/registrations/filter` | `data[i].institutionLevel` | institutionLevel | ⏳ 待验证 |
| `GET /api/admin/reviews/rankings` | `data[i].institutionLevel` | institutionLevel | ⏳ 待验证 |
| `GET /api/admin/reviews/reviewers` | `data[i].institutionLevel` | institutionLevel | ⏳ 待验证 |

**注意**: `GET /api/admin/reviews/reviewers` 在测试脚本中是 `GET /api/admin/reviewers`，可能是同一个API的不同路径。

---

## ❌ 仍然缺失的API（需要后端补充）

| API | 字段路径 | 字段名 | 影响角色 | 影响页面 |
|-----|---------|--------|---------|---------|
| `GET /api/registrations/my` | `data[i].institutionLevel` | institutionLevel | 参赛者 | 我的报名列表 |
| `GET /api/registrations/{id}/review-results` | `data[i].institutionLevel` | institutionLevel | 参赛者 | 评审结果页面 |
| `GET /api/reviews/tasks/stage` | `data[i].institutionLevel` | institutionLevel | 组委会 | 评审任务管理 |
| `GET /api/reviews/tasks/stage` | `data[i].projectName` | projectName | 组委会 | 评审任务管理 |
| `GET /api/reviews/tasks/stage` | `data[i].institutionName` | institutionName | 组委会 | 评审任务管理 |

**说明**:
- `GET /api/registrations/my` - 如果列表需要显示机构等级
- `GET /api/registrations/{id}/review-results` - 评审结果查看时需要显示机构等级
- `GET /api/reviews/tasks/stage` - 目前只返回任务ID和状态，缺少项目和机构信息

---

## 📊 统计汇总

### 后端已添加
- ✅ **登录API**: 2个字段（institutionRegion, institutionLevel）
- ✅ **机构API**: 3个接口添加 level 字段
- ✅ **报名API**: 1个接口添加 level 字段
- ✅ **评审API**: 3个接口添加 institutionLevel 字段
- **总计**: 10个字段（涉及10个API）

### 仍需补充
- ❌ **报名API**: 2个接口缺少 institutionLevel
- ❌ **评审API**: 1个接口缺少项目和机构完整信息
- **总计**: 5个字段（涉及3个API）

---

## 🔍 详细对比

### 1. 登录API ✅

#### `POST /api/auth/login`
**后端已添加**:
```json
{
  "data": {
    "token": "...",
    "institutionRegion": "杭州",      // ✅ 已添加
    "institutionLevel": "三级甲等"    // ✅ 已添加
  }
}
```

**前端测试结果**: ⏳ 待验证（当前测试显示为 None，可能需要重启服务）

---

### 2. 报名详情API ✅

#### `GET /api/registrations/{id}`
**后端已添加**:
```json
{
  "data": {
    "institution": {
      "id": 11,
      "name": "浙江大学医学院附属儿童医院",
      "code": "INS-0011",
      "uscc": "12330000470533493L",
      "region": "杭州",
      "level": "三级甲等"              // ✅ 已添加
    }
  }
}
```

**影响页面**:
- `src/views/contestant/MyCompetition.vue` - 参赛者报名详情
- `src/views/reviewer/Review.vue` - 评审专家查看项目详情

---

### 3. 机构管理API ✅

#### `GET /api/institutions`
**后端已添加**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "浙江大学医学院附属第二医院",
      "code": "INS-0001",
      "uscc": "1233000047053349XG",
      "region": "杭州",
      "level": "三级甲等"              // ✅ 已添加
    }
  ]
}
```

**影响页面**: `src/views/ops/Institutions.vue`

#### `GET /api/institutions/{id}`
**后端已添加**: `data.level`  
**影响**: 机构详情查看

#### `GET /api/admin/institutions/export`
**后端已添加**: `data[i].level`  
**影响**: 机构导出功能

---

### 4. 评审任务API ✅

#### `GET /api/reviews/my-tasks`
**后端已添加**:
```json
{
  "data": [
    {
      "id": 115,
      "registrationId": 106,
      "projectName": "护理交接班规范化-1",
      "institutionName": "浙江大学医学院附属第二医院",
      "institutionLevel": "三级甲等",   // ✅ 已添加
      "stage": "BOOK",
      "status": "SCORED"
    }
  ]
}
```

**影响页面**:
- `src/views/reviewer/Tasks.vue` - 评审任务列表
- `src/views/reviewer/Dashboard.vue` - 评审专家Dashboard

---

### 5. 报名筛选API ✅

#### `GET /api/admin/registrations/filter`
**后端已添加**:
```json
{
  "data": [
    {
      "registrationId": 106,
      "projectName": "护理交接班规范化-1",
      "institutionName": "浙江大学医学院附属第二医院",
      "institutionLevel": "三级甲等",   // ✅ 已添加
      "groupType": "BASIC",
      "applicantName": "参赛者1"
    }
  ]
}
```

**影响页面**:
- `src/views/committee/book/Registration.vue` - 项目分组
- `src/views/committee/interview/Group.vue` - 面谈分组
- `src/views/committee/book/Reviewer.vue` - 书审评委分配
- `src/views/committee/interview/Reviewer.vue` - 面谈评委分配
- `src/views/committee/final/Reviewer.vue` - 决赛评委分配

---

### 6. 评审排名API ✅

#### `GET /api/admin/reviews/rankings`
**后端已添加**:
```json
{
  "data": [
    {
      "rank": 1,
      "registrationId": 106,
      "projectName": "护理交接班规范化-1",
      "institutionName": "浙江大学医学院附属第二医院",
      "institutionLevel": "三级甲等",   // ✅ 已添加
      "groupType": "BASIC",
      "stage": "BOOK",
      "avgTotal": 88.0
    }
  ]
}
```

**影响页面**: `src/views/committee/interview/Shortlist.vue` - 入围管理

---

### 7. 评审人列表API ✅

#### `GET /api/admin/reviews/reviewers` 或 `GET /api/admin/reviewers`
**后端已添加**:
```json
{
  "data": [
    {
      "id": 6,
      "phone": "13800000021",
      "name": "Li Minghua",
      "institutionId": 2,
      "institutionName": "浙江省中医院",
      "institutionLevel": "三级甲等",   // ✅ 已添加
      "expertBackground": "MEDICAL"
    }
  ]
}
```

**影响页面**:
- `src/views/committee/book/Reviewer.vue` - 书审评委分配
- `src/views/committee/interview/Reviewer.vue` - 面谈评委分配
- `src/views/committee/final/Reviewer.vue` - 决赛评委分配

**用途**: 显示评委所属机构等级，用于同机构回避UI提示

---

## ❌ 仍需后端补充的API

### 1. 我的报名列表

#### `GET /api/registrations/my`
**当前返回**:
```json
{
  "data": [
    {
      "id": 116,
      "competitionId": 21,
      "institutionId": 11,
      "projectName": "门诊预约体验提升-11",
      "groupType": "COMPREHENSIVE",
      "status": "APPROVED"
      // ❌ 缺少 institutionLevel
    }
  ]
}
```

**需要添加**:
```json
{
  "data": [
    {
      "id": 116,
      "competitionId": 21,
      "institutionId": 11,
      "institutionName": "嘉兴市第一医院",      // 如果需要
      "institutionLevel": "三级甲等",           // ✅ 需要添加
      "projectName": "门诊预约体验提升-11",
      "groupType": "COMPREHENSIVE",
      "status": "APPROVED"
    }
  ]
}
```

**影响页面**: `src/views/contestant/MyRegistrations.vue`  
**说明**: 如果列表需要显示机构等级，则需要添加此字段

---

### 2. 评审结果查看

#### `GET /api/registrations/{id}/review-results`
**期望添加**: `data[i].institutionLevel`

**影响页面**: `src/views/contestant/ReviewResults.vue`  
**说明**: 查看评审结果时，可能需要显示评审专家所属机构等级

---

### 3. 按阶段获取评审任务

#### `GET /api/reviews/tasks/stage?competitionId=21&stage=BOOK`
**当前返回**:
```json
{
  "data": [
    {
      "id": 115,
      "stage": "BOOK",
      "status": "SCORED",
      "createdAt": "2026-02-06T18:12:37.447"
      // ❌ 缺少项目信息和机构信息
    }
  ]
}
```

**需要添加**:
```json
{
  "data": [
    {
      "id": 115,
      "registrationId": 106,              // ✅ 需要添加
      "projectName": "护理交接班规范化-1",   // ✅ 需要添加
      "institutionName": "浙江大学医学院附属第二医院", // ✅ 需要添加
      "institutionLevel": "三级甲等",       // ✅ 需要添加
      "stage": "BOOK",
      "status": "SCORED",
      "createdAt": "2026-02-06T18:12:37.447"
    }
  ]
}
```

**影响**: 组委会查看评审任务进度时，需要显示项目和机构信息  
**说明**: 该API目前信息过于简单，建议添加完整的项目和机构信息

---

## 🔧 后续步骤

### Step 1: 后端重启服务 ⏳
后端已添加的10个API字段，需要重启服务使其生效。

### Step 2: 前端验证 🔍
后端重启后，运行测试脚本验证：
```bash
python scripts/scan_institution_level_api.py
```

### Step 3: 后端补充剩余API ⚙️
补充3个还缺少的API字段。

### Step 4: 前端开发 💻
确认所有API都支持后，前端开始修改14个页面文件。

---

## 📝 快速参考表

### ✅ 已添加（需验证）
| API | 字段路径 | 字段名 |
|-----|---------|--------|
| `POST /api/auth/login` | `data.institutionRegion` | institutionRegion |
| `POST /api/auth/login` | `data.institutionLevel` | institutionLevel |
| `GET /api/registrations/{id}` | `data.institution.level` | level |
| `GET /api/institutions` | `data[i].level` | level |
| `GET /api/institutions/{id}` | `data.level` | level |
| `GET /api/admin/institutions/export` | `data[i].level` | level |
| `GET /api/reviews/my-tasks` | `data[i].institutionLevel` | institutionLevel |
| `GET /api/admin/registrations/filter` | `data[i].institutionLevel` | institutionLevel |
| `GET /api/admin/reviews/rankings` | `data[i].institutionLevel` | institutionLevel |
| `GET /api/admin/reviews/reviewers` | `data[i].institutionLevel` | institutionLevel |

### ❌ 仍需添加
| API | 字段路径 | 字段名 |
|-----|---------|--------|
| `GET /api/registrations/my` | `data[i].institutionLevel` | institutionLevel |
| `GET /api/registrations/{id}/review-results` | `data[i].institutionLevel` | institutionLevel |
| `GET /api/reviews/tasks/stage` | `data[i].projectName` | projectName |
| `GET /api/reviews/tasks/stage` | `data[i].institutionName` | institutionName |
| `GET /api/reviews/tasks/stage` | `data[i].institutionLevel` | institutionLevel |

---

**报告生成时间**: 2026-02-07  
**状态**: 等待后端服务重启验证
