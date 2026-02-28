# Minio文件管理功能 - 前端改动评估报告

**评估时间：** 2026-02-27  
**后端状态：** 准备集成Minio（尚未完成）  
**本报告：** 仅评估，不做代码改动

---

## 📋 需求概述

### 功能需求

1. **文件上传（参赛者）：**
   - 报名表（必填）
   - 成果说明书（必填）
   - 佐证材料（多个文件，可选）

2. **文件查看权限：**
   - **评审专家：** 可查看，仅预览不下载
   - **参赛者：** 可查看自己的，仅预览不下载
   - **组委会管理员：** 可查看，不支持批量下载
   - **系统运维（OPS）：** 可查看，不支持批量下载

3. **UX要求：**
   - 列表页一键预览文件
   - 不跳转详情页，直接在列表点击预览
   - 新标签页方式打开预览
   - 禁用下载功能

---

## 🎯 前端改动评估

### 一、组件开发（核心工作量）

#### 1. 文件上传组件 `FileUploadGroup.vue`

**位置：** `src/components/FileUploadGroup.vue`

**功能：**
- 支持多文件上传
- 文件格式限制（PDF、Word、Excel、图片等）
- 文件大小限制（单个10MB，总计50MB等）
- 上传进度显示
- 文件列表展示（已上传文件）
- 删除已上传文件
- 必填/可选文件提示

**技术选型：**
```javascript
// 基于 Element Plus Upload 组件
- el-upload（文件选择和上传）
- axios（上传请求，支持进度）
- 可能需要分片上传（大文件）
```

**预估工作量：** ⏱️ **2-3天**

---

#### 2. 文件预览组件 `FilePreviewDialog.vue`

**位置：** `src/components/FilePreviewDialog.vue`

**功能：**
- 在线预览PDF、Word、Excel、PPT、图片
- 新标签页打开预览
- 禁用下载按钮（通过样式和权限控制）
- 预览失败时的友好提示
- 支持多种预览方式：
  - 直接预览（PDF、图片）
  - Office在线预览（Word、Excel、PPT）
  - 第三方预览服务集成

**技术选型：**
```javascript
// 方案1：使用第三方预览库（推荐）
- pdf.js（PDF预览）
- vue-office（Office文档预览）
- viewer.js（图片预览）

// 方案2：使用在线预览服务
- Office Online Viewer
- Google Docs Viewer
- 自建预览服务

// 方案3：新标签页直接打开（简单但功能受限）
- window.open(fileUrl, '_blank')
- 依赖浏览器原生支持
```

**预估工作量：** ⏱️ **3-4天**（含预览库集成和调试）

---

#### 3. 列表内文件图标组件 `FileIconButton.vue`

**位置：** `src/components/FileIconButton.vue`

**功能：**
- 文件图标+文件名显示
- 点击直接预览
- 文件类型识别（图标不同）
- 多文件时显示数量
- Tooltip提示

**预估工作量：** ⏱️ **0.5天**

---

### 二、页面改动（主要改动点）

#### 1. 参赛者 - 报名表单页 ⭐⭐⭐

**文件：** `src/views/contestant/RegisterForm.vue`

**现状：**
- 步骤5"材料上传"已存在
- 目前是空的 `<el-upload>` 占位

**需要改动：**
```vue
<!-- 步骤5: 材料上传 -->
<div v-show="currentStep === 4">
  <!-- 1. 报名表上传（必填）-->
  <FileUploadGroup
    v-model="form.materials.applicationForm"
    label="报名表"
    :required="true"
    :limit="1"
    accept=".pdf,.doc,.docx"
    :max-size="10"
  />
  
  <!-- 2. 成果说明书上传（必填）-->
  <FileUploadGroup
    v-model="form.materials.achievementDoc"
    label="成果说明书"
    :required="true"
    :limit="1"
    accept=".pdf,.doc,.docx"
    :max-size="10"
  />
  
  <!-- 3. 佐证材料上传（可选，多个）-->
  <FileUploadGroup
    v-model="form.materials.supportingDocs"
    label="佐证材料"
    :required="false"
    :limit="10"
    accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.png"
    :max-size="10"
  />
</div>
```

**改动内容：**
- 引入 `FileUploadGroup` 组件
- 添加 `form.materials` 数据结构
- 实现上传API调用
- 添加表单验证（必填项）
- 保存草稿时保存文件列表
- 提交时验证文件完整性

**预估工作量：** ⏱️ **1天**

---

#### 2. 参赛者 - 我的报名列表页 ⭐⭐⭐

