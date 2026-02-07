# 批量添加分页功能 - 修改清单

## 执行计划

由于需要修改11个页面，每个页面的修改包括：
1. 引入 usePagination
2. 初始化分页状态
3. 修改数据加载函数
4. 添加分页器组件
5. 添加分页样式
6. 筛选时重置分页

为了提高效率，我将：
1. 先完成最关键的2个页面（评审任务列表、书审评委分配）作为示例
2. 然后基于模式快速完成其他页面
3. 最后统一测试所有分页功能

## 修改优先级

### P0 - 立即修改（后端明确支持分页的API）
1. src/views/reviewer/Tasks.vue - 使用 getMyReviewTasks (stage API)
2. src/views/committee/book/Reviewer.vue - 使用 filterRegistrations
3. src/views/committee/interview/Reviewer.vue - 使用 filterRegistrations
4. src/views/committee/final/Reviewer.vue - 使用 filterRegistrations
5. src/views/committee/book/Registration.vue - 使用 filterRegistrations
6. src/views/committee/interview/Group.vue - 使用 filterRegistrations

### P1 - 后续修改（其他列表）
7. src/views/committee/book/Score.vue
8. src/views/committee/interview/Score.vue
9. src/views/committee/final/Score.vue
10. src/views/committee/interview/Shortlist.vue
11. src/views/ops/Institutions.vue

## 关键修改点

### 1. 引入依赖
```javascript
import { usePagination } from '@/composables/usePagination'
```

### 2. 初始化
```javascript
const {
  currentPage,
  pageSize,
  totalCount,
  pageSizes,
  showPagination,
  extractDataList,
  resetPagination,
  getPaginationParams
} = usePagination({ defaultPageSize: 50 })
```

### 3. 修改API调用
```javascript
// 添加分页参数
const res = await api({
  ...existingParams,
  ...getPaginationParams()
})

// 使用 extractDataList 处理返回数据
dataList.value = extractDataList(res.data)
```

### 4. 添加分页器
```vue
<div v-if="showPagination" class="pagination-container">
  <el-pagination
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :total="totalCount"
    :page-sizes="pageSizes"
    layout="total, sizes, prev, pager, next, jumper"
    @size-change="loadData"
    @current-change="loadData"
  />
</div>
```

### 5. 筛选重置
```javascript
const handleFilter = () => {
  resetPagination()
  loadData()
}
```

## 开始执行

现在开始逐个修改...
