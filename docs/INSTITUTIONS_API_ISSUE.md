# 机构管理API问题报告

## 测试时间
2026-03-01 13:05

## 测试账号
- 手机号: 13800000005
- 角色: OPS（系统运维）

---

## 🔴 问题根源

### 后端API已变更，前端未同步更新

**后端返回的错误信息**:
```json
{
  "success": false,
  "data": null,
  "message": "此接口已禁用，请使用 POST /api/institutions/search 进行查询。数据量过大(36K+)，必须使用分页。"
}
```

**问题说明**:
- 后端已禁用 `GET /api/institutions` 接口
- 原因：数据量过大（42094条机构记录）
- 要求使用 `POST /api/institutions/search` 进行查询

---

## API测试结果

| API端点 | 方法 | 状态 | 说明 |
|---------|------|------|------|
| /institutions | GET | ❌ 已禁用 | 后端返回错误信息 |
| /institutions/search | POST | ✅ 正常 | 返回42094条记录 |

---

## 前端当前实现

**文件**: `src/views/ops/Institutions.vue`

**当前代码**:
```javascript
const loadData = async () => {
  try {
    const res = await getInstitutions(getPaginationParams())
    if (res.success) {
      institutions.value = extractDataList(res.data)
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  }
}
```

**API调用**: `src/api/institution.js`
```javascript
export function getInstitutions(params) {
  return request({
    url: '/institutions',  // ❌ 这个端点已被禁用
    method: 'get',
    params
  })
}
```

---

## ✅ 正确的API

### POST /api/institutions/search

**请求方式**: POST

**请求参数**:
```json
{
  "page": 0,
  "size": 50
}
```

**响应格式**:
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": 64067,
        "name": "三门县人民医院",
        "region": "三门县",
        "level": "三级",
        "usccLast4": "415D",
        "displayText": "三门县人民医院 (三门县) [三级]"
      }
    ],
    "totalElements": 42094,
    "totalPages": 842,
    "size": 50,
    "number": 0
  },
  "message": null
}
```

**数据统计**:
- 总记录数: 42094条
- 当前页记录数: 50条
- 总页数: 842页

---

## 🔧 前端修复方案

### 方案1: 修改API调用（推荐）

**修改文件**: `src/api/institution.js`

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
    data: params  // 注意：POST使用data，不是params
  })
}
```

**优点**:
- 只需修改一处
- 前端页面代码无需改动
- API接口名称保持不变

---

### 方案2: 使用现有的searchInstitutions函数

**修改文件**: `src/views/ops/Institutions.vue`

**修改前**:
```javascript
import {
  getInstitutions,
  // ...
} from '@/api/institution'

const loadData = async () => {
  try {
    const res = await getInstitutions(getPaginationParams())
    if (res.success) {
      institutions.value = extractDataList(res.data)
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  }
}
```

**修改后**:
```javascript
import {
  searchInstitutions,  // 改用searchInstitutions
  // ...
} from '@/api/institution'

const loadData = async () => {
  try {
    const res = await searchInstitutions(getPaginationParams())
    if (res.success) {
      institutions.value = extractDataList(res.data)
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  }
}
```

**优点**:
- 使用已有的API函数
- 语义更清晰（search表示搜索）

**缺点**:
- 需要修改页面代码
- 如果其他地方也用了getInstitutions，需要一起修改

---

## 📋 推荐修复方案

**推荐使用方案1**，原因：
1. 只需修改一处（API定义文件）
2. 对现有代码影响最小
3. 保持API接口名称的语义一致性

---

## 🔍 其他可能受影响的地方

需要检查项目中是否还有其他地方调用了 `getInstitutions`：

```bash
# 搜索命令
grep -r "getInstitutions" src/
```

**可能的文件**:
- `src/views/ops/Institutions.vue` - 机构管理页面
- `src/components/InstitutionSelector.vue` - 机构选择组件（如果有）
- 其他使用机构列表的页面

---

## 📝 修复步骤

### 步骤1: 修改API定义

编辑 `src/api/institution.js`:

```javascript
/**
 * 获取机构列表
 * 注意：后端已将此接口改为POST方式，使用/search端点
 */
export function getInstitutions(params) {
  return request({
    url: '/institutions/search',
    method: 'post',
    data: params  // POST使用data，不是params
  })
}
```

### 步骤2: 测试验证

1. 清除浏览器缓存（Ctrl+Shift+R）
2. 重新登录系统
3. 访问"系统管理" → "机构管理"
4. 应该能看到机构列表（42094条记录）

### 步骤3: 检查其他调用

搜索项目中所有使用 `getInstitutions` 的地方，确保都能正常工作。

---

## 🧪 测试验证

### 测试脚本
```bash
python scripts/test_institutions_api.py
```

### 预期结果
```
✅ 搜索机构（POST）: 正常
总记录数: 42094
当前页记录数: 50
```

---

## 📊 数据统计

**机构数据量**: 42094条

**分页建议**:
- 默认每页: 50条
- 总页数: 842页
- 建议添加搜索功能，避免用户翻页过多

---

## 💡 后续优化建议

### 1. 添加搜索功能

在机构管理页面添加搜索框：
- 按机构名称搜索
- 按地区筛选
- 按等级筛选

### 2. 优化分页

- 添加快速跳转功能
- 显示总记录数
- 优化分页器样式

### 3. 性能优化

- 考虑使用虚拟滚动
- 添加加载状态提示
- 优化大数据量渲染

---

## 🎯 优先级

**优先级**: 🔴 高

**原因**:
1. 影响OPS核心功能
2. 机构管理页面无法正常使用
3. 修复简单，只需改一行代码

**建议处理时间**: 立即修复（5分钟）

---

**报告生成时间**: 2026-03-01  
**报告生成人**: Kiro AI Assistant