**文件：** `src/views/contestant/MyRegistrations.vue`

**需要改动：**
```vue
<el-table-column label="材料" width="120">
  <template #default="{ row }">
    <FileIconButton
      :files="row.materials"
      @preview="handlePreview"
    />
  </template>
</el-table-column>
```

**改动内容：**
- 表格增加"材料"列
- 引入 `FileIconButton` 组件
- 实现 `handlePreview` 方法（调用预览组件）
- API返回数据需要包含文件列表

**预估工作量：** ⏱️ **0.5天**

---

#### 3. 评审专家 - 任务列表页 ⭐⭐⭐

**文件：** `src/views/reviewer/Tasks.vue`

**需要改动：**
```vue
<el-table-column label="报名材料" width="120">
  <template #default="{ row }">
    <FileIconButton
      :files="row.materials"
      @preview="handlePreview"
    />
  </template>
</el-table-column>
```

**改动内容：**
- 同参赛者列表页
- 权限控制：只能预览，不能下载

**预估工作量：** ⏱️ **0.5天**

---

#### 4. 评审专家 - 评审详情页 ⭐⭐

**文件：** `src/views/reviewer/Review.vue`

**需要改动：**
```vue
<!-- 项目材料区域 -->
<el-card class="materials-section">
  <template #header>
    <span>报名材料</span>
  </template>
  
  <el-descriptions :column="1">
    <el-descriptions-item label="报名表">
      <FileIconButton
        :files="[registration.applicationForm]"
        @preview="handlePreview"
      />
    </el-descriptions-item>
    <el-descriptions-item label="成果说明书">
      <FileIconButton
        :files="[registration.achievementDoc]"
        @preview="handlePreview"
      />
    </el-descriptions-item>
    <el-descriptions-item label="佐证材料">
      <FileIconButton
        :files="registration.supportingDocs"
        @preview="handlePreview"
      />
    </el-descriptions-item>
  </el-descriptions>
</el-card>
```

**改动内容：**
- 添加材料展示区域
- 引入 `FileIconButton` 组件
- 实现预览功能

**预估工作量：** ⏱️ **0.5天**

---

#### 5. 组委会 - 书审分组列表页 ⭐⭐

**文件：** `src/views/committee/book/Registration.vue`

**需要改动：**
- 同评审专家任务列表页
- 表格增加"材料"列

**预估工作量：** ⏱️ **0.5天**

---

#### 6. 组委会 - 面谈分组列表页 ⭐⭐

**文件：** `src/views/committee/interview/Group.vue`

**需要改动：**
- 同书审分组列表页

**预估工作量：** ⏱️ **0.5天**

---

#### 7. 组委会 - 入围管理列表页 ⭐⭐

**文件：** `src/views/committee/interview/Shortlist.vue`

**需要改动：**
- 同书审分组列表页

**预估工作量：** ⏱️ **0.5天**

---

#### 8. OPS - 系统管理相关页面 ⭐

**文件：** `src/views/ops/*.vue`（如果需要查看报名材料）

**需要改动：**
- 根据具体需求添加文件查看功能

**预估工作量：** ⏱️ **0.5天**（如需要）

---

### 三、API 集成

#### 1. 文件上传 API

**新增 API 方法：** `src/api/file.js`

```javascript
// 上传单个文件
export function uploadFile(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request({
    url: '/api/files/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: onProgress
  })
}

// 批量上传文件
export function uploadFiles(files, type, registrationId) {
  // ...
}

// 删除文件
export function deleteFile(fileId) {
  return request({
    url: `/api/files/${fileId}`,
    method: 'delete'
  })
}

// 获取文件列表
export function getFilesByRegistration(registrationId) {
  return request({
    url: `/api/files/registration/${registrationId}`,
    method: 'get'
  })
}

// 获取文件预览URL
export function getFilePreviewUrl(fileId) {
  return request({
    url: `/api/files/${fileId}/preview`,
    method: 'get'
  })
}
```

**预估工作量：** ⏱️ **0.5天**

---

#### 2. 修改现有 API 返回

**需要后端配合：**

所有返回报名数据的API，需要增加文件信息：

