# 客户端筛选方案说明

## 🔴 后端接口问题

`/api/registrations` 接口的限制：
1. ❌ **不返回品管工具字段**（methodCode/methodLabel 为 null）
2. ❌ **不返回机构名称**（institutionName 为 null）
3. ❌ **不返回项目编号**（registrationId 为 null）
4. ❌ **不返回报名人**（applicantName 为 null）
5. ❌ **不支持任何筛选参数**（传什么都返回全部数据）

## ✅ 已实施的解决方案

### 1. 客户端筛选

**修改位置：** `src/views/committee/BookStage.vue`

**实现方式：**
- 一次性获取所有数据（只传 `competitionId`）
- 在前端进行筛选（组别、分组、项目名称）
- 动态从实际数据中提取可用的 `groupCode`（A1, A2, B1, B2）

**代码：**
```javascript
// 存储所有数据
const allRegistrations = ref([])

// 加载时获取全部数据
const loadRegistrations = async () => {
  const res = await getRegistrations({
    competitionId: registrationFilters.competitionId
  })
  allRegistrations.value = res.data || []
  applyClientFilters()
}

// 客户端筛选
const applyClientFilters = () => {
  let filtered = [...allRegistrations.value]
  
  if (registrationFilters.groupType) {
    filtered = filtered.filter(item => item.groupType === registrationFilters.groupType)
  }
  
  if (registrationFilters.groupCode) {
    filtered = filtered.filter(item => item.groupCode === registrationFilters.groupCode)
  }
  
  if (registrationFilters.projectName) {
    const keyword = registrationFilters.projectName.toLowerCase()
    filtered = filtered.filter(item => 
      item.projectName && item.projectName.toLowerCase().includes(keyword)
    )
  }
  
  registrations.value = filtered
}

// 动态提取 groupCode
const groupCodes = computed(() => {
  const codes = new Set()
  allRegistrations.value.forEach(item => {
    if (registrationFilters.groupType) {
      if (item.groupType === registrationFilters.groupType && item.groupCode) {
        codes.add(item.groupCode)
      }
    } else {
      if (item.groupCode) {
        codes.add(item.groupCode)
      }
    }
  })
  return Array.from(codes).sort()
})
```

### 2. 暂时禁用的筛选

由于 `/api/registrations` 不返回这些字段，以下筛选暂时被注释掉：
- ❌ 医疗机构名称筛选
- ❌ 品管工具筛选

**恢复方法：** 后端修复 `/api/admin/registrations/filter` 的 401 问题后，取消注释这些筛选项。

### 3. 详情页面的品管工具显示

**问题：** 列表接口不返回 `methodLabel`，但详情接口 `GET /api/registrations/{id}` 会返回完整信息。

**解决方案：** 在详情页面中，需要调用详情接口获取完整数据，包括品管工具信息。

## 🧪 测试结果

### 可用的 groupCode
从实际数据中提取到：**A1, A2, B1, B2**

### 筛选效果
✅ 按组别筛选：BASIC / COMPREHENSIVE / ADVANCED  
✅ 按分组筛选：A1, A2, B1, B2（动态提取）  
✅ 按项目名称筛选：模糊匹配  
❌ 按机构名称筛选：需要完整接口  
❌ 按品管工具筛选：需要完整接口

## 📋 用户使用指南

### 筛选步骤

1. **按组别筛选**
   - 选择"基层组" / "综合组" / "进阶组"
   - 分组下拉会自动显示该组别的可用分组

2. **按分组筛选**
   - 先选择组别（或不选）
   - 从分组下拉中选择具体分组（A1, A2, B1, B2）

3. **按项目名称筛选**
   - 输入项目名称关键词
   - 支持模糊匹配

4. **点击"查询"**
   - 应用筛选条件
   - 显示符合条件的报名

5. **点击"重置"**
   - 清空所有筛选条件
   - 显示全部报名

### 详情查看

点击列表中的"详情"按钮，会调用详情接口获取完整信息，包括：
- 品管工具（methodCode / methodLabel）
- 医疗机构信息（institutionName）
- 报名人信息（applicantName）
- 项目摘要
- 活动说明
- 提交材料

## 🎯 后端修复后的恢复步骤

### 1. 修复 `/api/admin/registrations/filter` 的 401 问题

后端修复权限验证后，前端需要：

1. **恢复使用 admin 接口**
```javascript
import { filterRegistrations } from '@/api/admin'

const loadRegistrations = async () => {
  const res = await filterRegistrations(registrationFilters)
  registrations.value = res.data || []
}
```

2. **取消注释筛选项**
```vue
<!-- 恢复医疗机构名称筛选 -->
<el-form-item label="医疗机构名称">
  <el-input v-model="registrationFilters.institutionName" placeholder="请输入机构名称" clearable />
</el-form-item>

<!-- 恢复品管工具筛选 -->
<el-form-item label="品管工具">
  <el-select v-model="registrationFilters.methodCode" placeholder="全部" clearable>
    <el-option
      v-for="item in dictionaries.methods"
      :key="item.code"
      :label="item.label"
      :value="item.code"
    />
  </el-select>
</el-form-item>
```

3. **恢复表格列**
```vue
<el-table-column prop="registrationId" label="项目编号" width="140" />
<el-table-column prop="institutionName" label="医疗机构名称" min-width="160" />
<el-table-column prop="methodLabel" label="品管工具" min-width="140" />
<el-table-column prop="applicantName" label="报名人" width="100" />
```

4. **移除客户端筛选逻辑**
   - 删除 `allRegistrations` 变量
   - 删除 `applyClientFilters` 函数
   - 查询按钮改回 `@click="loadRegistrations"`

## 📝 更新日志

- **2026-02-06 22:30**: 实施客户端筛选方案
- **待后端修复**: `/api/admin/registrations/filter` 权限问题
