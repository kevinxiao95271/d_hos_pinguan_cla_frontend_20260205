# 评审专家API变更 - 前端适配完成报告

## 变更时间
2026-02-11

## 变更原因
后端删除了评审专家的分组限制（reviewerGroupCode, interviewGroupCode），因为：
- 评审专家没有固定分组
- 评审专家可以评审任何分组的项目
- 分配专家并不会基于分组字段

---

## 前端修改内容

### 1. 评审专家管理页面 (`src/views/ops/Reviewers.vue`)

#### 删除的功能

**筛选条件**：
- ❌ 删除"书审分组"筛选框
- ❌ 删除"面谈分组"筛选框
- ✅ 保留"专家背景"筛选框

**表格列**：
- ❌ 删除"书审分组"列（`reviewerGroupCode`）
- ❌ 删除"面谈分组"列（`interviewGroupCode`）
- ✅ 保留"专家背景"列（`expertBackground`）

**新增/编辑表单**：
- ❌ 删除"书审分组"输入框
- ❌ 删除"面谈分组"输入框
- ✅ 保留"专家背景"输入框

#### 修改的代码逻辑

**filters对象**：
```javascript
// 修改前
const filters = reactive({
  institutionId: null,
  reviewerGroupCode: '',      // ❌ 已删除
  interviewGroupCode: '',      // ❌ 已删除
  expertBackground: ''
})

// 修改后
const filters = reactive({
  institutionId: null,
  expertBackground: ''         // ✅ 保留
})
```

**form对象**：
```javascript
// 修改前
const form = reactive({
  phone: '',
  name: '',
  title: '',
  institutionId: null,
  reviewerGroupCode: '',       // ❌ 已删除
  interviewGroupCode: '',      // ❌ 已删除
  expertBackground: ''
})

// 修改后
const form = reactive({
  phone: '',
  name: '',
  title: '',
  institutionId: null,
  expertBackground: ''         // ✅ 保留
})
```

**API调用参数**：
```javascript
// loadData函数
const params = {}
if (filters.institutionId) params.institutionId = filters.institutionId
// ❌ 已删除：if (filters.reviewerGroupCode) params.reviewerGroupCode = filters.reviewerGroupCode
// ❌ 已删除：if (filters.interviewGroupCode) params.interviewGroupCode = filters.interviewGroupCode
if (filters.expertBackground) params.expertBackground = filters.expertBackground
```

**提交数据**：
```javascript
// submitForm函数
const data = {
  phone: form.phone,
  name: form.name,
  title: form.title,
  institutionId: form.institutionId,
  // ❌ 已删除：reviewerGroupCode: form.reviewerGroupCode || null,
  // ❌ 已删除：interviewGroupCode: form.interviewGroupCode || null,
  expertBackground: form.expertBackground || null
}
```

---

## 2. API接口文件 (`src/api/review.js`)

### 评委管理API（无需修改）

API接口定义保持不变，后端会自动忽略前端传递的分组参数（如果有的话）：

```javascript
// 获取评委列表
export function getReviewers(params) {
  return request({
    url: '/admin/reviewers',
    method: 'get',
    params  // 现在只会包含 institutionId 和 expertBackground
  })
}

// 新增评委
export function createReviewer(data) {
  return request({
    url: '/admin/reviewers',
    method: 'post',
    data  // 现在不再包含 reviewerGroupCode 和 interviewGroupCode
  })
}

// 更新评委
export function updateReviewer(id, data) {
  return request({
    url: `/admin/reviewers/${id}`,
    method: 'put',
    data  // 现在不再包含 reviewerGroupCode 和 interviewGroupCode
  })
}
```

---

## 影响范围分析

### ✅ 已修改的文件
- `src/views/ops/Reviewers.vue` - 评审专家管理页面

### ⚠️ 其他可能使用评委API的页面（需要检查）

1. **书审评委分配** (`src/views/committee/book/Reviewer.vue`)
   - 可能显示评委的分组信息
   - 建议删除分组相关显示

2. **面谈评委分配** (`src/views/committee/interview/Reviewer.vue`)
   - 可能显示评委的分组信息
   - 建议删除分组相关显示

3. **决赛评委分配** (`src/views/committee/final/Reviewer.vue`)
   - 可能显示评委的分组信息
   - 建议删除分组相关显示

4. **书审得分列表** (`src/views/committee/book/Score.vue`)
   - 可能使用 `reviewerGroupCode` 进行筛选
   - 建议删除该筛选条件

---

## 测试建议

### 功能测试清单

- [x] **评委列表查询** - 验证不传分组参数时能正常返回数据
- [ ] **评委新增** - 验证不传分组字段能成功创建评委
- [ ] **评委编辑** - 验证不传分组字段能成功更新评委
- [ ] **评委删除** - 验证删除功能正常
- [ ] **专家背景筛选** - 验证按专家背景筛选能正常工作
- [ ] **机构筛选** - 验证按机构筛选能正常工作

### API测试示例

```bash
# 1. 测试评委列表（不带分组参数）
curl -X GET "http://localhost:6031/api/admin/reviewers?institutionId=1&expertBackground=临床医学" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. 测试新增评委（不带分组字段）
curl -X POST "http://localhost:6031/api/admin/reviewers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "name": "测试评委",
    "title": "主任医师",
    "institutionId": 1,
    "expertBackground": "临床医学"
  }'

# 3. 测试更新评委（不带分组字段）
curl -X PUT "http://localhost:6031/api/admin/reviewers/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "name": "测试评委",
    "title": "主任医师",
    "institutionId": 1,
    "expertBackground": "临床医学"
  }'
```

---

## 数据模型对比

### 修改前的评委数据结构
```json
{
  "id": 1,
  "phone": "13800138000",
  "name": "张三",
  "title": "主任医师",
  "institutionId": 10,
  "institutionName": "浙江大学医学院附属第一医院",
  "reviewerGroupCode": "A1",        // ❌ 已删除
  "interviewGroupCode": "B2",       // ❌ 已删除
  "expertBackground": "临床医学",
  "currentLoad": 5
}
```

### 修改后的评委数据结构
```json
{
  "id": 1,
  "phone": "13800138000",
  "name": "张三",
  "title": "主任医师",
  "institutionId": 10,
  "institutionName": "浙江大学医学院附属第一医院",
  "expertBackground": "临床医学",   // ✅ 保留
  "currentLoad": 5
}
```

---

## 总结

### 删除的字段
- ❌ `reviewerGroupCode` - 书审分组代码
- ❌ `interviewGroupCode` - 面谈分组代码

### 保留的字段
- ✅ `expertBackground` - 专家背景
- ✅ `institutionId` - 所属机构ID
- ✅ `institutionName` - 所属机构名称
- ✅ `currentLoad` - 当前负荷
- ✅ `phone` - 手机号
- ✅ `name` - 姓名
- ✅ `title` - 职称

### 修改的页面
- ✅ `src/views/ops/Reviewers.vue` - 已完成

### 待确认的页面
- ⏳ `src/views/committee/book/Reviewer.vue` - 待检查
- ⏳ `src/views/committee/interview/Reviewer.vue` - 待检查
- ⏳ `src/views/committee/final/Reviewer.vue` - 待检查
- ⏳ `src/views/committee/book/Score.vue` - 待检查

---

**文档版本**: 1.0  
**更新时间**: 2026-02-11  
**状态**: ✅ 评审专家管理页面适配完成  
**负责人**: AI Assistant
