# 书审得分API修复报告

## 修复时间
2026-03-01

## 问题描述

书审得分页面调用 `GET /api/admin/reviews/book-scores` 返回404错误，导致页面无法加载数据。

```
错误: GET /api/admin/reviews/book-scores?competitionId=1 → 404 Not Found
位置: Score.vue:247
```

## 问题分析

### 后端API状态

通过测试脚本验证：

| API端点 | 状态 | 说明 |
|---------|------|------|
| `/admin/reviews/book-scores` | ❌ 404 | 不存在 |
| `/admin/reviews/scores` | ❌ 404 | 不存在 |
| `/admin/reviews/summary` | ✅ 200 | 存在，需要stage参数 |

### 可用的替代API

`GET /admin/reviews/summary` 支持以下参数：
- `competitionId` (必填)
- `stage` (必填: BOOK/INTERVIEW/FINAL)
- `groupType` (可选)
- `reviewerName` (可选)
- `institutionName` (可选)

## 解决方案

使用 `/admin/reviews/summary?stage=BOOK` 替代原API。

### 代码修改

**文件:** `src/api/review.js`

**修改前:**
```javascript
export function getBookScores(params) {
  return request({
    url: '/admin/reviews/book-scores',
    method: 'get',
    params
  })
}
```

**修改后:**
```javascript
/**
 * 获取书审得分列表（组委会管理）
 * 使用 /admin/reviews/summary API，固定 stage=BOOK
 */
export function getBookScores(params) {
  return request({
    url: '/admin/reviews/summary',
    method: 'get',
    params: {
      ...params,
      stage: 'BOOK'  // 固定为书审阶段
    }
  })
}
```

### 修改说明

1. **API端点变更:** `/admin/reviews/book-scores` → `/admin/reviews/summary`
2. **参数调整:** 自动添加 `stage: 'BOOK'` 参数
3. **兼容性:** 保持原有参数（competitionId, groupType, reviewerName, institutionName）不变
4. **影响范围:** 仅影响 `src/views/committee/book/Score.vue` 页面

## 测试验证

### API测试结果

```bash
# 测试脚本
python scripts/explore_summary_api.py

# 结果
GET /admin/reviews/summary?competitionId=1&stage=BOOK
状态码: 200 ✅
响应: { "success": true, "data": [], "message": null }

# 支持筛选参数
- competitionId + stage + groupType: 200 ✅
- competitionId + stage + reviewerName: 200 ✅
- competitionId + stage + institutionName: 200 ✅
- 所有参数组合: 200 ✅
```

### 当前状态

- ✅ API调用成功，不再返回404
- ⚠️ 系统中暂无评分数据，返回空数组
- ⏳ 需要等待有评分数据后验证字段结构

## 待验证事项

### 数据结构验证

需要在系统有评分数据后，验证返回的字段是否包含：

**必需字段:**
- `scoreId` - 评分ID（用于驳回功能）
- `projectName` - 项目名称
- `institutionName` - 医疗机构
- `institutionLevel` - 机构等级
- `groupType` - 组别
- `groupCode` - 分组代码
- `reviewerName` - 评委姓名
- `reviewerInstitutionName` - 评委机构
- `plan`, `problem`, `action`, `success`, `review`, `operation`, `presentation` - 7个分项评分
- `total` - 总分
- `submittedAt` - 提交时间

### 功能验证

需要测试以下功能：
1. ✅ 页面加载（不再404）
2. ⏳ 数据显示（等待有数据）
3. ⏳ 筛选功能（按组别、评委、机构）
4. ⏳ 驳回功能（需要scoreId字段）

## 风险评估

### 已解决
- ✅ API 404错误已修复
- ✅ 参数传递正确
- ✅ 筛选功能支持

### 潜在风险
- ⚠️ 字段名可能不完全匹配（需要有数据后验证）
- ⚠️ 某些字段可能缺失（需要有数据后验证）

### 缓解措施
- 已准备字段映射方案（如需要）
- 保持与后端沟通渠道
- 记录字段差异以便反馈

## 后续行动

1. **立即:** ✅ 代码已修改并提交
2. **短期:** 等待系统有评分数据后测试页面
3. **中期:** 验证所有字段和功能正常
4. **长期:** 如有问题，反馈后端或添加适配层

## 相关文件

### 修改的文件
- `src/api/review.js` - API定义

### 测试脚本
- `scripts/test_book_scores_api.py` - API存在性测试
- `scripts/explore_summary_api.py` - API参数和结构探测
- `scripts/create_test_score_data.py` - 测试数据创建（未成功）

### 文档
- `docs/CONSOLE_ERRORS_ANALYSIS_20260301.md` - 问题分析
- `docs/BOOK_SCORE_AND_SCROLLBAR_ANALYSIS.md` - 详细技术分析
- `docs/SUMMARY_API_USAGE_PLAN.md` - 实施方案
- `docs/BOOK_SCORES_API_FIX.md` - 本文档

## 总结

通过将API端点从不存在的 `/admin/reviews/book-scores` 改为可用的 `/admin/reviews/summary`，并固定添加 `stage=BOOK` 参数，成功解决了404错误。页面现在可以正常调用API，等待系统有评分数据后即可完整验证功能。
