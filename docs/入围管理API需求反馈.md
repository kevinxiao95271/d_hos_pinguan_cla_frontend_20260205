# 入围管理页面 - 后端API需求反馈

> 日期：2026-02-07  
> 状态：等待后端实现/确认  
> 负责人：前端已完成设计，等待后端API调整

---

## 📋 功能概述

入围管理页面用于**综合管理书审和面谈的入围决策**，需要在一个页面上同时展示：
- 书审得分
- 面谈得分
- 综合排名（基于加权计算）
- 入围状态管理

---

## 🔌 核心API需求

### API 1: 书审排名接口 ⭐⭐⭐

**重要性**: 必需（核心功能）

**接口**:
```
GET /api/admin/reviews/rankings
```

**请求参数**:
```json
{
  "competitionId": 21,     // 必需：赛事ID
  "stage": "BOOK"          // 必需：阶段（书审）
}
```

**期望响应**:
```json
{
  "success": true,
  "data": [
    {
      "registrationId": 106,               // ⭐ 必需：报名ID
      "projectName": "护理交接班规范化-1",   // ⭐ 必需：项目名称
      "institutionName": "浙江大学医学院附属第一医院", // ⭐ 必需：医疗机构名称
      "groupType": "BASIC",                // ⭐ 必需：组别
      "avgTotal": 92.5,                    // ⭐ 必需：总分（核心字段）
      "avgPlan": 18,                       // 建议：计划得分
      "avgProblem": 17,                    // 建议：问题得分
      "avgAction": 19,                     // 建议：行动得分
      "avgSuccess": 18,                    // 建议：成效得分
      "avgReview": 16,                     // 建议：回顾得分
      "avgOperation": 0,                   // 建议：运作得分
      "avgPresentation": 0,                // 建议：展示得分
      "highlights": ["亮点1", "亮点2"],     // 建议：亮点汇总
      "weaknesses": ["建议1", "建议2"]      // 建议：改进建议汇总
    }
    // ... 更多项目
  ],
  "message": null
}
```

**关键字段说明**:
| 字段 | 类型 | 必需性 | 说明 |
|-----|------|--------|------|
| `registrationId` | Integer | ⭐ 必需 | 用于合并书审和面谈数据 |
| `projectName` | String | ⭐ 必需 | 项目名称 |
| `institutionName` | String | ⭐ 必需 | 医疗机构名称 |
| `groupType` | String | ⭐ 必需 | 组别（BASIC/ADVANCED/COMPREHENSIVE） |
| `avgTotal` | Double | ⭐ 必需 | **核心字段**，用于综合得分计算 |
| `avgPlan` 等细分 | Double | 建议 | 用于详情展示 |
| `highlights` | Array | 建议 | 评委亮点汇总 |
| `weaknesses` | Array | 建议 | 评委改进建议汇总 |

---

### API 2: 面谈排名接口 ⭐⭐⭐

**重要性**: 必需（核心功能）

**接口**:
```
GET /api/admin/reviews/rankings
```

**请求参数**:
```json
{
  "competitionId": 21,     // 必需：赛事ID
  "stage": "INTERVIEW"     // 必需：阶段（面谈）
}
```

**期望响应**:
```json
{
  "success": true,
  "data": [
    {
      "registrationId": 106,               // ⭐ 必需：报名ID（用于与书审数据合并）
      "projectName": "护理交接班规范化-1",   // ⭐ 必需：项目名称
      "institutionName": "浙江大学医学院附属第一医院", // ⭐ 必需：医疗机构名称
      "groupType": "ADVANCED",             // ⭐ 必需：组别（注：只有进阶组有面谈）
      "avgTotal": 90.0,                    // ⭐ 必需：总分（核心字段）
      "avgPlan": 18,                       // 建议：计划得分
      "avgProblem": 17,                    // 建议：问题得分
      // ... 其他细分得分
      "highlights": ["亮点1", "亮点2"],     // 建议：亮点汇总
      "weaknesses": ["建议1", "建议2"]      // 建议：改进建议汇总
    }
    // ... 更多项目
  ],
  "message": null
}
```

