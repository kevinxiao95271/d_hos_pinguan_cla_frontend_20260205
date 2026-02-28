# OPS报名详情 - 机构信息显示问题分析

**分析时间：** 2026-02-28  
**测试项目：** 项目编号70  
**问题：** 详情页机构信息未显示  
**状态：** ✅ 问题已定位

---

## 🔍 问题现象

**用户反馈：**
```
系统管理 → 报名列表 → 点击详情

显示结果：
  医疗机构: (空白)
  机构等级: -
```

**测试项目：**
- 项目编号：70
- 项目名称：病人照护-PDCA-杭州市求是教育集团浙江大学附属小学卫生站-63

---

## ✅ 核查结果

### 后端API返回情况

**接口：** `GET /api/registrations/70`

**状态：** ✅ **后端API有返回机构信息**

**实际返回数据：**
```json
{
  "success": true,
  "data": {
    "registration": {
      "id": 70,
      "projectName": "病人照护-PDCA-杭州市求是教育集团浙江大学附属小学卫生站-63",
      "groupType": "BASIC",
      "status": "SUBMITTED"
    },
    "institution": {
      "id": 36177,
      "name": "桐庐县第一人民医院",    ← 机构名称
      "code": "INST_D05D0E2A",
      "uscc": "123301224703200842",
      "region": "桐庐县",
      "level": "二级"                    ← 机构等级
    },
    "members": [...],
    "activityInfo": {...},
    "projectSummary": {...},
    "materials": []
  }
}
```

**结论：** ✅ 后端API完整返回了机构信息，包含name和level字段。

---

## 🐛 问题根因

### 字段路径不匹配

**后端实际返回的数据结构：**
```javascript
data.institution.name   // 机构名称: "桐庐县第一人民医院"
data.institution.level  // 机构等级: "二级"
```

**前端代码尝试访问的路径：**
```javascript
// src/views/ops/Registrations.vue 第226-230行
currentDetail.registration?.institutionName  // ❌ 不存在
currentDetail.institutionName                // ❌ 不存在
currentDetail.registration?.institutionLevel // ❌ 不存在
currentDetail.institutionLevel               // ❌ 不存在
```

**正确的访问路径应该是：**
```javascript
currentDetail.institution?.name   // ✅ 机构名称
currentDetail.institution?.level  // ✅ 机构等级
```

---

## 📊 详细对比

### 后端返回的数据结构

```json
{
  "data": {
    "registration": {
      "id": 70,
      "projectName": "...",
      "groupType": "BASIC",
      "status": "SUBMITTED"
      // ❌ 没有 institutionName 字段
      // ❌ 没有 institutionLevel 字段
    },
    "institution": {
      "id": 36177,
      "name": "桐庐县第一人民医院",     // ✅ 机构名称在这里
      "level": "二级",                   // ✅ 机构等级在这里
      "code": "INST_D05D0E2A",
      "uscc": "123301224703200842",
      "region": "桐庐县"
    },
    "members": [...],
    "activityInfo": {...}
  }
}
```

### 前端代码当前逻辑

**文件：** `src/views/ops/Registrations.vue`

**第226-230行（错误的访问路径）：**
```vue
<el-descriptions-item label="医疗机构">
  {{ currentDetail.registration?.institutionName || currentDetail.institutionName }}
</el-descriptions-item>
<el-descriptions-item label="机构等级">
  {{ currentDetail.registration?.institutionLevel || currentDetail.institutionLevel || '-' }}
</el-descriptions-item>
```

**问题：**
- `currentDetail.registration.institutionName` - ❌ 字段不存在
- `currentDetail.institutionName` - ❌ 字段不存在
- `currentDetail.registration.institutionLevel` - ❌ 字段不存在
- `currentDetail.institutionLevel` - ❌ 字段不存在

**正确的访问路径：**
- `currentDetail.institution.name` - ✅ 机构名称
- `currentDetail.institution.level` - ✅ 机构等级

---

## 🔄 参考实现

### 组委会页面的正确实现

**文件：** `src/views/committee/book/Registration.vue`

**第304-311行（正确的访问路径）：**
```vue
<el-descriptions-item label="医疗机构名称">
  {{ currentDetail.institution.name }}
</el-descriptions-item>
<el-descriptions-item label="机构等级">
  <el-tag v-if="currentDetail.institution.level" type="success">
    {{ currentDetail.institution.level }}
  </el-tag>
</el-descriptions-item>
```

