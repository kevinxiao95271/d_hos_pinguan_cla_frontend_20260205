# 等级下拉框问题 - API分析报告

## 🎯 问题描述

**用户反馈**：注册报名的机构搜索场景下，等级下拉框里有"三甲"、"二甲"等选项，这些数据不应该出现。

---

## 🔍 问题定位

### 1. 前端代码位置

**文件**: `src/components/InstitutionSelector.vue`

**相关代码**（第56-70行）:
```vue
<el-form-item label="等级">
  <el-select
    v-model="filters.level"
    placeholder="选择等级"
    clearable
    @change="handleFilterChange"
    style="width: 150px"
  >
    <el-option
      v-for="level in allLevels"
      :key="level"
      :label="level"
      :value="level"
    />
  </el-select>
</el-form-item>
```

**数据来源**（第161行）:
```javascript
const allLevels = ref([])
```

**数据初始化**（第274-284行）:
```javascript
onMounted(async () => {
  try {
    // 并行加载所有初始数据
    const [citiesRes, levelsRes] = await Promise.all([
      getCities(),
      getAllLevels()  // ← 这里调用获取等级列表
    ])

    if (citiesRes.success) {
      cities.value = citiesRes.data
    }
    if (levelsRes.success) {
      allLevels.value = levelsRes.data  // ← "三甲"、"二甲"就是从这里来的！
    }

    // 加载初始机构列表
    loadInstitutions()
  } catch (error) {
    console.error('初始化失败:', error)
  }
})
```

---

## 🌐 API信息

### API定义

**文件**: `src/api/institution.js`

**代码**（第135-145行）:
```javascript
/**
 * 获取所有等级列表
 * 公开接口，无需Token
 */
export function getAllLevels() {
  return request({
    url: '/institutions/levels',
    method: 'get',
    skipAuth: true
  })
}
```

### API详情

| 项目 | 内容 |
|------|------|
| **API地址** | `GET /api/institutions/levels` |
| **请求方法** | GET |
| **访问权限** | 公开接口（skipAuth: true，无需Token） |
| **调用时机** | 页面初始化时（onMounted） |
| **用途** | 填充机构搜索的"等级"下拉框选项 |

---

## 📦 API返回数据结构

### 预期格式

根据前端代码，后端应该返回以下格式：

```json
{
  "success": true,
  "data": [
    "等级选项1",
    "等级选项2",
    "等级选项3"
  ],
  "message": "成功"
}
```

### 前端使用方式

前端直接使用 `levelsRes.data` 作为下拉框选项：

```javascript
if (levelsRes.success) {
  allLevels.value = levelsRes.data  // 直接赋值给下拉框数据源
}
```

然后在模板中循环渲染：

```vue
<el-option
  v-for="level in allLevels"
  :key="level"
  :label="level"
  :value="level"
/>
```

---

## ❌ 当前问题

### 问题现象

前端等级下拉框中出现了：
- **"三甲"** - 三级甲等医院
- **"二甲"** - 二级甲等医院
- 可能还有 **"一甲"**、**"三乙"** 等

### 数据来源

这些数据**100%来自后端API**: `GET /api/institutions/levels`

**证据**：
1. 前端 `allLevels` 变量在初始化时为空数组（第161行）
2. 只有在调用 `getAllLevels()` API 成功后，才会赋值（第283行）
3. 前端没有任何硬编码的等级数据
4. 前端没有对返回数据进行任何加工或映射

### 问题本质

后端 `/api/institutions/levels` API 返回的是**医院的等级分类**（三级甲等、二级甲等等），而不是**机构的行政级别**。

---

## ✅ 正确的数据应该是什么

### 方案1：机构无等级分类（推荐）

如果机构本身没有"等级"这个维度，建议返回空数组：

```json
{
  "success": true,
  "data": [],
  "message": "成功"
}
```

**效果**：前端等级下拉框为空，不显示该筛选条件。

### 方案2：使用行政级别

如果确实需要按等级筛选机构，应该返回行政级别：

```json
{
  "success": true,
  "data": [
    "省级",
    "市级",
    "区县级"
  ],
  "message": "成功"
}
```

### 方案3：使用其他分类

如果有其他合理的机构分类维度：

