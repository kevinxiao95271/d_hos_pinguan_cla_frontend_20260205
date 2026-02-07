# 机构等级字段缺失API清单

## ⚠️ 已确认缺失

### 1. ✅ `GET /api/institutions` - 机构列表
**角色**: 系统运维（OPS）  
**影响页面**: `src/views/ops/Institutions.vue`  
**缺失字段**: `data[i].level`  

**当前返回**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "浙江大学医学院附属第二医院",
      "code": "INS-0001",
      "uscc": "1233000047053349XG",
      "region": null
    }
  ]
}
```

**需要添加**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "浙江大学医学院附属第二医院",
      "code": "INS-0001",
      "uscc": "1233000047053349XG",
      "region": "杭州",
      "level": "三级甲等"  // ← 需要添加此字段
    }
  ]
}
```

---

## ❓ 待确认（后端服务超时，未能测试）

### 2. `POST /api/auth/login` - 登录接口
**角色**: 所有角色  
**期望字段**: `data.institutionLevel`  

### 3. `GET /api/registrations/{id}` - 报名详情
**角色**: 参赛者（CONTESTANT）、评审专家（REVIEWER）  
**影响页面**: 
- `src/views/contestant/MyCompetition.vue`
- `src/views/reviewer/Review.vue`

**期望字段**: `data.institution.level`

### 4. `GET /api/reviews/my-tasks` - 评审任务列表
**角色**: 评审专家（REVIEWER）  
**影响页面**: 
- `src/views/reviewer/Tasks.vue`
- `src/views/reviewer/Dashboard.vue`

**期望字段**: `data[i].institutionLevel`

### 5. `GET /api/admin/registrations/filter` - 报名筛选列表
**角色**: 组委会（COMMITTEE_ADMIN）  
**影响页面**: 
- `src/views/committee/book/Registration.vue` - 项目分组
- `src/views/committee/interview/Group.vue` - 面谈分组
- `src/views/committee/book/Reviewer.vue` - 书审评委分配
- `src/views/committee/interview/Reviewer.vue` - 面谈评委分配
- `src/views/committee/final/Reviewer.vue` - 决赛评委分配

**期望字段**: `data[i].institutionLevel`

### 6. `GET /api/admin/reviews/rankings` - 评审排名列表
**角色**: 组委会（COMMITTEE_ADMIN）  
**影响页面**: `src/views/committee/interview/Shortlist.vue` - 入围管理

**期望字段**: `data[i].institutionLevel`

### 7. `GET /api/admin/reviewers` - 评审人列表
**角色**: 组委会（COMMITTEE_ADMIN）  
**影响页面**: 
- `src/views/committee/book/Reviewer.vue`
- `src/views/committee/interview/Reviewer.vue`
- `src/views/committee/final/Reviewer.vue`

**期望字段**: `data[i].institutionLevel`  
**说明**: 评委所属机构的等级，用于同机构回避UI展示

---

## 📊 影响统计

### 按角色分类
- **参赛者**: 2个页面受影响
- **评审专家**: 3个页面受影响
- **组委会**: 8个页面受影响
- **系统运维**: 1个页面受影响

### 总计
- **需要修改的前端文件**: 14个
- **需要后端添加字段的API**: 7个（1个已确认，6个待确认）

---

## 🔧 后续步骤

### Step 1: 后端API修改
请后端确认并添加缺失的 `level` / `institutionLevel` 字段。

### Step 2: API测试
后端修改完成后，前端运行测试脚本验证：
```bash
python scripts/scan_institution_level_api.py
```

### Step 3: 前端页面修改
确认所有API都支持后，前端开始修改14个页面文件。

---

## 📖 参考文档
详细扫描报告: `docs/机构等级字段需求扫描报告.md`
