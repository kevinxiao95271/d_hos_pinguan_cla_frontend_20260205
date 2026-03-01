# 报名统计页面 - 组别统计数据缺失问题

## 问题描述
报名统计页面的"组别统计"表格显示"暂无数据"，但之前是有数据的。

**页面位置**: 委员会 → 报名统计  
**文件**: `src/views/committee/Statistics.vue`

---

## 问题分析

### 前端期望的数据结构

**代码位置**: `src/views/committee/Statistics.vue` 第47-66行

```vue
<el-table :data="stats.groupTypeStats" border stripe>
  <el-table-column prop="groupTypeName" label="组别" />
  <el-table-column prop="institutionCount" label="机构数" />
  <el-table-column prop="projectCount" label="项目数" />
  <el-table-column prop="projectPercentage" label="项目占比" />
  <el-table-column prop="avgProjectsPerInstitution" label="平均项目/机构" />
</el-table>
```

**前端期望的数据格式**:
```javascript
stats.groupTypeStats = [
  {
    groupTypeName: "基层组",
    institutionCount: 50,
    projectCount: 80,
    projectPercentage: 40.0,
    avgProjectsPerInstitution: 1.6
  },
  {
    groupTypeName: "综合组",
    institutionCount: 30,
    projectCount: 60,
    projectPercentage: 30.0,
    avgProjectsPerInstitution: 2.0
  },
  {
    groupTypeName: "进阶组",
    institutionCount: 25,
    projectCount: 60,
    projectPercentage: 30.0,
    avgProjectsPerInstitution: 2.4
  }
]
```

---

### 后端实际返回的数据

**API**: `GET /api/admin/stats/summary?competitionId=1`

**实际返回的字段**:
```json
{
  "competitionId": 1,
  "competitionName": "2026浙江省品管大赛",
  "registrationCount": 123,
  "toolTypeCount": 24,
  "reviewerCount": 127,
  "reviewerInstitutionCount": 69,
  "bookReviewTaskCount": 0,
  "bookReviewUnscoredCount": 0,
  "regionCounts": { ... },
  "subjectTypeCounts": { ... },
  "methodCounts": { ... },
  "leaderTitleCounts": { ... },
  "avgPlan": 0.0,
  "avgProblem": 0.0,
  "avgAction": 0.0,
  "avgSuccess": 0.0,
  "avgReview": 0.0,
  "avgOperation": 0.0,
  "avgPresentation": 0.0
}
```

**问题**: ❌ **缺少 `groupTypeStats` 字段**

---

## 根本原因

### 可能的原因

1. **后端优化时移除了该字段**
   - 在优化N+1查询时，可能移除了组别统计的计算逻辑
   - 或者字段名称发生了变化

2. **字段名称不匹配**
   - 后端可能使用了不同的字段名
   - 例如: `groupStats`, `groupTypeStatistics`, `groupTypeSummary` 等

3. **数据计算逻辑缺失**
   - 后端没有实现组别统计的计算
   - 需要从报名数据中聚合计算

---

## 影响范围

### 受影响的功能
- ❌ 组别统计表格显示"暂无数据"
- ✅ 其他统计数据正常（地区分布、主题类型、品管工具等）
- ✅ 总览卡片正常（报名总数、机构总数等）

### 用户体验
- 用户无法查看各组别的统计信息
- 无法了解各组别的机构数、项目数、占比等关键指标

---

## 解决方案

### 方案1: 后端添加 groupTypeStats 字段（推荐）

**后端需要返回**:
```java
@Data
public class StatsSummary {
    // ... 现有字段
    
    // 新增：组别统计
    private List<GroupTypeStat> groupTypeStats;
}

@Data
public class GroupTypeStat {
    private String groupTypeName;        // 组别名称：基层组、综合组、进阶组
    private Integer institutionCount;    // 机构数
    private Integer projectCount;        // 项目数
    private Double projectPercentage;    // 项目占比
    private Double avgProjectsPerInstitution;  // 平均项目/机构
}
```

