# OPS报名列表与文件预览 - 需求分析

**分析时间：** 2026-02-28  
**分析人员：** AI Assistant  
**状态：** ✅ 待确认

---

## 📝 需求概述

**目标：** 在系统管理（OPS）页面实现报名列表查看功能，包含文件预览按钮。

**核心功能：**
1. 显示所有报名项目的列表
2. 每个项目显示材料信息
3. 提供文件预览按钮
4. 支持筛选和搜索

---

## 🔍 现状分析

### 1. 现有API支持

#### ✅ 已有API（完全支持）

**报名列表API：**
- `filterRegistrations(params)` - `/admin/registrations/filter`
  - 用途：筛选报名列表（组委会在用）
  - 支持参数：competitionId, status, groupType, institutionName, projectName, methodLabel, groupCode
  - **返回数据包含materials字段** ✅
  
**报名详情API：**
- `getRegistration(id)` - `/registrations/{id}`
  - 用途：获取单个报名的详细信息
  - 返回完整的报名信息、成员、材料等

**材料下载API：**
- `downloadMaterial(materialId)` - `/materials/{materialId}/download`
  - 用途：下载材料文件
  - 返回：Blob文件流
  - 权限：已实现权限控制

**材料列表API：**
- `getMaterialsByRegistration(registrationId)` - `/materials/registration/{registrationId}`
  - 用途：获取某个报名的所有材料
  - 返回：材料列表数组

#### ❓ 文件预览支持情况

**现状：**
- ❌ 目前没有专门的预览API
- ✅ 下载API返回Blob，可用于预览
- ✅ 前端可以通过Blob创建URL进行预览

**可预览的文件类型：**
- ✅ PDF - 浏览器原生支持预览
- ✅ 图片 (JPG/PNG) - 浏览器原生支持预览
- ⚠️ Word (DOC/DOCX) - 需要下载或使用第三方服务
- ⚠️ 压缩包 (ZIP/RAR) - 需要下载，无法预览

---

### 2. 现有页面参考

#### 组委会书审报名列表页面
**文件：** `src/views/committee/book/Registration.vue`

**已实现功能：**
- ✅ 使用 `filterRegistrations` API获取列表
- ✅ 显示材料数量和状态
- ✅ 材料查看和下载功能
- ✅ 分页、筛选、搜索
- ✅ 详情弹窗显示材料列表

**材料显示方式：**
```vue
<!-- 列表页材料列 -->
<el-table-column label="材料" width="120">
  <template #default="{ row }">
    <div v-if="row.materials && row.materials.length > 0">
      <el-tag type="success" size="small">{{ row.materials.length }}个文件</el-tag>
      <el-button type="primary" size="small" link @click="viewMaterials(row)">
        查看
      </el-button>
    </div>
    <el-tag v-else type="info" size="small">无材料</el-tag>
  </template>
</el-table-column>

<!-- 详情弹窗中的材料表格 -->
<el-table :data="currentDetail.materials" border>
  <el-table-column prop="fileName" label="文件名" />
  <el-table-column prop="fileType" label="类型" width="100" />
  <el-table-column label="操作" width="120">
    <template #default="{ row }">
      <el-button type="primary" size="small" @click="downloadFile(row)">
        下载
      </el-button>
    </template>
  </el-table-column>
</el-table>
```

**下载实现：**
```javascript
const downloadFile = async (material) => {
  try {
    const blob = await downloadMaterial(material.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = material.fileName || '材料文件'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}
```

---

## 💡 实施方案

### 方案一：复用组委会页面逻辑（推荐）⭐

**思路：** 基于现有的组委会书审页面，为OPS创建一个类似的报名列表页面。

**优点：**
- ✅ API完全支持，无需后端改动
- ✅ 复用已验证的前端逻辑
- ✅ 开发速度快，风险低
- ✅ UI/UX一致性好

**实施步骤：**

1. **创建OPS报名列表页面**
   - 文件：`src/views/ops/Registrations.vue`
   - 复用组委会页面的核心逻辑
   - 去掉分组、分类等组委会特有功能
   - 保留筛选、搜索、分页功能