```javascript
// 示例：报名详情API返回
{
  "success": true,
  "data": {
    "id": 123,
    "projectName": "项目名称",
    // ... 其他字段
    "materials": {
      "applicationForm": {
        "id": "file_001",
        "name": "报名表.pdf",
        "url": "http://minio.../preview/file_001",
        "size": 1024000,
        "uploadedAt": "2026-02-27T10:00:00"
      },
      "achievementDoc": {
        "id": "file_002",
        "name": "成果说明书.docx",
        "url": "http://minio.../preview/file_002",
        "size": 2048000,
        "uploadedAt": "2026-02-27T10:05:00"
      },
      "supportingDocs": [
        {
          "id": "file_003",
          "name": "佐证材料1.pdf",
          "url": "http://minio.../preview/file_003",
          "size": 512000,
          "uploadedAt": "2026-02-27T10:10:00"
        }
        // ... 更多文件
      ]
    }
  }
}
```

**影响的API：**
- `GET /api/registrations/{id}` - 报名详情
- `GET /api/registrations/my` - 我的报名列表
- `GET /api/reviewer/tasks` - 评审任务列表
- `GET /api/admin/registrations/filter` - 组委会报名列表
- 等等...

**预估工作量：** ⏱️ **协调后端，前端适配 0.5天**

---

### 四、工具函数和权限控制

#### 1. 文件类型识别工具

**文件：** `src/utils/fileHelper.js`

```javascript
// 获取文件图标
export function getFileIcon(fileName) {
  const ext = fileName.split('.').pop().toLowerCase()
  const iconMap = {
    'pdf': 'document',
    'doc': 'document',
    'docx': 'document',
    'xls': 'document',
    'xlsx': 'document',
    'ppt': 'document',
    'pptx': 'document',
    'jpg': 'picture',
    'jpeg': 'picture',
    'png': 'picture',
    'gif': 'picture'
  }
  return iconMap[ext] || 'document'
}

// 格式化文件大小
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 验证文件类型
export function validateFileType(file, acceptTypes) {
  // ...
}

// 验证文件大小
export function validateFileSize(file, maxSize) {
  // ...
}
```

**预估工作量：** ⏱️ **0.5天**

---

#### 2. 权限控制

**文件：** `src/utils/filePermission.js`

```javascript
// 检查文件下载权限
export function canDownloadFile(userRole) {
  // 所有角色都不能下载
  return false
}

// 检查文件预览权限
export function canPreviewFile(userRole, registrationId, currentUserId) {
  const role = userRole
  
  // 评审专家：可以预览分配给自己的任务的文件
  if (role === 'REVIEWER') {
    return true // 需要后端验证任务分配关系
  }
  
  // 参赛者：只能预览自己的
  if (role === 'CONTESTANT') {
    // 需要检查registrationId是否属于当前用户
    return true
  }
  
  // 组委会和OPS：可以预览所有
  if (role === 'COMMITTEE_ADMIN' || role === 'OPS') {
    return true
  }
  
  return false
}
```

**预估工作量：** ⏱️ **0.5天**

---

### 五、样式和用户体验

#### 1. 文件图标和样式

**文件：** `src/styles/file.scss`

```scss
// 文件图标样式
.file-icon {
  &.pdf { color: #ff4d4f; }
  &.doc, &.docx { color: #1890ff; }
  &.xls, &.xlsx { color: #52c41a; }
  &.image { color: #faad14; }
}

// 文件列表样式
.file-list {
  // ...
}

// 预览禁用下载的样式
.file-preview-no-download {
  iframe {
    pointer-events: none; // 可能需要根据具体情况调整
  }
}
```

**预估工作量：** ⏱️ **0.5天**

---

#### 2. 响应式设计

- 移动端文件列表展示优化
- 预览弹窗适配移动端

**预估工作量：** ⏱️ **0.5天**

---

## 📊 总工作量评估

### 按模块统计

| 模块 | 工作量 | 难度 | 优先级 |
|-----|-------|------|--------|
| **1. 文件上传组件** | 2-3天 | ⭐⭐⭐ | P0（最高）|
| **2. 文件预览组件** | 3-4天 | ⭐⭐⭐⭐ | P0（最高）|
| **3. 列表内文件图标组件** | 0.5天 | ⭐ | P1 |
| **4. 报名表单页改动** | 1天 | ⭐⭐ | P0（最高）|
| **5. 参赛者列表页改动** | 0.5天 | ⭐⭐ | P1 |
| **6. 评审专家任务列表页** | 0.5天 | ⭐⭐ | P0（最高）|
| **7. 评审详情页改动** | 0.5天 | ⭐⭐ | P0（最高）|
| **8. 组委会各列表页改动** | 1.5天 | ⭐⭐ | P1 |
| **9. OPS页面改动** | 0.5天 | ⭐ | P2 |
| **10. API集成** | 1天 | ⭐⭐ | P0（最高）|
| **11. 工具函数开发** | 1天 | ⭐⭐ | P1 |
| **12. 样式和UX优化** | 1天 | ⭐⭐ | P2 |
| **13. 测试和调试** | 2天 | ⭐⭐⭐ | P0（最高）|
| **14. 文档编写** | 0.5天 | ⭐ | P2 |