**特殊说明**:
- ⚠️ 面谈阶段可能返回**空数组**（面谈未开始或未完成）是正常的
- ⚠️ 只有**进阶组**项目才参加面谈
- ⚠️ `data` 为空数组时，前端会标记这些项目为"待面谈"

---

### API 3: 评审详情接口 ⭐⭐

**重要性**: 建议（用于查看详情）

**接口**:
```
GET /api/registrations/{registrationId}/review-details
```

**期望响应**:
```json
{
  "success": true,
  "data": [
    {
      "stage": "BOOK",                     // 阶段
      "avgTotal": 92.5,                    // 总分
      "avgPlan": 18,                       // 计划得分
      "avgProblem": 17,                    // 问题得分
      "avgAction": 19,                     // 行动得分
      "avgSuccess": 18,                    // 成效得分
      "avgReview": 16,                     // 回顾得分
      "avgOperation": 0,                   // 运作得分
      "avgPresentation": 0,                // 展示得分
      "highlights": ["亮点1", "亮点2"],     // 亮点列表
      "weaknesses": ["建议1", "建议2"]      // 改进建议列表
    },
    {
      "stage": "INTERVIEW",                // 面谈阶段
      // ... 同样的结构
    }
  ],
  "message": null
}
```

**用途**: 点击"查看详情"时，显示该项目的详细评分和评委意见。

---

## 🎯 前端数据合并逻辑

### 核心算法

```javascript
// 1. 获取书审和面谈数据
const bookData = await getBookRankings()      // API 1
const interviewData = await getInterviewRankings()  // API 2

// 2. 创建项目映射（以 registrationId 为key）
const projectMap = new Map()

// 3. 添加书审数据
bookData.forEach(item => {
  projectMap.set(item.registrationId, {
    registrationId: item.registrationId,
    projectName: item.projectName,
    institutionName: item.institutionName,
    groupType: item.groupType,
    bookScore: item.avgTotal,       // 书审得分
    interviewScore: null,           // 面谈得分（初始为空）
    compositeScore: null            // 综合得分（待计算）
  })
})

// 4. 添加面谈数据
interviewData.forEach(item => {
  if (projectMap.has(item.registrationId)) {
    projectMap.get(item.registrationId).interviewScore = item.avgTotal
  }
})

// 5. 计算综合得分
const bookWeight = 50  // 书审权重 50%
const interviewWeight = 50  // 面谈权重 50%

projectMap.forEach(project => {
  if (project.bookScore !== null && project.interviewScore !== null) {
    // 有书审和面谈得分，计算综合得分
    project.compositeScore = 
      project.bookScore * bookWeight / 100 + 
      project.interviewScore * interviewWeight / 100
  } else if (project.bookScore !== null) {
    // 只有书审，标记为"待面谈"
    project.compositeScore = null
  }
})

// 6. 按综合得分排序
const projects = Array.from(projectMap.values())
projects.sort((a, b) => {
  if (a.compositeScore === null) return 1   // 待面谈排在后面
  if (b.compositeScore === null) return -1
  return b.compositeScore - a.compositeScore  // 降序
})

// 7. 分配排名
let rank = 1
projects.forEach(project => {
  if (project.compositeScore !== null) {
    project.rank = rank++
  }
})
```

### 示例结果

```javascript
[
  {
    rank: 1,
    registrationId: 106,
    projectName: "护理交接班规范化-1",
    institutionName: "浙江大学医学院附属第一医院",
    groupType: "ADVANCED",
    bookScore: 92.5,
    interviewScore: 90.0,
    compositeScore: 91.25,  // (92.5 * 50% + 90.0 * 50%)
    isShortlisted: false    // 入围状态（前端管理）
  },
  {
    rank: 2,
    registrationId: 107,
    projectName: "门诊报到时效提升-2",
    bookScore: 89.0,
    interviewScore: 88.0,
    compositeScore: 88.5
  },
  // ... 更多已完成面谈的项目
  {
    rank: null,
    registrationId: 115,
    projectName: "缩短等待时间改进项目-10",
    groupType: "BASIC",
    bookScore: 85.0,
    interviewScore: null,   // 基层组没有面谈
    compositeScore: null    // 标记为"待面谈"（虽然实际是没有面谈）
  }
]
```

---

## 🎨 前端页面设计要点

### 1. 入围策略配置区

