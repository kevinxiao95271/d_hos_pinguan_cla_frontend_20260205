# 参赛者报名详情API - 缺失字段报告

## 🐛 问题描述

参赛者项目详情页面的"阶段进度"（跑马灯）无法显示时间段信息。

## 📊 问题分析

### API端点
```
GET /api/registrations/{id}
```

### 问题字段
**`registration.competitionId`** - 赛事ID字段缺失

### 当前API返回结构

```json
{
  "success": true,
  "data": {
    "registration": {
      "id": 106,
      "projectName": "护理交接班规范化-1",
      "groupType": "BASIC",
      "groupCode": "A1",
      "status": "APPROVED",
      "submittedAt": "2026-02-04T15:38:52.604359",
      "createdAt": "2026-02-05T23:38:52.604359"
      // ❌ 缺少 competitionId 字段
    },
    "institution": { ... },
    "members": [ ... ],
    "activityInfo": { ... },
    "projectSummary": { ... }
  }
}
```

### 期望API返回结构

```json
{
  "success": true,
  "data": {
    "registration": {
      "id": 106,
      "competitionId": 21,  // ✅ 需要添加这个字段
      "projectName": "护理交接班规范化-1",
      "groupType": "BASIC",
      "groupCode": "A1",
      "status": "APPROVED",
      "submittedAt": "2026-02-04T15:38:52.604359",
      "createdAt": "2026-02-05T23:38:52.604359"
    },
    "institution": { ... },
    "members": [ ... ],
    "activityInfo": { ... },
    "projectSummary": { ... }
  }
}
```

---

## 🎯 影响范围

### 前端页面
- **`src/views/contestant/MyCompetition.vue`** - 参赛者项目详情页

### 功能影响
- ❌ 无法显示阶段进度（跑马灯）的时间段
- ❌ 无法根据 `competitionId` 加载赛事详细信息

### 用户体验
- 参赛者看不到当前赛事的各个阶段时间安排（报名、书审、面谈、决赛）

---

## 🔧 临时解决方案（前端）

前端已采用临时方案：从 `localStorage` 获取当前赛事ID

```javascript
// 优先使用 API 返回的 competitionId，如果没有则从 localStorage 获取
const competitionId = data.registration?.competitionId 
                      || localStorage.getItem('currentCompetitionId') 
                      || '21'  // 兜底默认值
```

### 临时方案的局限性
- ❌ 如果用户查看的是历史赛事的报名，会错误地显示当前赛事的时间段
- ❌ 依赖 localStorage，不够可靠
- ❌ 无法支持跨赛事查看功能

---

## ✅ 建议的后端修复方案

### 1. 在 Registration 实体中添加 competitionId 字段

确保数据库表 `registrations` 中有 `competition_id` 字段（应该已经存在）。

### 2. 修改 DTO 返回结构

在 `RegistrationDetailDTO` 或类似的返回对象中，添加 `competitionId` 字段：

```java
public class RegistrationDTO {
    private Long id;
    private Long competitionId;  // ✅ 添加这个字段
    private String projectName;
    private String groupType;
    private String groupCode;
    private String status;
    private LocalDateTime submittedAt;
    private LocalDateTime createdAt;
    // ... 其他字段
}
```

### 3. 在 Service 层填充数据

```java
// 示例代码
RegistrationDTO dto = new RegistrationDTO();
dto.setId(registration.getId());
dto.setCompetitionId(registration.getCompetitionId());  // ✅ 填充赛事ID
dto.setProjectName(registration.getProjectName());
// ... 其他字段
```

---

## 🧪 测试验证

### 测试脚本
已提供测试脚本：`scripts/test_contestant_detail.py`

### 验证步骤

1. 运行测试脚本：
   ```bash
   python scripts/test_contestant_detail.py
   ```

2. 检查输出中的关键字段：
   ```
   ✅ registration.competitionId: 21  ← 应该显示这个
   ```

3. 前端验证：
   - 登录参赛者账号
   - 进入"我的报名" → 点击任一项目
   - 查看阶段进度是否显示时间段

---

## 📝 相关API

### 依赖的赛事详情API
```
GET /api/competition/{id}
```

**返回示例**：
```json
{
  "id": 21,
  "name": "2026浙江品管大赛",
  "currentStage": "BOOK",
  "registrationStartTime": "2026-01-01T00:00:00",
  "registrationEndTime": "2026-01-31T23:59:59",
  "bookStartTime": "2026-02-01T00:00:00",
  "bookEndTime": "2026-02-28T23:59:59",
  "interviewStartTime": "2026-03-01T00:00:00",
  "interviewEndTime": "2026-03-31T23:59:59",
  "finalStartTime": "2026-04-01T00:00:00",
  "finalEndTime": "2026-04-30T23:59:59"
}
```

---

## 📊 数据库参考

### registrations 表结构（推测）

```sql
CREATE TABLE registrations (
  id BIGSERIAL PRIMARY KEY,
  competition_id BIGINT NOT NULL,  -- ✅ 应该已存在
  project_name VARCHAR(255),
  group_type VARCHAR(50),
  group_code VARCHAR(50),
  status VARCHAR(50),
  submitted_at TIMESTAMP,
  created_at TIMESTAMP,
  -- ... 其他字段
  
  FOREIGN KEY (competition_id) REFERENCES competitions(id)
);
```

### SQL查询示例

```sql
-- 查询某个报名的赛事ID
SELECT id, project_name, competition_id 
FROM registrations 
WHERE id = 106;

-- 验证字段存在性
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'registrations' 
  AND column_name = 'competition_id';
```

---

## 🚀 优先级

**高** - 影响用户体验，建议尽快修复

### 影响
- 参赛者无法看到赛事时间安排
- 功能不完整，影响系统专业性

### 修复难度
**低** - 只需在现有DTO中添加一个字段

### 修复时间估计
**5-10分钟**

---

**文档版本**: 1.0  
**报告时间**: 2026-02-11  
**状态**: ⏳ 待后端修复  
**临时方案**: ✅ 已实施（前端从localStorage获取）