**总计：** ⏱️ **15-17个工作日**（约3周）

---

### 按优先级统计

| 优先级 | 内容 | 工作量 |
|-------|------|--------|
| **P0（核心功能）** | 上传组件、预览组件、报名表单、评审页面、API集成、测试 | 10-12天 |
| **P1（重要功能）** | 各列表页改动、工具函数 | 3.5天 |
| **P2（次要功能）** | OPS页面、样式优化、文档 | 2天 |

---

## 🚧 技术难点和风险

### 1. 文件预览技术选型 ⭐⭐⭐⭐

**难点：**
- PDF预览相对简单（pdf.js）
- Office文档预览较复杂（Word、Excel、PPT）
- 需要考虑兼容性和性能

**解决方案：**
```javascript
// 方案A：前端预览库（推荐）
- pdf.js (PDF)
- vue-office (Office文档)
- 优点：用户体验好，不依赖外部服务
- 缺点：库体积大，可能影响加载速度

// 方案B：在线预览服务
- Office Online Viewer: https://view.officeapps.live.com/op/view.aspx?src={fileUrl}
- Google Docs Viewer: https://docs.google.com/viewer?url={fileUrl}
- 优点：无需前端处理，兼容性好
- 缺点：依赖外部服务，可能被墙，速度不稳定

// 方案C：后端转换（推荐）
- 后端将Office文档转换为PDF
- 前端统一使用pdf.js预览
- 优点：前端实现简单，预览体验一致
- 缺点：增加后端工作量
```

**推荐方案：** 方案C（后端转PDF + pdf.js）

---

### 2. 禁用下载功能 ⭐⭐⭐

**难点：**
- 浏览器原生预览很难完全禁止下载
- 用户可以通过开发者工具获取文件URL

**解决方案：**
```javascript
// 1. 前端限制（基础）
- 隐藏下载按钮
- CSS禁用右键菜单
- 使用 iframe 加载（限制操作）

// 2. 后端限制（核心）
- 文件URL加时效性Token
- URL只能预览，不能直接下载
- 水印标记（后端生成预览时添加用户信息水印）

// 3. 权限控制
- 后端检查用户权限
- 记录文件访问日志
```

**注意：** 完全防止下载是不可能的，只能增加难度。

---

### 3. 大文件上传 ⭐⭐⭐

**难点：**
- 文件可能很大（成果说明书可能几十MB）
- 网络不稳定时上传失败

**解决方案：**
```javascript
// 1. 分片上传
- 将大文件切分为小块（如2MB一块）
- 逐块上传，支持断点续传
- 使用库：vue-simple-uploader 或自己实现

// 2. 上传进度显示
- 实时显示上传进度
- 预估剩余时间

// 3. 失败重试
- 上传失败自动重试
- 提供手动重试按钮
```

---

### 4. 新标签页预览 ⭐⭐

**难点：**
- 新标签页打开时，如何保持登录状态
- 如何禁用下载

**解决方案：**
```javascript
// 方案1：使用Token URL
const previewUrl = `${fileUrl}?token=${userToken}&preview=true`
window.open(previewUrl, '_blank')

// 方案2：使用独立的预览页面
router.push({
  path: '/preview',
  query: { fileId: file.id }
})
// 然后在新标签页打开

// 方案3：使用弹窗
- 不新开标签页，使用全屏弹窗
- 用户体验可能稍差，但控制更好
```

---

### 5. 多种文件格式支持 ⭐⭐⭐

**需要支持的格式：**
- PDF ✅ (pdf.js)
- Word (.doc, .docx) ⚠️ (需要转换或使用vue-office)
- Excel (.xls, .xlsx) ⚠️ (需要转换或使用vue-office)
- PPT (.ppt, .pptx) ⚠️ (需要转换或使用vue-office)
- 图片 (.jpg, .png, .gif) ✅ (原生支持)

**建议：**
- 限制上传格式为PDF和图片
- 或者后端统一转换为PDF

---

## 📦 依赖库推荐

### 必需依赖

```json
{
  "dependencies": {
    "pdf.js-dist": "^3.11.174",  // PDF预览
    "vue-office": "^1.3.0",      // Office文档预览（如需要）
    "axios": "^1.6.0"            // 已有，用于上传
  }
}
```

### 可选依赖