2. **添加文件预览功能**
   - 在材料操作列添加"预览"按钮
   - 根据文件类型选择预览方式：
     - PDF/图片：新窗口打开预览
     - Word/其他：提示下载

3. **添加路由**
   - 路径：`/ops/registrations`
   - 权限：OPS角色

4. **更新导航菜单**
   - 在OPS菜单中添加"报名列表"入口

---

### 方案二：增强预览功能（可选）

如果需要更强大的预览功能，可以考虑：

#### 选项A：使用浏览器原生预览

**实现方式：**
```javascript
const previewFile = async (material) => {
  const blob = await downloadMaterial(material.id)
  const url = window.URL.createObjectURL(blob)
  
  // 根据文件类型判断
  if (material.fileType === 'pdf' || material.fileName.endsWith('.pdf')) {
    // PDF直接在新窗口打开
    window.open(url, '_blank')
  } else if (['jpg', 'jpeg', 'png', 'gif'].some(ext => material.fileName.toLowerCase().endsWith(ext))) {
    // 图片在弹窗中显示
    showImagePreview(url)
  } else {
    // 其他文件提示下载
    ElMessage.info('该文件类型不支持预览，请下载后查看')
    downloadFile(material)
  }
}
```

**支持的文件类型：**
- ✅ PDF - 浏览器原生支持
- ✅ 图片 (JPG/PNG/GIF) - 使用Image或el-image-viewer
- ❌ Word - 不支持预览
- ❌ 压缩包 - 不支持预览

#### 选项B：使用第三方预览服务（需要额外开发）

**可选方案：**
1. Office文档预览：
   - Microsoft Office Online
   - Google Docs Viewer
   - 需要公网访问

2. 自建预览服务：
   - LibreOffice转换服务
   - PDF.js
   - 需要后端支持

**不推荐原因：**
- ⚠️ 需要额外的后端服务
- ⚠️ 增加系统复杂度
- ⚠️ 文件安全性问题
- ⚠️ 用户可以直接下载查看

---

## 📋 推荐的实施清单

### 第一阶段：基础报名列表（推荐立即实施）

**目标：** 让OPS能看到所有报名项目和材料

**任务清单：**
1. ✅ 创建 `src/views/ops/Registrations.vue`
   - 复用组委会页面布局
   - 实现列表展示、筛选、分页
   - 显示材料数量和状态

2. ✅ 添加材料查看功能
   - 点击"查看"显示详情弹窗
   - 弹窗中显示材料列表
   - 材料列表显示文件名、类型、大小

3. ✅ 添加材料下载功能
   - 复用现有downloadFile方法
   - 点击下载按钮下载文件

4. ✅ 添加路由和菜单
   - 路由：`/ops/registrations`
   - 菜单项："报名列表"

**预计工作量：** 2-3小时

---

### 第二阶段：文件预览（可选）

**目标：** 为支持的文件类型提供预览功能

**任务清单：**
1. ✅ 添加文件类型判断
   - 根据文件扩展名或MIME类型
   - 区分PDF、图片、其他

2. ✅ 实现PDF预览
   - 新窗口打开PDF
   - 或使用iframe嵌入预览

3. ✅ 实现图片预览
   - 使用el-image-viewer组件
   - 支持放大、缩小、旋转

4. ✅ 优化操作按钮
   - 可预览：显示"预览"+"下载"
   - 不可预览：只显示"下载"

**预计工作量：** 1-2小时

---

## 🎯 技术实现要点

### 1. 列表数据结构

**API返回的materials字段格式：**
```javascript
{
  "registrationId": 1,
  "projectName": "测试项目",
  "materials": [
    {
      "id": 456,
      "type": "registration_form",  // registration_form | result_report | evidence
      "fileName": "报名表.pdf",
      "fileSize": 102400,           // 字节
      "uploadedAt": "2026-02-27T10:00:00",
      "downloadUrl": "/api/materials/456/download"  // 可选
    }
  ]
}
```

### 2. 文件预览实现

**PDF预览：**
```javascript
const previewPDF = async (material) => {
  const blob = await downloadMaterial(material.id)
  const url = window.URL.createObjectURL(blob)
  window.open(url, '_blank')
  
  // 延迟释放URL（给浏览器时间加载）
  setTimeout(() => {
    window.URL.revokeObjectURL(url)
  }, 60000)
}
```

