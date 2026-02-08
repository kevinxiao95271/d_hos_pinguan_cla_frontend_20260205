# 评审专家登录信息

## 测试时间
2026-02-06 22:00

---

## ✅ 有评审任务的专家 (1位)

### 评审专家 1: Reviewer A ⭐ 推荐使用

**登录信息**:
```
手机号: 13800000021
姓名: Reviewer A
角色: REVIEWER
```

**任务信息**:
- 任务数量: 5个
- 第一个任务ID: 115
- 项目ID: 106
- 项目名称: 护理交接班规范化-1
- 状态: PENDING (待评审)

**直接访问URL**:
```
http://localhost:6039/reviewer/review/115?registrationId=106&projectName=护理交接班规范化-1
```

**测试步骤**:
1. 访问: http://localhost:6039/login
2. 输入手机号: `13800000021`
3. 点击登录
4. 点击"评审任务"菜单
5. 看到5个任务，点击第一个的"评分"按钮
6. ✅ 应该能看到完整的项目信息

---

## ⚠️ 其他评审专家（暂无任务）

以下评审专家可以登录，但暂时没有分配评审任务：

### 评审专家 2: Reviewer B
```
手机号: 13800000022
姓名: Reviewer B
角色: REVIEWER
任务数: 0
```

### 评审专家 3: Reviewer C
```
手机号: 13800000023
姓名: Reviewer C
角色: REVIEWER
任务数: 0
```

### 评审专家 4: Reviewer D
```
手机号: 13800000024
姓名: Reviewer D
角色: REVIEWER
任务数: 0
```

### 评审专家 5: Reviewer E
```
手机号: 13800000025
姓名: Reviewer E
角色: REVIEWER
任务数: 0
```

### 评审专家 6: Reviewer F
```
手机号: 13800000026
姓名: Reviewer F
角色: REVIEWER
任务数: 0
```

---

## 🔧 如何为其他专家分配任务

### 方法1: 使用管理端界面

1. **登录赛事组委会账号**
   ```
   手机号: 13800000041
   姓名: CommitteeAdmin A
   角色: COMMITTEE_ADMIN
   ```

2. **进入评委分配页面**
   - 点击"书审阶段" → "评委分配"
   - 或访问: http://localhost:6039/committee/book-stage/reviewer

3. **分配评委**
   - 选择待分配的项目（左侧列表）
   - 选择评委（右侧列表）
   - 点击"批量分配"或"手动分配"

### 方法2: 使用API直接分配

```bash
# 手动分配评审任务
POST /api/admin/reviews/tasks
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "registrationId": 106,
  "reviewerId": 7,  # Reviewer B 的ID
  "stage": "BOOK"
}
```

### 方法3: 自动分配

```bash
# 批量自动分配
POST /api/admin/reviews/auto-assign
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "competitionId": 21,
  "stage": "BOOK",
  "reviewersPerRegistration": 2  # 每个项目分配2位评委
}
```

---

## 📝 当前推荐测试方案

由于目前只有 **Reviewer A** 有任务，建议：

### 方案A: 使用现有的评审专家
```
✅ 立即可用: Reviewer A (13800000021)
   - 5个评审任务
   - 可以完整测试评分流程
```

### 方案B: 分配更多任务
1. 登录管理员账号
2. 进入"书审阶段" → "评委分配"
3. 为 Reviewer B、C、D 分配评审任务
4. 刷新评审专家页面查看新任务

---

## 🎯 快速测试指南

### 测试评委端功能

#### 步骤1: 登录
```
访问: http://localhost:6039/login
手机号: 13800000021
```

#### 步骤2: 查看任务列表
```
点击: 评审任务
应该看到: 5个待评审任务
```

#### 步骤3: 开始评分
```
点击第一个任务的"评分"按钮
应该看到:
  - 项目名称: 护理交接班规范化-1
  - 医疗机构: 浙江省中医院
  - 竞赛组别: 基层组
  - 项目详情面板（可展开）
```

#### 步骤4: 查看项目详情
```
展开"查看项目详情"面板
应该看到:
  ✅ 项目成员表格（姓名、职称、科室、角色）
  ✅ 活动说明（主题、类型、手法等）
  ✅ 项目总结（计划、问题分析、实施、成果、总结）
```

#### 步骤5: 填写评分
```
填写7个维度的分数:
  - 计划 (0-100)
  - 问题结构与对策措施探讨 (0-100)
  - 对策实施 (0-100)
  - 成功表现 (0-100)
  - 检讨 (0-100)
  - 整体运作 (0-100)
  - 资料呈现 (0-100)

填写评价:
  - 亮点（最多500字）
  - 不足之处（最多500字）
```

#### 步骤6: 提交评分
```
点击"提交评分"
确认对话框 → 点击"确认"
应该提示: "提交成功"
返回任务列表，状态变为"已完成"
```

---

## 🔍 验证项目详情是否正常显示

### 检查清单

打开评分页面后，按F12打开控制台，应该看到：

#### 1. URL参数 ✅
```
http://localhost:6039/reviewer/review/115?registrationId=106&projectName=...
```

#### 2. 控制台日志 ✅
```
项目详情加载成功: {
  projectName: "护理交接班规范化-1",
  members: 5,
  hasActivity: true,
  hasSummary: true
}
```

#### 3. 网络请求 ✅
```
GET /api/reviews/my-tasks
Status: 200

GET /api/registrations/106
Status: 200
Response: {
  "success": true,
  "data": {
    "projectName": "护理交接班规范化-1",
    "institutionName": "浙江省中医院",
    "members": [...],
    "activityInfo": {...},
    "summary": {...}
  }
}
```

#### 4. 页面显示 ✅
- [x] 项目名称显示
- [x] 医疗机构显示
- [x] 竞赛组别显示
- [x] "查看项目详情"面板可展开
- [x] 成员表格有数据
- [x] 活动说明有数据
- [x] 项目总结有数据

---

## 📞 如果遇到问题

### 问题1: 看不到项目详情
**检查**: 
- URL中是否有 `registrationId` 参数
- 控制台是否有加载成功的日志
- Network中是否有 `/api/registrations/106` 请求

### 问题2: 项目详情为空
**检查**:
- API返回的数据结构
- `members`、`activityInfo`、`summary` 字段是否存在
- 控制台是否有错误信息

### 问题3: 登录后没有任务
**解决**:
- 使用 Reviewer A (13800000021)
- 或在管理端为其他评委分配任务

---

## 📚 相关文档

- **修复说明**: `docs/REVIEWER_VIEW_DETAIL_FIX.md`
- **查找脚本**: `scripts/find_reviewers_with_tasks.py`
- **API测试**: `scripts/test_reviewer_view_detail.py`

---

## ✅ 总结

**当前可用的评审专家**: 1位
- ⭐ Reviewer A (13800000021) - 有5个任务

**建议**:
1. 先使用 Reviewer A 测试评分功能
2. 如需更多测试账号，在管理端为其他评委分配任务
3. 验证项目详情是否完整显示

**立即开始测试**: http://localhost:6039/login