**关键差异：**
- 组委会页面：访问 `currentDetail.institution.name` ✅
- OPS页面：访问 `currentDetail.registration?.institutionName` ❌

---

## 📋 完整的字段映射

| 显示内容 | 后端返回位置 | 前端当前访问路径 | 正确访问路径 | 状态 |
|---------|-------------|-----------------|-------------|------|
| 医疗机构 | `data.institution.name` | `registration.institutionName` | `institution.name` | ❌ 错误 |
| 机构等级 | `data.institution.level` | `registration.institutionLevel` | `institution.level` | ❌ 错误 |
| 机构代码 | `data.institution.code` | - | `institution.code` | - |
| 统一信用代码 | `data.institution.uscc` | - | `institution.uscc` | - |
| 所在地区 | `data.institution.region` | - | `institution.region` | - |

---

## 🎯 解决方案

### 需要修改的代码

**文件：** `src/views/ops/Registrations.vue`

**第226-230行：**

**当前代码（错误）：**
```vue
<el-descriptions-item label="医疗机构">
  {{ currentDetail.registration?.institutionName || currentDetail.institutionName }}
</el-descriptions-item>
<el-descriptions-item label="机构等级">
  {{ currentDetail.registration?.institutionLevel || currentDetail.institutionLevel || '-' }}
</el-descriptions-item>
```

**应该改为（正确）：**
```vue
<el-descriptions-item label="医疗机构">
  {{ currentDetail.institution?.name || '-' }}
</el-descriptions-item>
<el-descriptions-item label="机构等级">
  <el-tag v-if="currentDetail.institution?.level" type="success" size="small">
    {{ currentDetail.institution.level }}
  </el-tag>
  <span v-else>-</span>
</el-descriptions-item>
```

---

## 📝 测试验证

### 实际API返回（项目70）

```json
{
  "institution": {
    "id": 36177,
    "name": "桐庐县第一人民医院",
    "level": "二级",
    "code": "INST_D05D0E2A",
    "uscc": "123301224703200842",
    "region": "桐庐县"
  }
}
```

### 修复后的显示效果

```
医疗机构: 桐庐县第一人民医院
机构等级: [绿色标签] 二级
```

---

## ⚠️ 其他可能受影响的字段

检查OPS详情页是否还有其他字段访问路径错误：

| 字段 | 当前访问路径 | 是否正确 | 说明 |
|------|-------------|---------|------|
| 项目编号 | `registration.id` | ✅ | 正确 |
| 项目名称 | `registration.projectName` | ✅ | 正确 |
| **医疗机构** | `registration.institutionName` | ❌ | 应改为 `institution.name` |
| **机构等级** | `registration.institutionLevel` | ❌ | 应改为 `institution.level` |
| 竞赛组别 | `registration.groupType` | ✅ | 正确 |
| 状态 | `registration.status` | ✅ | 正确 |
| 报名人 | `registration.applicantName` | ⚠️ | 字段可能不存在 |
| 提交时间 | `registration.submittedAt` | ✅ | 正确 |

---

## 🔍 为什么组委会页面正常？

### 组委会书审页面

**文件：** `src/views/committee/book/Registration.vue`

**详情显示（第304-311行）：**
```vue
<el-descriptions-item label="医疗机构名称">
  {{ currentDetail.institution.name }}     ← 正确访问
</el-descriptions-item>
<el-descriptions-item label="机构等级">
  <el-tag v-if="currentDetail.institution.level" type="success">
    {{ currentDetail.institution.level }}  ← 正确访问
  </el-tag>
</el-descriptions-item>
```

**原因：** 组委会页面使用了正确的字段路径 `institution.name` 和 `institution.level`

---

## 📋 总结

### ✅ 核查结论

1. **后端API完全正常** ✅
   - 详情API正确返回了 `institution` 对象
   - 包含 `name` 和 `level` 字段
   - 数据完整无误

2. **前端代码字段路径错误** ❌
   - OPS页面使用了错误的字段访问路径
   - 应该访问 `institution.name` 而不是 `registration.institutionName`
   - 应该访问 `institution.level` 而不是 `registration.institutionLevel`

### 🔧 修复建议

**修改文件：** `src/views/ops/Registrations.vue`

**修改行数：** 第226-230行

**修改内容：**
- 将 `registration?.institutionName` 改为 `institution?.name`
- 将 `registration?.institutionLevel` 改为 `institution?.level`

**参考：** 组委会页面的实现方式（`src/views/committee/book/Registration.vue` 第304-311行）

---

**问题根因：前端字段访问路径错误，后端API返回数据正常。** ✅