```json
{
  "success": true,
  "data": [
    "综合医院",
    "专科医院",
    "社区卫生服务中心"
  ],
  "message": "成功"
}
```

---

## 🔧 如何验证API返回数据

### 方法1：使用浏览器

1. 打开浏览器开发者工具（F12）
2. 访问注册页面的机构搜索
3. 切换到 Network 标签
4. 找到 `levels` 请求
5. 查看 Response 数据

### 方法2：使用curl命令

```bash
curl http://localhost:6031/api/institutions/levels
```

### 方法3：使用Postman或Swagger

- 访问后端的 Swagger 文档
- 找到 `GET /api/institutions/levels` 接口
- 点击 "Try it out" → "Execute"
- 查看返回数据

### 方法4：使用Python脚本

已提供测试脚本 `scripts/test_levels_api.py`，运行：

```bash
python scripts/test_levels_api.py
```

---

## 📋 反馈给后端的信息

### 问题概要

**API**: `GET /api/institutions/levels`  
**问题**: 返回的是医院分级（三甲、二甲），不应该出现在机构等级筛选中  
**影响**: 前端机构搜索的等级下拉框显示了错误的选项  

### 详细说明

1. **API地址**: `GET /api/institutions/levels`
2. **调用位置**: 前端注册页面的机构搜索组件（`InstitutionSelector.vue`）
3. **调用时机**: 页面初始化时自动调用
4. **当前返回数据**（问题数据）:
   ```json
   {
     "success": true,
     "data": ["三甲", "二甲", ...]  // ← 这些是医院分级，不应该在这里
   }
   ```
5. **期望返回数据**:
   ```json
   {
     "success": true,
     "data": []  // 空数组，表示机构无等级分类
   }
   ```
   或者
   ```json
   {
     "success": true,
     "data": ["省级", "市级", "区县级"]  // 行政级别
   }
   ```

### 建议修复方案

**方案A（推荐）**：如果机构没有"等级"维度，直接返回空数组：
```java
@GetMapping("/institutions/levels")
public ApiResponse<List<String>> getLevels() {
    return ApiResponse.success(Collections.emptyList());
}
```

**方案B**：如果需要返回行政级别：
```java
@GetMapping("/institutions/levels")
public ApiResponse<List<String>> getLevels() {
    List<String> levels = Arrays.asList("省级", "市级", "区县级");
    return ApiResponse.success(levels);
}
```

### 后端需要检查的代码

1. 找到 `GET /api/institutions/levels` 的控制器方法
2. 检查返回数据的来源（可能是数据库查询、配置文件等）
3. 确认是否混淆了"医院等级"和"机构等级"的概念
4. 修改返回逻辑，确保返回正确的机构等级数据

---

## 📸 前端截图位置

如果需要截图给后端看，可以：

1. 访问页面：`http://localhost:5173/register`
2. 进入机构搜索部分
3. 点击"等级"下拉框
4. 截图显示"三甲"、"二甲"等选项
5. 标注：这些数据来自 `GET /api/institutions/levels`

---

## 📊 数据流转图

```
后端数据库/配置
    ↓
GET /api/institutions/levels
    ↓
返回 ["三甲", "二甲", ...]  ← 问题在这里！
    ↓
前端 getAllLevels() 调用
    ↓
allLevels.value = levelsRes.data
    ↓
等级下拉框显示"三甲"、"二甲"  ← 用户看到的错误选项
```

---

## 🎯 总结

### 问题根源

后端 `GET /api/institutions/levels` API 返回了医院的三级甲等、二级甲等分类，而不是机构的行政级别或其他合理的等级分类。

### 责任归属

**100%是后端问题**，前端只是忠实地展示了后端返回的数据。

### 解决方案

后端修改 `GET /api/institutions/levels` 的返回数据：
- 方案1：返回空数组 `[]`（推荐）
- 方案2：返回行政级别 `["省级", "市级", "区县级"]`
- 方案3：返回其他合理的机构分类

### 前端无需改动

前端代码逻辑正确，无需修改。只要后端返回正确的数据，问题即可解决。

---

**报告生成时间**: 2026-02-26  
**报告目的**: 为后端提供清晰的问题定位和修复建议
