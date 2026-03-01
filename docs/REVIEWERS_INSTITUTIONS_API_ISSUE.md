# 评审专家管理页面 - 机构列表加载错误分析

## 错误信息
```
Reviewers.vue:169 加载机构列表失败: AxiosError: Request failed with status code 400
at settle (axios.js?v=d7925996:1267:12)
at XMLHttpRequest.onloadend (axios.js?v=d7925996:1616:7)
at Axios.request (axios.js?v=d7925996:2233:41)
at async loadInstitutions (Reviewers.vue:164:17)
```

**页面位置**: `src/views/ops/Reviewers.vue`  
**错误行**: 第164-169行的 `loadInstitutions()` 函数  
**影响**: 报错但不影响页面数据展示（评委列表正常）

---

## 问题分析

### 1. 前端调用代码
**文件**: `src/views/ops/Reviewers.vue` (第164行)

```javascript
// 加载机构列表
const loadInstitutions = async () => {
  try {
    const res = await getInstitutions()  // ❌ 没有传递任何参数
    if (res.success && res.data) {
      institutions.value = res.data
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  }
}
```

**问题**: 调用 `getInstitutions()` 时没有传递任何参数

---

### 2. API实现
**文件**: `src/api/institution.js`

```javascript
/**
 * 获取机构列表
 * 注意：后端已将此接口改为POST方式，使用/search端点
 * 原因：数据量过大(42K+)，必须使用分页查询
 */
export function getInstitutions(params) {
  return request({
    url: '/institutions/search',
    method: 'post',
    data: params  // POST使用data，不是params
  })
}
```

**实际请求**:
- 端点: `POST /institutions/search`
- 请求体: `undefined` (因为没有传参数)

---

### 3. 后端行为推测

根据之前的经验（用户管理页面的问题），后端可能：

1. **不接受空对象或undefined**
   - 当请求体为空时，返回 400 Bad Request
   - 需要明确的参数，即使是空查询条件

2. **需要分页参数**
   - 数据量过大(42K+机构)
   - 可能强制要求分页参数: `page`, `size`

3. **参数验证严格**
   - 后端可能对请求体格式有严格验证
   - 空请求体触发参数校验失败

---

## 与其他页面的对比

### 机构管理页面 (已修复)
**文件**: `src/views/ops/Institutions.vue`

```javascript
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage - 1,
      size: pagination.pageSize
    }
    
    // 添加筛选条件
    if (filters.name) params.name = filters.name
    if (filters.region) params.region = filters.region
    if (filters.level) params.level = filters.level
    
    const res = await getInstitutions(params)  // ✅ 传递了完整参数
    // ...
  }
}
```

**差异**:
- 机构管理页面传递了完整的分页参数和筛选条件
- 评审专家管理页面没有传递任何参数

---

## 为什么页面仍然正常工作？

### 评委列表独立加载
```javascript
// 评委列表使用不同的API
const loadData = async () => {
  const res = await getReviewers(params)  // ✅ 使用评委API，不依赖机构列表
  // ...
}
```

### 机构列表仅用于下拉选择
```vue
<!-- 筛选条件中的机构选择器 -->
<el-select v-model="filters.institutionId">
  <el-option
    v-for="inst in institutions"
    :key="inst.id"
    :label="inst.name"
    :value="inst.id"
  />
</el-select>

<!-- 新增/编辑对话框中的机构选择器 -->
<el-select v-model="form.institutionId">
  <el-option
    v-for="inst in institutions"
    :key="inst.id"
    :label="inst.name"
    :value="inst.id"
  />
</el-select>
```

**影响**:
- 机构下拉列表为空（`institutions.value = []`）
- 但评委列表中的 `institutionName` 字段由后端直接返回
- 用户可以查看评委列表，但无法通过机构筛选
- 新增/编辑评委时无法选择机构

---

## 根本原因

**与用户管理页面相同的问题**:
1. 后端不接受空参数或undefined
2. 前端调用API时没有传递必要的参数
3. 后端返回 400 Bad Request

**之前的修复方案** (用户管理页面):
```javascript
// 修复前
const res = await getUsers({ phone: "", name: "", role: "" })  // ❌ 空字符串

// 修复后
const params = {}
if (searchForm.phone) params.phone = searchForm.phone
if (searchForm.name) params.name = searchForm.name
if (searchForm.role) params.role = searchForm.role
const res = await getUsers(params)  // ✅ 只传非空字段
```

---

## 解决方案

### 方案1: 传递空对象（最简单）
```javascript
const loadInstitutions = async () => {
  try {
    const res = await getInstitutions({})  // 传递空对象
    if (res.success && res.data) {
      institutions.value = res.data
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  }
}
```

**优点**: 改动最小  
**缺点**: 可能返回全部42K+机构，性能问题

---

### 方案2: 传递分页参数（推荐）
```javascript
const loadInstitutions = async () => {
  try {
    const res = await getInstitutions({
      page: 0,
      size: 10000  // 获取足够多的机构用于下拉选择
    })
    if (res.success && res.data) {
      // 处理分页响应
      if (Array.isArray(res.data)) {
        institutions.value = res.data
      } else if (res.data.content) {
        institutions.value = res.data.content
      }
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  }
}
```

**优点**: 符合后端分页要求  
**缺点**: 需要处理分页响应格式

---

### 方案3: 使用专门的下拉列表API（最佳）
如果后端提供了专门的机构下拉列表API（不分页，返回简化数据）：

```javascript
const loadInstitutions = async () => {
  try {
    const res = await getInstitutionsForSelect()  // 假设有这个API
    if (res.success && res.data) {
      institutions.value = res.data
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  }
}
```

**优点**: 
- 性能最好
- 只返回必要字段（id, name）
- 不需要分页

**缺点**: 需要后端新增API

---

## 测试建议

### 1. 测试空对象请求
```bash
curl -X POST http://localhost:8080/api/institutions/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{}'
```

### 2. 测试分页请求
```bash
curl -X POST http://localhost:8080/api/institutions/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"page": 0, "size": 100}'
```

### 3. 观察响应格式
- 是否返回数组？
- 是否返回分页对象（content, totalElements, totalPages）？
- 是否包含完整机构信息？

---

## 后续影响

### 当前受影响的功能
1. ❌ 按机构筛选评委（下拉列表为空）
2. ❌ 新增评委时选择机构（下拉列表为空）
3. ❌ 编辑评委时选择机构（下拉列表为空）
4. ✅ 查看评委列表（正常，institutionName由后端返回）

### 修复后的效果
1. ✅ 机构下拉列表正常显示
2. ✅ 可以按机构筛选评委
3. ✅ 新增/编辑评委时可以选择机构

---

## 建议

### 短期方案
1. 先测试传递空对象 `{}` 是否可行
2. 如果不行，传递分页参数 `{ page: 0, size: 10000 }`
3. 处理分页响应格式

### 长期方案
1. 建议后端提供专门的下拉列表API
2. 只返回必要字段，提升性能
3. 考虑添加机构搜索功能（输入提示）

---

**分析时间**: 2026-03-01  
**分析人员**: Kiro AI Assistant  
**状态**: 待修复
