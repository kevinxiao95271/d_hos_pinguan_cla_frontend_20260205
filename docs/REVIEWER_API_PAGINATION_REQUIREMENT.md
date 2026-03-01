# 评委列表API分页需求

## 问题描述

当前 `GET /api/admin/reviewers` API不支持分页，无论传入什么分页参数，都返回所有数据（131条）的数组格式。

这导致前端的分页器无法正常工作，用户改变每页数目（如改成100条）时，显示的数据数量不会改变。

## 测试结果

### 当前API行为

```bash
# 测试1: 无分页参数
GET /api/admin/reviewers?competitionId=1
返回: 数组格式，131条数据

# 测试2: 每页10条
GET /api/admin/reviewers?competitionId=1&page=0&size=10
返回: 数组格式，131条数据（忽略了分页参数）

# 测试3: 每页50条
GET /api/admin/reviewers?competitionId=1&page=0&size=50
返回: 数组格式，131条数据（忽略了分页参数）

# 测试4: 每页100条
GET /api/admin/reviewers?competitionId=1&page=0&size=100
返回: 数组格式，131条数据（忽略了分页参数）

# 测试5: 第2页，每页50条
GET /api/admin/reviewers?competitionId=1&page=1&size=50
返回: 数组格式，131条数据（忽略了分页参数）
```

**结论:** API完全忽略了 `page` 和 `size` 参数，始终返回所有数据。

## 前端期望

### API端点
```
GET /api/admin/reviewers
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| competitionId | number | 是 | 赛事ID | 1 |
| page | number | 否 | 页码（从0开始） | 0 |
| size | number | 否 | 每页数量 | 50 |
| institutionId | number | 否 | 机构ID筛选 | 36232 |
| expertBackground | string | 否 | 专家背景筛选 | "MEDICAL" |

### 期望的响应格式

**分页格式（推荐）:**

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": 5,
        "phone": "13800002569",
        "name": "孙丽娟",
        "title": "Test Title",
        "institutionId": 36232,
        "institutionName": "绍兴市第七人民医院",
        "reviewerGroupCode": "A1",
        "interviewGroupCode": "A1",
        "expertBackground": "MEDICAL",
        "currentLoad": 0
      }
      // ... 更多评委
    ],
    "pageNo": 0,
    "pageSize": 50,
    "totalCount": 131,
    "totalPages": 3,
    "hasNext": true,
    "hasPrevious": false
  },
  "message": null
}
```

### 分页字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| content | array | 当前页的数据列表 |
| pageNo | number | 当前页码（从0开始） |
| pageSize | number | 每页数量 |
| totalCount | number | 总记录数 |
| totalPages | number | 总页数 |
| hasNext | boolean | 是否有下一页 |
| hasPrevious | boolean | 是否有上一页 |

## 前端代码逻辑

### 前端如何使用分页数据

```javascript
// 1. 获取分页参数
const params = {
  competitionId: 1,
  page: 0,      // 当前页码
  size: 50      // 每页数量
}

// 2. 调用API
const res = await getReviewers(params)

// 3. 提取数据
if (res.success) {
  const data = res.data
  
  // 判断是否为分页格式
  if (data.content && data.pageNo !== undefined) {
    // 分页格式
    reviewers.value = data.content           // 当前页数据
    currentPage.value = data.pageNo          // 当前页码
    pageSize.value = data.pageSize           // 每页数量
    totalCount.value = data.totalCount       // 总记录数
  } else if (Array.isArray(data)) {
    // 数组格式（不支持分页）
    reviewers.value = data
    totalCount.value = data.length
  }
}
```

### 前端分页器配置

```vue
<el-pagination
  v-model:current-page="currentPage"
  v-model:page-size="pageSize"
  :total="totalCount"
  :page-sizes="[10, 20, 50, 100, 200]"
  layout="total, sizes, prev, pager, next, jumper"
  @size-change="handlePageSizeChange"
  @current-change="loadReviewers"
/>
```

