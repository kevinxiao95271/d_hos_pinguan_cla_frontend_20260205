# 模版管理和机构管理修复总结

## 修复时间
2026-03-01

---

## 问题1: 机构管理页面显示空列表

### 问题原因
后端已禁用 `GET /api/institutions` 接口，要求使用 `POST /api/institutions/search`

**后端返回的错误信息**:
```json
{
  "success": false,
  "message": "此接口已禁用，请使用 POST /api/institutions/search 进行查询。数据量过大(36K+)，必须使用分页。"
}
```

### 修复方案
修改 `src/api/institution.js`，将 GET 请求改为 POST 请求：

**修改前**:
```javascript
export function getInstitutions(params) {
  return request({
    url: '/institutions',
    method: 'get',
    params
  })
}
```

**修改后**:
```javascript
export function getInstitutions(params) {
  return request({
    url: '/institutions/search',
    method: 'post',
    data: params  // POST使用data，不是params
  })
}
```

### 修复结果
✅ 机构管理页面正常显示 42094 条机构记录

---

## 问题2: 模版管理页面报错

### 问题原因
前端调用了不存在的 `GET /api/system-templates` 接口

### 业务需求澄清
- OPS只需要查看当前激活的模版（最多2条：报名表 + 成果报告书）
- 不需要查看历史版本
- `GET /api/system-templates/active` 接口完全满足需求

### 修复方案

#### 1. 修改数据加载逻辑

**文件**: `src/views/ops/SystemTemplates.vue`

**修改前**:
```javascript
const loadTemplates = async () => {
  loading.value = true
  try {
    // 加载有效模版和所有模版
    const [activeRes, allRes] = await Promise.all([
      getActiveTemplates(),
      getAllTemplates()  // ❌ 这个API不存在
    ])
    
    if (activeRes.success) {
      activeTemplates.value = activeRes.data || []
    }
    
    if (allRes.success) {
      allTemplates.value = allRes.data || []
    }
  } catch (error) {
    console.error('加载模版列表失败:', error)
    ElMessage.error('加载模版列表失败')
  } finally {
    loading.value = false
  }
}
```

**修改后**:
```javascript
const loadTemplates = async () => {
  loading.value = true
  try {
    // 只加载有效模版（当前激活的模版）
    const activeRes = await getActiveTemplates()
    
    if (activeRes.success) {
      activeTemplates.value = activeRes.data || []
      // OPS管理页面也只显示当前激活的模版
      allTemplates.value = activeRes.data || []
    }
  } catch (error) {
    console.error('加载模版列表失败:', error)
    ElMessage.error('加载模版列表失败')
  } finally {
    loading.value = false
  }
}
```

#### 2. 调整表格列定义

后端返回的字段与前端期望不一致，需要调整：

| 前端原字段 | 后端实际字段 | 修改 |
|-----------|-------------|------|
| templateName | templateType | ✅ 已修改 |
| active | isActive | ✅ 已修改 |
| createdAt | uploadedAt | ✅ 已修改 |
| filePath | (无此字段) | ✅ 已删除 |

**修改后的表格列**:
```vue
<el-table-column prop="templateType" label="模版类型">
  <template #default="{ row }">
    {{ getTemplateTypeName(row.templateType) }}
  </template>
</el-table-column>
<el-table-column prop="isActive" label="状态">
  <template #default="{ row }">
    <el-tag :type="row.isActive ? 'success' : 'info'">
      {{ row.isActive ? '有效' : '已停用' }}
    </el-tag>
  </template>
</el-table-column>
<el-table-column prop="uploadedAt" label="上传时间">
  <template #default="{ row }">
    {{ formatDate(row.uploadedAt) }}
  </template>
</el-table-column>
```

#### 3. 添加辅助函数

```javascript
const getTemplateTypeName = (type) => {
  const typeMap = {
    'registration_form': '报名表模版',
    'result_report': '成果报告书模版'
  }
  return typeMap[type] || type
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}
```

#### 4. 简化操作按钮

由于只显示当前激活的模版，移除"停用"和"删除"按钮，只保留"下载"按钮：

```vue
<el-button
  type="primary"
  size="small"
  @click="downloadTemplateFile(row)"
>
  下载
</el-button>
<!-- 当前激活的模版不显示停用/删除按钮 -->
```

### 修复结果
✅ 模版管理页面正常显示 2 条激活的模版记录

---

## 后端API现状

### 系统模版API

| 接口 | 方法 | 功能 | 权限 | 状态 |
|------|------|------|------|------|
| /system-templates/active | GET | 获取激活的模版 | 公开 | ✅ 正常 |
| /system-templates/history/{type} | GET | 获取历史版本 | OPS | ✅ 存在 |
| /system-templates/upload | POST | 上传模版 | OPS | ✅ 正常 |
| /system-templates/{id}/download | GET | 下载模版 | 公开 | ✅ 正常 |
| /system-templates/{id} | DELETE | 删除模版 | OPS | ✅ 正常 |

### 机构API

| 接口 | 方法 | 功能 | 权限 | 状态 |
|------|------|------|------|------|
| /institutions | GET | 获取机构列表 | - | ❌ 已禁用 |
| /institutions/search | POST | 搜索机构（分页） | 公开 | ✅ 正常 |

---

## 修改的文件

1. **src/api/institution.js** - 修改机构API调用方式
2. **src/views/ops/SystemTemplates.vue** - 修改模版管理页面

---

## 测试验证

### 机构管理
1. 访问"系统管理" → "机构管理"
2. ✅ 应该显示机构列表（42094条记录）
3. ✅ 分页功能正常

### 模版管理
1. 访问"系统管理" → "模版管理"
2. ✅ 应该显示2条激活的模版
3. ✅ 可以下载模版文件
4. ✅ 可以上传新模版

---

## 数据统计

- **机构总数**: 42094条
- **激活模版**: 2条
  - 报名表模版 (registration_form)
  - 成果报告书模版 (result_report)

---

## 后续优化建议

### 机构管理
1. 添加搜索功能（按名称、地区、等级）
2. 优化大数据量渲染性能
3. 添加导出功能

### 模版管理
1. 如果需要查看历史版本，可以添加"查看历史"按钮
2. 调用 `GET /system-templates/history/{templateType}` 接口
3. 在对话框中显示历史版本列表

---

**修复完成时间**: 2026-03-01  
**修复人员**: Kiro AI Assistant