```json
{
  "dependencies": {
    "vue-simple-uploader": "^0.7.6",  // 分片上传（如果需要）
    "viewer.js": "^1.11.6",           // 图片预览（如果需要更好的体验）
    "file-saver": "^2.0.5"            // 如果允许下载时使用（当前不需要）
  }
}
```

---

## 🔄 与后端对接清单

### 后端需要提供的API

| API | 方法 | 说明 | 优先级 |
|-----|------|------|--------|
| `/api/files/upload` | POST | 上传单个文件 | P0 |
| `/api/files/upload/batch` | POST | 批量上传文件 | P1 |
| `/api/files/{fileId}` | DELETE | 删除文件 | P0 |
| `/api/files/registration/{registrationId}` | GET | 获取报名的所有文件 | P0 |
| `/api/files/{fileId}/preview` | GET | 获取文件预览URL | P0 |
| `/api/files/{fileId}/info` | GET | 获取文件元信息 | P1 |

### 现有API需要修改

所有返回报名数据的API，需要增加 `materials` 字段：

- `GET /api/registrations/{id}`
- `GET /api/registrations/my`
- `GET /api/reviewer/tasks`
- `GET /api/admin/registrations/filter`
- `POST /api/registrations` (创建时保存文件ID)
- `PUT /api/registrations/{id}` (更新时更新文件)

### 后端需要处理的功能

1. **文件存储到Minio**
2. **文件访问权限控制**（重要！）
3. **文件预览URL生成**（带时效Token）
4. **文件格式转换**（Office → PDF，推荐）
5. **文件大小和格式验证**
6. **水印添加**（可选，防止截图传播）
7. **访问日志记录**（安全审计）

---

## 📋 实施建议

### 第一阶段：核心功能（P0，7-8天）

1. **组件开发（5天）：**
   - FileUploadGroup 组件（2天）
   - FilePreviewDialog 组件（3天）

2. **页面改动（2天）：**
   - RegisterForm.vue 报名表单（1天）
   - 评审专家任务列表和详情页（1天）

3. **API集成和测试（1天）**

### 第二阶段：扩展功能（P1，3-4天）

1. **列表页改动（2天）：**
   - 参赛者列表页
   - 组委会各列表页
   - FileIconButton 组件

2. **工具函数和权限控制（1天）**

3. **测试和调试（1天）**

### 第三阶段：完善和优化（P2，2天）

1. OPS页面（如需要）
2. 样式优化和响应式适配
3. 文档编写

---

## ⚠️ 注意事项

### 1. 用户体验

- ✅ 上传进度实时显示
- ✅ 上传失败友好提示
- ✅ 文件预览加载中状态
- ✅ 大文件上传优化（分片）
- ✅ 移动端适配

### 2. 安全性

- ✅ 文件类型和大小验证（前端+后端）
- ✅ 权限控制（后端为主）
- ✅ 防止XSS攻击（文件名过滤）
- ✅ 访问日志记录

### 3. 性能

- ✅ 图片压缩（上传前）
- ✅ 懒加载（文件列表）
- ✅ 缓存预览URL
- ✅ 按需加载预览库

### 4. 兼容性

- ✅ 测试主流浏览器（Chrome、Firefox、Safari、Edge）
- ✅ 移动端浏览器测试
- ⚠️ IE11不支持（可以不考虑）

---

## 📊 总结

### 工作量总结

| 项目 | 工作量 |
|-----|--------|
| **核心开发** | 10-12天 |
| **扩展功能** | 3-4天 |
| **完善优化** | 2天 |
| **总计** | **15-17天**（约3周）|

### 技术难度

- ⭐⭐⭐⭐ **文件预览（特别是Office文档）**
- ⭐⭐⭐ **禁用下载功能**
- ⭐⭐⭐ **大文件上传**
- ⭐⭐ **权限控制**
- ⭐⭐ **列表页改动**

### 推荐方案

1. **文件预览：** 后端转PDF + pdf.js（统一体验）
2. **文件上传：** Element Plus Upload + 自定义封装
3. **禁用下载：** 后端Token验证 + 前端UI限制
4. **新标签页预览：** 独立预览页面 + Token URL

### 风险提示

1. ⚠️ Office文档预览技术复杂，可能需要调整方案
2. ⚠️ 完全禁止下载不可能，只能增加难度
3. ⚠️ 需要后端密切配合，API设计很关键
4. ⚠️ 大文件上传可能需要分片技术

---

**评估完成时间：** 2026-02-27  
**评估人员：** 前端开发团队  
**状态：** ✅ 仅评估，等待后端Minio集成完成后再实施