**计算逻辑**:
```java
public List<GroupTypeStat> calculateGroupTypeStats(Long competitionId) {
    List<GroupTypeStat> stats = new ArrayList<>();
    
    // 查询所有报名数据
    List<Registration> registrations = registrationRepository
        .findByCompetitionId(competitionId);
    
    int totalCount = registrations.size();
    
    // 按组别分组统计
    Map<String, List<Registration>> groupedByType = registrations.stream()
        .collect(Collectors.groupingBy(Registration::getGroupType));
    
    for (Map.Entry<String, List<Registration>> entry : groupedByType.entrySet()) {
        String groupType = entry.getKey();
        List<Registration> groupRegs = entry.getValue();
        
        // 统计机构数（去重）
        long institutionCount = groupRegs.stream()
            .map(Registration::getInstitutionId)
            .distinct()
            .count();
        
        // 项目数
        int projectCount = groupRegs.size();
        
        // 项目占比
        double percentage = totalCount > 0 ? 
            (projectCount * 100.0 / totalCount) : 0.0;
        
        // 平均项目/机构
        double avgProjects = institutionCount > 0 ? 
            (projectCount * 1.0 / institutionCount) : 0.0;
        
        GroupTypeStat stat = new GroupTypeStat();
        stat.setGroupTypeName(getGroupTypeName(groupType));
        stat.setInstitutionCount((int) institutionCount);
        stat.setProjectCount(projectCount);
        stat.setProjectPercentage(percentage);
        stat.setAvgProjectsPerInstitution(avgProjects);
        
        stats.add(stat);
    }
    
    // 按组别排序：基层组、综合组、进阶组
    stats.sort(Comparator.comparing(GroupTypeStat::getGroupTypeName));
    
    return stats;
}

private String getGroupTypeName(String groupType) {
    switch (groupType) {
        case "BASIC": return "基层组";
        case "COMPREHENSIVE": return "综合组";
        case "ADVANCED": return "进阶组";
        default: return groupType;
    }
}
```

---

### 方案2: 前端从现有数据计算（临时方案）

如果后端暂时无法修改，前端可以从报名列表数据中计算：

```javascript
// 需要调用报名列表API获取完整数据
const calculateGroupTypeStats = (registrations) => {
  const totalCount = registrations.length
  
  // 按组别分组
  const grouped = {}
  registrations.forEach(reg => {
    const type = reg.groupType
    if (!grouped[type]) {
      grouped[type] = []
    }
    grouped[type].push(reg)
  })
  
  // 计算统计数据
  const stats = []
  for (const [type, regs] of Object.entries(grouped)) {
    // 统计机构数（去重）
    const institutions = new Set(regs.map(r => r.institutionId))
    const institutionCount = institutions.size
    
    // 项目数
    const projectCount = regs.length
    
    // 项目占比
    const projectPercentage = totalCount > 0 ? 
      (projectCount * 100.0 / totalCount) : 0
    
    // 平均项目/机构
    const avgProjectsPerInstitution = institutionCount > 0 ? 
      (projectCount / institutionCount) : 0
    
    stats.push({
      groupTypeName: getGroupTypeName(type),
      institutionCount,
      projectCount,
      projectPercentage,
      avgProjectsPerInstitution
    })
  }
  
  return stats
}
```

**缺点**:
- 需要额外调用报名列表API
- 增加前端计算负担
- 可能影响性能

---

## 推荐方案

### ✅ 方案1: 后端添加 groupTypeStats 字段

**理由**:
1. 统计数据应该由后端计算，前端只负责展示
2. 后端可以使用数据库聚合查询，性能更好
3. 保持API的完整性和一致性
4. 前端代码无需修改

**优先级**: 🔴 高（影响用户查看关键统计数据）

---

## 测试验证

### 后端修改后需要验证

1. **API返回数据包含 groupTypeStats**
```bash
curl -X GET "http://localhost:6031/api/admin/stats/summary?competitionId=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

期望返回:
```json
{
  "competitionId": 1,
  "competitionName": "2026浙江省品管大赛",
  "registrationCount": 123,
  "groupTypeStats": [
    {
      "groupTypeName": "基层组",
      "institutionCount": 50,
      "projectCount": 60,
      "projectPercentage": 48.8,
      "avgProjectsPerInstitution": 1.2
    },
    {
      "groupTypeName": "综合组",
      "institutionCount": 30,
      "projectCount": 40,
      "projectPercentage": 32.5,
      "avgProjectsPerInstitution": 1.33
    },
    {
      "groupTypeName": "进阶组",
      "institutionCount": 25,
      "projectCount": 23,
      "projectPercentage": 18.7,
      "avgProjectsPerInstitution": 0.92
    }
  ],
  // ... 其他字段
}
```

2. **前端页面显示正常**
   - 组别统计表格有数据
   - 各列数据正确显示
   - 百分比格式正确

---

## 相关信息

**前端文件**: `src/views/committee/Statistics.vue`  
**API**: `GET /api/admin/stats/summary`  
**后端方法**: `getStatsSummary()`  

**测试脚本**: `scripts/test_stats_grouptype.py`

---

**报告生成时间**: 2026-03-01  
**分析人员**: Kiro AI Assistant  
**状态**: ⚠️ 待后端修复
