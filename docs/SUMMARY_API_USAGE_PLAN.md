# 使用 /admin/reviews/summary API 的方案

## 当前状况

1. **目标API不存在:** `GET /admin/reviews/book-scores` 返回404
2. **替代API可用:** `GET /admin/reviews/summary?stage=BOOK` 返回200
3. **数据状态:** 系统中暂无评分数据，无法验证返回的数据结构

## 测试结果

### API测试
```bash
GET /admin/reviews/summary?competitionId=1&stage=BOOK
状态码: 200
响应: { "success": true, "data": [], "message": null }
```

### 参数支持
测试确认该API支持以下筛选参数：
- ✅ `competitionId` (必填)
- ✅ `stage` (必填: BOOK/INTERVIEW/FINAL)
- ✅ `groupType` (可选: BASIC/COMPREHENSIVE/ADVANCED)
- ✅ `reviewerName` (可选: 评委姓名)
- ✅ `institutionName` (可选: 机构名称)

## 前端需要的字段

根据 `src/views/committee/book/Score.vue` 分析：

```javascript
{
  scoreId: number,              // 评分ID（用于驳回）
  projectName: string,          // 项目名称
  institutionName: string,      // 医疗机构
  institutionLevel: string,     // 机构等级
  groupType: string,            // 组别
  groupCode: string,            // 分组代码
  reviewerName: string,         // 评委姓名
  reviewerInstitutionName: string, // 评委机构
  
  // 7个分项评分
  plan: number,
  problem: number,
  action: number,
  success: number,
  review: number,
  operation: number,
  presentation: number,
  
  total: number,                // 总分
  submittedAt: string           // 提交时间
}
```

## 实施方案

### 方案A: 直接替换API端点（推荐）

假设 `/admin/reviews/summary` 返回的数据结构与前端需求一致或接近。

**修改文件:** `src/api/review.js`

```javascript
/**
 * 获取书审得分列表（组委会管理）
 */
export function getBookScores(params) {
  return request({
    url: '/admin/reviews/summary',  // 修改端点
    method: 'get',
    params: {
      ...params,
      stage: 'BOOK'  // 固定添加stage参数
    }
  })
}
```

**优点:**
- 只需修改一行代码
- 前端其他代码无需改动
- 立即可用

**风险:**
- 如果字段名不匹配，需要额外处理
- 如果缺少必需字段，功能可能不完整

### 方案B: 添加数据适配层

如果API返回的字段名与前端不一致，添加适配函数。

```javascript
/**
 * 获取书审得分列表（组委会管理）
 */
export function getBookScores(params) {
  return request({
    url: '/admin/reviews/summary',
    method: 'get',
    params: {
      ...params,
      stage: 'BOOK'
    }
  }).then(response => {
    // 如果需要字段映射
    if (response.success && response.data) {
      response.data = response.data.map(item => ({
        scoreId: item.id || item.scoreId,
        projectName: item.projectName,
        institutionName: item.institutionName,
        institutionLevel: item.institutionLevel,
        groupType: item.groupType,
        groupCode: item.groupCode,
        reviewerName: item.reviewerName,
        reviewerInstitutionName: item.reviewerInstitution || item.reviewerInstitutionName,
        plan: item.plan,
        problem: item.problem,
        action: item.action,
        success: item.success,
        review: item.review,
        operation: item.operation,
        presentation: item.presentation,
        total: item.total || item.totalScore,
        submittedAt: item.submittedAt || item.createdAt
      }))
    }
    return response
  })
}
```

## 建议的实施步骤

### 第1步: 先使用方案A（最简单）

直接修改API端点，看是否能正常工作：

```javascript
// src/api/review.js
export function getBookScores(params) {
  return request({
    url: '/admin/reviews/summary',
    method: 'get',
    params: {
      ...params,
      stage: 'BOOK'
    }
  })
}
```

### 第2步: 测试验证

1. 修改代码后，访问书审得分页面
2. 查看控制台是否还有404错误
3. 如果有评分数据，检查页面显示是否正常

### 第3步: 根据结果调整

**情况A: 页面正常显示**
- ✅ 完成！无需进一步修改

**情况B: 字段名不匹配**
- 使用方案B添加字段映射
- 或者反馈给后端调整字段名

**情况C: 缺少必需字段**
- 反馈给后端，需要在API中添加缺失字段
- 或者考虑从其他API获取补充数据

## 风险评估

### 低风险
- API端点存在且可访问 ✅
- 支持所需的筛选参数 ✅
- 返回格式符合预期（success/data/message）✅

### 中风险
- 字段名可能不完全匹配 ⚠️
- 某些字段可能缺失 ⚠️

### 缓解措施
- 先实施方案A，快速验证
- 准备方案B作为备选
- 与后端保持沟通，确认字段列表

## 后续跟进

1. **立即行动:** 实施方案A，修改API端点
2. **测试验证:** 在有评分数据时测试页面功能
3. **记录问题:** 如果发现字段不匹配，记录具体差异
4. **反馈后端:** 将字段差异反馈给后端团队
5. **最终确认:** 确保所有功能（查看、筛选、驳回）正常工作

## 相关文件

- `src/api/review.js` - API定义文件
- `src/views/committee/book/Score.vue` - 书审得分页面
- `scripts/explore_summary_api.py` - API探测脚本
- `scripts/create_test_score_data.py` - 测试数据创建脚本