```vue
<el-card>
  <!-- 权重配置 -->
  <el-form-item label="评分权重">
    书审权重: <el-input-number v-model="bookWeight" />%
    面谈权重: <el-input-number v-model="interviewWeight" />%
    <el-button @click="applyWeight">应用权重</el-button>
  </el-form-item>

  <!-- 入围比例 -->
  <el-form-item label="入围比例">
    <el-radio-group v-model="ratioType">
      <el-radio value="30">前30%</el-radio>
      <el-radio value="40">前40%</el-radio>
      <el-radio value="50">前50%</el-radio>
      <el-radio value="custom">自定义</el-radio>
    </el-radio-group>
  </el-form-item>

  <!-- 操作按钮 -->
  <el-button @click="loadData">刷新数据</el-button>
  <el-button @click="batchSetShortlist">批量设置入围</el-button>
  <el-button @click="exportList">导出名单</el-button>
</el-card>
```

### 2. 统计信息区

```vue
<el-card>
  <el-row :gutter="20">
    <el-col :span="4">
      <el-statistic title="总项目数" :value="totalCount" />
    </el-col>
    <el-col :span="4">
      <el-statistic title="已完成书审" :value="completedBookCount" />
    </el-col>
    <el-col :span="4">
      <el-statistic title="已完成面谈" :value="completedInterviewCount" />
    </el-col>
    <el-col :span="4">
      <el-statistic title="当前入围数" :value="shortlistedCount">
        <template #suffix>
          <span>({{ shortlistRatio }}%)</span>
        </template>
      </el-statistic>
    </el-col>
    <el-col :span="4">
      <el-statistic title="手动增补" :value="manualAddCount" />
    </el-col>
  </el-row>
</el-card>
```

### 3. 项目列表区

```vue
<el-table :data="projects" border stripe>
  <!-- 综合排名 -->
  <el-table-column prop="rank" label="综合排名" width="90" align="center">
    <template #default="{ row }">
      <el-tag v-if="row.rank <= 3" :type="getRankTagType(row.rank)">
        {{ row.rank }}
      </el-tag>
      <span v-else>{{ row.rank }}</span>
    </template>
  </el-table-column>

  <!-- 得分详情 -->
  <el-table-column label="得分详情" width="150" align="center">
    <template #default="{ row }">
      <div>书审: {{ row.bookScore?.toFixed(1) || '-' }}</div>
      <div>面谈: {{ row.interviewScore?.toFixed(1) || '-' }}</div>
    </template>
  </el-table-column>

  <!-- 项目信息 -->
  <el-table-column prop="projectName" label="项目名称" min-width="200" />
  <el-table-column prop="institutionName" label="医疗机构" min-width="180" />
  <el-table-column prop="groupType" label="组别" width="100" />

  <!-- 综合得分 -->
  <el-table-column prop="compositeScore" label="综合得分" width="120" align="center">
    <template #default="{ row }">
      <span v-if="row.compositeScore !== null" style="font-weight: bold; font-size: 16px">
        {{ row.compositeScore.toFixed(1) }}
      </span>
      <span v-else style="color: #909399">待面谈</span>
    </template>
  </el-table-column>

  <!-- 入围状态 -->
  <el-table-column label="入围状态" width="120" align="center">
    <template #default="{ row }">
      <el-tag :type="getShortlistTagType(row)">
        {{ getShortlistLabel(row) }}
      </el-tag>
    </template>
  </el-table-column>

  <!-- 操作 -->
  <el-table-column label="操作" width="220" align="center" fixed="right">
    <template #default="{ row }">
      <el-button size="small" @click="viewDetail(row)">查看详情</el-button>
      <el-button
        v-if="row.isShortlisted"
        size="small"
        type="warning"
        @click="toggleShortlist(row, false)"
      >
        取消入围
      </el-button>
      <el-button
        v-else
        size="small"
        type="success"
        @click="toggleShortlist(row, true)"
      >
        增补入围
      </el-button>
    </template>
  </el-table-column>
</el-table>
```

---

## ✅ API需求总结

### 优先级1（必需）