**图片预览：**
```javascript
import { ElImageViewer } from 'element-plus'

const previewImage = async (material) => {
  const blob = await downloadMaterial(material.id)
  const url = window.URL.createObjectURL(blob)
  
  // 使用el-image-viewer
  const viewer = ElImageViewer({
    urlList: [url],
    initialIndex: 0,
    hideOnClickModal: true
  })
}
```

### 3. 权限控制

**OPS角色权限：**
- ✅ 查看所有赛事的报名列表
- ✅ 查看和下载所有材料
- ✅ 不需要评审功能
- ✅ 只读，不修改报名状态

---

## ⚠️ 注意事项

### 1. 文件大小限制
- 后端限制：30MB
- 浏览器预览：建议<10MB的文件才预览
- 大文件提示用户下载

### 2. 文件类型支持
- PDF：完全支持预览
- 图片：完全支持预览
- Word：建议下载查看
- 压缩包：只能下载

### 3. 安全性
- 材料下载API已有权限控制
- OPS角色需要有查看所有材料的权限
- 预览时使用Blob URL，不暴露真实路径

### 4. 性能优化
- 列表只显示材料数量，不加载文件
- 点击查看时才加载材料详情
- 预览时显示加载提示
- 使用虚拟滚动处理大量数据

---

## 📊 API验证状态

| API | 路径 | 状态 | 说明 |
|-----|------|------|------|
| 报名列表 | `/admin/registrations/filter` | ✅ 已验证 | 包含materials字段 |
| 报名详情 | `/registrations/{id}` | ✅ 已验证 | 完整信息 |
| 材料下载 | `/materials/{id}/download` | ✅ 已验证 | 返回Blob |
| 材料列表 | `/materials/registration/{id}` | ✅ 可用 | 可选使用 |

**结论：** 所有必需的API都已经支持，无需后端改动。

---

## 🎨 UI设计建议

### 列表页面布局

```
┌────────────────────────────────────────────────────────┐
│ 报名列表管理                                            │
├────────────────────────────────────────────────────────┤
│ [赛事选择▼] [状态▼] [机构名称___] [项目名称___] [查询] │
├────────────────────────────────────────────────────────┤
│ 编号 │ 赛事  │ 项目名称 │ 机构    │ 材料  │ 状态 │ 操作 │
│ 001 │ 2026 │ XXX项目  │ XX医院  │ 3个   │ 已提交│ 查看│
│ 002 │ 2026 │ YYY项目  │ YY医院  │ 2个   │ 草稿  │ 查看│
├────────────────────────────────────────────────────────┤
│                    << 1 2 3 4 5 >>                     │
└────────────────────────────────────────────────────────┘
```

### 材料详情弹窗

```
┌──────────────────────────────────────────┐
│ 项目材料 - XXX项目                        │
├──────────────────────────────────────────┤
│ 文件名              │ 类型    │ 操作     │
│ 报名表.pdf         │ 报名表  │ [预览][下载]│
│ 成果报告.docx      │ 报告书  │ [下载]  │
│ 证明材料.zip       │ 佐证    │ [下载]  │
├──────────────────────────────────────────┤
│                          [关闭]           │
└──────────────────────────────────────────┘
```

---

## 📝 总结

### ✅ 现有条件
- API完全支持，无需后端改动
- 前端已有类似页面可参考
- 下载功能已验证可用
- 权限控制已实现

### 🎯 推荐方案
**方案一（推荐）：** 基础报名列表 + 简单预览
- 创建OPS报名列表页面
- 复用组委会页面逻辑
- 添加PDF/图片预览
- Word和压缩包提示下载

**优点：**
- 快速实现（2-3小时）
- 无需后端改动
- 满足基本需求
- 用户体验良好

### ❓ 待确认问题
1. ✅ 是否需要Word文档预览？（建议：不需要，提示下载即可）
2. ✅ 是否需要批量下载功能？（建议：可选，后续添加）
3. ✅ 是否需要材料上传时间、上传人等信息？（建议：在详情中显示）
4. ✅ 是否需要材料审核功能？（建议：不需要，OPS只查看）

---

**分析完成，等待用户确认后开始实施。**