## 使用场景

### 场景1: 书审评委分配
- **页面:** `src/views/committee/book/Reviewer.vue`
- **默认每页:** 50条
- **可选每页:** 10, 20, 50, 100, 200

### 场景2: 面谈评委分配
- **页面:** `src/views/committee/interview/Reviewer.vue`
- **默认每页:** 50条
- **可选每页:** 10, 20, 50, 100, 200

### 场景3: 决赛评委分配
- **页面:** `src/views/committee/final/Reviewer.vue`
- **默认每页:** 50条
- **可选每页:** 10, 20, 50, 100, 200

## 为什么需要分页

1. **性能优化**
   - 当前131位评委，未来可能更多
   - 一次性加载所有数据会影响性能
   - 分页可以减少数据传输量

2. **用户体验**
   - 用户可以选择每页显示数量
   - 大屏幕用户可以选择100条/页
   - 小屏幕用户可以选择10条/页

3. **功能一致性**
   - 报名列表已经支持分页
   - 评委列表也应该支持分页
   - 保持前端功能一致

## 实现建议

### 后端实现步骤

1. **接收分页参数**
   ```java
   @GetMapping("/admin/reviewers")
   public Result<PageResult<Reviewer>> getReviewers(
       @RequestParam Long competitionId,
       @RequestParam(defaultValue = "0") Integer page,
       @RequestParam(defaultValue = "50") Integer size,
       @RequestParam(required = false) Long institutionId,
       @RequestParam(required = false) String expertBackground
   ) {
       // ...
   }
   ```

2. **使用分页查询**
   ```java
   Pageable pageable = PageRequest.of(page, size);
   Page<Reviewer> reviewerPage = reviewerRepository.findByConditions(
       competitionId, institutionId, expertBackground, pageable
   );
   ```

3. **返回分页结果**
   ```java
   PageResult<Reviewer> result = new PageResult<>();
   result.setContent(reviewerPage.getContent());
   result.setPageNo(reviewerPage.getNumber());
   result.setPageSize(reviewerPage.getSize());
   result.setTotalCount(reviewerPage.getTotalElements());
   result.setTotalPages(reviewerPage.getTotalPages());
   result.setHasNext(reviewerPage.hasNext());
   result.setHasPrevious(reviewerPage.hasPrevious());
   
   return Result.success(result);
   ```

## 兼容性说明

### 前端已经准备好

前端的 `usePagination` composable 已经支持两种格式：

1. **分页格式:** 自动提取 `content`、`pageNo`、`totalCount` 等字段
2. **数组格式:** 兼容处理，将数组作为单页数据

所以后端改成分页格式后，前端代码**无需修改**，会自动适配。

### 测试验证

后端实现后，可以使用以下脚本测试：

```bash
python scripts/test_reviewer_pagination.py
```

期望结果：
- 每页10条时，返回10条数据
- 每页50条时，返回50条数据
- 每页100条时，返回100条数据
- 第2页时，返回不同的数据（ID不同）

## 相关文件

### 前端文件
- `src/views/committee/book/Reviewer.vue` - 书审评委分配
- `src/views/committee/interview/Reviewer.vue` - 面谈评委分配
- `src/views/committee/final/Reviewer.vue` - 决赛评委分配
- `src/composables/usePagination.js` - 分页逻辑
- `src/api/admin.js` - API定义

### 测试脚本
- `scripts/test_reviewer_pagination.py` - 分页功能测试

### 文档
- `docs/REVIEWER_API_PAGINATION_REQUIREMENT.md` - 本文档

## 总结

**当前问题:** API不支持分页，忽略 `page` 和 `size` 参数

**解决方案:** 后端实现分页功能，返回分页格式的数据

**前端改动:** 无需改动，已经支持分页格式

**测试方法:** 使用 `test_reviewer_pagination.py` 脚本验证