| API | 接口 | 用途 | 状态 |
|-----|------|------|------|
| 书审排名 | `GET /api/admin/reviews/rankings?stage=BOOK` | 获取所有项目的书审得分 | ⚠️ 待确认 |
| 面谈排名 | `GET /api/admin/reviews/rankings?stage=INTERVIEW` | 获取所有项目的面谈得分 | ⚠️ 待确认 |

### 优先级2（建议）

| API | 接口 | 用途 | 状态 |
|-----|------|------|------|
| 评审详情 | `GET /api/registrations/{id}/review-details` | 查看项目详细评分和评委意见 | ⚠️ 待确认 |

---

## 📝 后端开发建议

### 1. 书审排名接口

**实现要点**:
```java
@GetMapping("/admin/reviews/rankings")
public ResponseEntity<ApiResponse<List<RankingItem>>> getRankings(
    @RequestParam Long competitionId,
    @RequestParam String stage  // BOOK or INTERVIEW
) {
    // 1. 获取该赛事该阶段的所有评审任务
    List<ReviewTask> tasks = reviewTaskService.findByCompetitionAndStage(competitionId, stage);
    
    // 2. 按 registrationId 分组，计算平均分
    Map<Long, RankingItem> rankings = new HashMap<>();
    
    for (ReviewTask task : tasks) {
        Long regId = task.getRegistrationId();
        
        if (!rankings.containsKey(regId)) {
            Registration reg = registrationService.findById(regId);
            RankingItem item = new RankingItem();
            item.setRegistrationId(regId);
            item.setProjectName(reg.getProjectName());
            item.setInstitutionName(reg.getInstitution().getName());
            item.setGroupType(reg.getGroupType());
            item.setScores(new ArrayList<>());
            rankings.put(regId, item);
        }
        
        // 添加该评委的评分
        ReviewScore score = reviewScoreService.findByTaskId(task.getId());
        if (score != null) {
            rankings.get(regId).getScores().add(score);
        }
    }
    
    // 3. 计算每个项目的平均分
    List<RankingItem> result = new ArrayList<>();
    for (RankingItem item : rankings.values()) {
        item.calculateAverages();  // 计算各项平均分
        result.add(item);
    }
    
    // 4. 按平均总分降序排序
    result.sort((a, b) -> Double.compare(b.getAvgTotal(), a.getAvgTotal()));
    
    return ResponseEntity.ok(ApiResponse.success(result));
}
```

### 2. RankingItem DTO

```java
@Data
public class RankingItem {
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private String groupType;
    
    // 平均分
    private Double avgTotal;
    private Double avgPlan;
    private Double avgProblem;
    private Double avgAction;
    private Double avgSuccess;
    private Double avgReview;
    private Double avgOperation;
    private Double avgPresentation;
    
    // 评委意见汇总
    private List<String> highlights;
    private List<String> weaknesses;
    
    // 临时存储所有评分
    @JsonIgnore
    private List<ReviewScore> scores;
    
    public void calculateAverages() {
        if (scores == null || scores.isEmpty()) {
            return;
        }
        
        int count = scores.size();
        avgPlan = scores.stream().mapToInt(ReviewScore::getPlan).average().orElse(0);
        avgProblem = scores.stream().mapToInt(ReviewScore::getProblem).average().orElse(0);
        avgAction = scores.stream().mapToInt(ReviewScore::getAction).average().orElse(0);
        avgSuccess = scores.stream().mapToInt(ReviewScore::getSuccess).average().orElse(0);
        avgReview = scores.stream().mapToInt(ReviewScore::getReview).average().orElse(0);
        avgOperation = scores.stream().mapToInt(ReviewScore::getOperation).average().orElse(0);
        avgPresentation = scores.stream().mapToInt(ReviewScore::getPresentation).average().orElse(0);
        
        avgTotal = avgPlan + avgProblem + avgAction + avgSuccess + avgReview + avgOperation + avgPresentation;
        
        // 汇总亮点和建议
        highlights = scores.stream()
            .map(ReviewScore::getHighlight)
            .filter(s -> s != null && !s.isEmpty())
            .collect(Collectors.toList());
        
        weaknesses = scores.stream()
            .map(ReviewScore::getWeakness)
            .filter(s -> s != null && !s.isEmpty())
            .collect(Collectors.toList());
    }
}
```

---

## 🎯 前端开发计划

### 阶段1: API确认（当前阶段）
- [x] 理解需求
- [x] 设计前端逻辑
- [x] 编写API测试脚本
- [x] 生成API需求文档
- [ ] **等待后端确认API可用性** ⬅️ 您在这里

### 阶段2: 前端开发（后端API确认后）
- [ ] 创建入围管理页面组件
- [ ] 实现数据加载和合并逻辑
- [ ] 实现权重配置功能
- [ ] 实现入围比例设置
- [ ] 实现个别增补功能
- [ ] 实现详情查看
- [ ] 实现导出功能

### 阶段3: 测试和优化
- [ ] 功能测试
- [ ] 边界情况测试
- [ ] 性能优化
- [ ] UI/UX优化

---

## 🔍 API测试清单

### 请后端开发者确认以下内容：

#### ✅ 书审排名API

- [ ] 接口是否已实现：`GET /api/admin/reviews/rankings?competitionId=21&stage=BOOK`
- [ ] 返回的数据结构是否包含以下必需字段：
  - [ ] `registrationId`
  - [ ] `projectName`
  - [ ] `institutionName`
  - [ ] `groupType`
  - [ ] `avgTotal`（核心字段）
- [ ] 如果某个项目没有评审得分，是否会被排除在外，还是返回空分数？

#### ✅ 面谈排名API

- [ ] 接口是否已实现：`GET /api/admin/reviews/rankings?competitionId=21&stage=INTERVIEW`
- [ ] 返回的数据结构是否与书审API一致？
- [ ] 如果面谈阶段未开始，返回空数组 `[]` 还是报错？
- [ ] 是否只返回**进阶组**的项目？

#### ✅ 评审详情API

- [ ] 接口是否已实现：`GET /api/registrations/{registrationId}/review-details`
- [ ] 返回的数据是否包含书审和面谈两个阶段的详情？
- [ ] 数据结构中的 `stage` 字段是否为 `"BOOK"` 或 `"INTERVIEW"`？

---

## 📋 反馈给后端的问题清单

### 问题1: 书审排名API是否存在？
- **期望**: `GET /api/admin/reviews/rankings?competitionId=21&stage=BOOK`
- **是否需要新增**: 是 / 否
- **如果已存在，当前接口路径**: ___________

### 问题2: 面谈排名API是否存在？
- **期望**: `GET /api/admin/reviews/rankings?competitionId=21&stage=INTERVIEW`
- **是否需要新增**: 是 / 否
- **如果已存在，当前接口路径**: ___________

### 问题3: 评审详情API是否存在？
- **期望**: `GET /api/registrations/{registrationId}/review-details`
- **是否需要新增**: 是 / 否
- **如果已存在，当前接口路径**: ___________

### 问题4: 数据结构确认
- **书审/面谈排名的返回结构是否符合文档中的 `RankingItem` 结构？**
- **如果不符合，请提供当前实际的返回结构示例**

### 问题5: 特殊情况处理
- **如果某个项目没有任何评审得分，该项目是否还会出现在排名列表中？**
  - [ ] 是（avgTotal = null 或 0）
  - [ ] 否（不出现在列表中）
- **如果面谈阶段未开始，面谈排名API返回什么？**
  - [ ] 空数组 `[]`
  - [ ] 错误信息
  - [ ] 其他: ___________

---

## 🚀 下一步行动

### 后端团队：
1. **阅读本文档**，确认API需求是否清晰
2. **确认以上3个API是否已实现**，或需要新增
3. **如果已实现，提供测试用例**（curl命令或Postman collection）
4. **如果需要新增，预估开发时间**
5. **完成开发后，通知前端团队进行联调**

### 前端团队（我）：
1. **等待后端确认**API可用性
2. **收到确认后，运行测试脚本**验证API
3. **如果API符合预期，立即开始前端开发**
4. **预计前端开发时间：1-2天**

---

## 📞 联系方式

**问题反馈**:
- 如有任何疑问，请直接回复此文档
- 或联系前端负责人

**文档状态**:
- ✅ 前端需求已明确
- ⚠️ 等待后端API确认
- ⏳ 前端开发准备就绪

---

**生成时间**: 2026-02-07  
**版本**: v1.0  
**状态**: 等待后端反馈 ⏳
