# 书审分组和面谈分组页面 - API性能测试报告

## 测试时间
2026-03-01

## 测试环境
- 后端服务: http://localhost:6031
- 测试账号: OPS (13800000005)
- 赛事ID: 1 (2026浙江省品管大赛)
- 超时设置: 60秒

---

## 测试结果汇总

### 书审分组页面 (src/views/committee/book/Registration.vue)

| 测试场景 | 响应时间 | 性能评级 | 数据量 | 状态 |
|---------|---------|---------|--------|------|
| 无筛选条件 | 4.579秒 | 🔴 较慢 | 64条 | ✅ 成功 |
| 按竞赛组别筛选 (BASIC) | 1.837秒 | 🟠 一般 | 23条 | ✅ 成功 |
| 按分组筛选 (A1) | 0.991秒 | 🟡 良好 | 12条 | ✅ 成功 |
| 按机构名称筛选 | 4.331秒 | 🔴 较慢 | 62条 | ✅ 成功 |
| 多条件组合筛选 | 0.858秒 | 🟡 良好 | 11条 | ✅ 成功 |

**统计:**
- 平均响应时间: 2.519秒
- 最快: 0.858秒
- 最慢: 4.579秒

---

### 面谈分组页面 (src/views/committee/interview/Group.vue)

| 测试场景 | 响应时间 | 性能评级 | 数据量 | 状态 |
|---------|---------|---------|--------|------|
| 进阶组无筛选 | 1.809秒 | 🟠 一般 | 22条 | ✅ 成功 |
| 进阶组按分组筛选 (C1) | 1.425秒 | 🟠 一般 | 13条 | ✅ 成功 |
| 进阶组按机构筛选 | 1.615秒 | 🟠 一般 | 22条 | ✅ 成功 |
| 进阶组多条件筛选 | 0.998秒 | 🟡 良好 | 13条 | ✅ 成功 |

**统计:**
- 平均响应时间: 1.462秒
- 最快: 0.998秒
- 最慢: 1.809秒

---

## 性能评级标准

| 评级 | 响应时间 | 用户体验 |
|-----|---------|---------|
| 🟢 优秀 | < 0.5秒 | 非常流畅 |
| 🟡 良好 | 0.5-1.0秒 | 流畅 |
| 🟠 一般 | 1.0-2.0秒 | 可接受 |
| 🔴 较慢 | 2.0-5.0秒 | 体验一般 |
| ⚫ 很慢 | > 5.0秒 | 体验差 |

---

## 问题分析

### 1. 慢查询场景

#### 🔴 书审分组 - 无筛选条件 (4.579秒)
**问题**: 
- 加载所有报名数据，无任何筛选条件
- 这是用户打开页面时的默认场景
- 响应时间超过4秒，严重影响用户体验

**影响**: 
- 用户打开书审分组页面时需要等待4.5秒
- 页面显示空白或加载状态时间过长
- 用户可能认为系统卡死

**原因推测**:
1. 全表扫描，没有有效的索引
2. 返回了过多不必要的字段
3. 可能存在N+1查询问题（关联查询机构、字典等）
4. 没有使用缓存

---

#### 🔴 书审分组 - 按机构名称筛选 (4.331秒)
**问题**:
- 模糊搜索机构名称包含"医院"的数据
- 响应时间4.3秒，几乎和无筛选一样慢

**影响**:
- 用户输入机构名称筛选时体验很差
- 这是常用的筛选场景

**原因推测**:
1. `institutionName` 字段没有索引
2. 使用了 `LIKE '%医院%'` 这样的模糊查询，无法使用索引
3. 可能需要关联查询机构表

---

### 2. 性能一般的场景

#### 🟠 书审分组 - 按竞赛组别筛选 (1.837秒)
- 响应时间接近2秒
- 虽然可接受，但仍有优化空间

#### 🟠 面谈分组 - 所有场景 (1.4-1.8秒)
- 面谈分组固定为进阶组，数据量较小
- 但响应时间仍在1.4-1.8秒之间
- 说明即使数据量小，查询效率也不高

---

### 3. 性能良好的场景

#### 🟡 多条件组合筛选 (0.858-0.998秒)
- 当筛选条件越多，响应时间反而越快
- 说明多条件可以缩小查询范围
- 但仍未达到优秀级别（<0.5秒）

---

## 根本原因分析

### 1. 数据库层面

#### 缺少索引
```sql
-- 当前可能缺少的索引
CREATE INDEX idx_registration_competition_id ON registrations(competition_id);
CREATE INDEX idx_registration_group_type ON registrations(group_type);
CREATE INDEX idx_registration_group_code ON registrations(group_code);
CREATE INDEX idx_registration_institution_name ON registrations(institution_name);

-- 组合索引（更高效）
CREATE INDEX idx_registration_filter ON registrations(competition_id, group_type, group_code);
```

#### 模糊查询问题
```sql
-- 当前可能的查询（无法使用索引）
SELECT * FROM registrations 
WHERE institution_name LIKE '%医院%';

-- 优化方案1: 使用全文索引
CREATE FULLTEXT INDEX idx_institution_name_fulltext ON registrations(institution_name);

-- 优化方案2: 使用前缀匹配（如果适用）
WHERE institution_name LIKE '医院%';  -- 可以使用索引
```

#### N+1查询问题
```java
// 可能存在的问题代码
List<Registration> registrations = registrationRepository.findAll();
for (Registration reg : registrations) {
    // 每次循环都查询一次数据库
    Institution inst = institutionRepository.findById(reg.getInstitutionId());
    reg.setInstitutionName(inst.getName());
    
    Dictionary method = dictionaryRepository.findByCode(reg.getMethodCode());
    reg.setMethodLabel(method.getLabel());
}

// 优化方案: 使用JOIN或批量查询
@Query("SELECT r FROM Registration r " +
       "LEFT JOIN FETCH r.institution " +
       "LEFT JOIN FETCH r.method " +
       "WHERE r.competitionId = :competitionId")
List<Registration> findWithDetails(@Param("competitionId") Long competitionId);
```

---

### 2. 应用层面

#### 返回字段过多
```java
// 当前可能返回了所有字段
public class RegistrationDTO {
    // 14个字段，包括可能不需要的
    private Long id;
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private String institutionLevel;
    private String groupType;
    private String groupCode;
    private LocalDateTime submittedAt;
    private String subjectTypeCode;
    private String methodCode;
    private String subjectTypeLabel;
    private String methodLabel;
    private String applicantName;
    private List<Material> materials;  // 可能包含大量数据
}

// 优化方案: 只返回列表页需要的字段
public class RegistrationListDTO {
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private String groupType;
    private String groupCode;
    private String methodLabel;
    private Integer materialCount;  // 只返回数量，不返回完整材料列表
}
```

#### 没有使用缓存
```java
// 优化方案: 缓存字典数据
@Cacheable(value = "dictionaries", key = "#type")
public List<Dictionary> getDictionaryByType(String type) {
    return dictionaryRepository.findByType(type);
}

// 优化方案: 缓存机构信息
@Cacheable(value = "institutions", key = "#id")
public Institution getInstitution(Long id) {
    return institutionRepository.findById(id);
}
```

---

## 优化建议

### 短期优化（立即可做）

#### 1. 添加数据库索引 ⭐⭐⭐⭐⭐
**优先级**: 最高  
**预期效果**: 响应时间减少50-70%

```sql
-- 单列索引
CREATE INDEX idx_registration_competition_id ON registrations(competition_id);
CREATE INDEX idx_registration_group_type ON registrations(group_type);
CREATE INDEX idx_registration_group_code ON registrations(group_code);

-- 组合索引（推荐）
CREATE INDEX idx_registration_filter 
ON registrations(competition_id, group_type, group_code);

-- 全文索引（用于机构名称搜索）
CREATE FULLTEXT INDEX idx_institution_name_fulltext 
ON registrations(institution_name);
```

#### 2. 优化查询，避免N+1问题 ⭐⭐⭐⭐⭐
**优先级**: 最高  
**预期效果**: 响应时间减少30-50%

```java
// 使用JOIN FETCH一次性加载关联数据
@Query("SELECT r FROM Registration r " +
       "LEFT JOIN FETCH r.institution " +
       "WHERE r.competitionId = :competitionId")
List<Registration> findWithInstitution(@Param("competitionId") Long competitionId);
```

#### 3. 减少返回字段 ⭐⭐⭐⭐
**优先级**: 高  
**预期效果**: 响应时间减少10-20%

- 列表页不返回完整的材料列表，只返回材料数量
- 不返回不必要的字段
- 使用DTO投影，只查询需要的字段

#### 4. 前端添加加载提示 ⭐⭐⭐
**优先级**: 中  
**预期效果**: 改善用户体验

```vue
<el-table v-loading="loading" loading-text="正在加载数据，请稍候...">
```

---

### 中期优化（1-2周内）

#### 5. 使用Redis缓存 ⭐⭐⭐⭐
**优先级**: 高  
**预期效果**: 响应时间减少20-40%

```java
// 缓存字典数据（很少变化）
@Cacheable(value = "dictionaries", key = "#type")
public List<Dictionary> getDictionaryByType(String type);

// 缓存机构信息（很少变化）
@Cacheable(value = "institutions", key = "#id")
public Institution getInstitution(Long id);

// 缓存热点查询（设置较短过期时间）
@Cacheable(value = "registrations", key = "#competitionId + '_' + #groupType", 
           unless = "#result == null", expire = 300)  // 5分钟过期
public List<Registration> getRegistrations(Long competitionId, String groupType);
```

#### 6. 分页优化 ⭐⭐⭐
**优先级**: 中  
**预期效果**: 减少单次数据量

- 当前每页50条，考虑减少到20-30条
- 使用游标分页代替偏移分页（大数据量时更高效）

#### 7. 异步加载材料信息 ⭐⭐⭐
**优先级**: 中  
**预期效果**: 首屏加载更快

- 列表页先加载基本信息
- 材料信息按需异步加载（点击"查看"时再加载）

---

### 长期优化（1个月以上）

#### 8. 数据库读写分离 ⭐⭐⭐⭐
**优先级**: 中  
**预期效果**: 提升并发能力

- 查询操作走从库
- 写入操作走主库

#### 9. 使用Elasticsearch ⭐⭐⭐⭐
**优先级**: 中  
**预期效果**: 搜索性能大幅提升

- 特别适合机构名称、项目名称的模糊搜索
- 支持全文检索和高亮显示

#### 10. 前端虚拟滚动 ⭐⭐⭐
**优先级**: 低  
**预期效果**: 大数据量时渲染更流畅

- 只渲染可见区域的数据
- 适合数据量很大的场景

---

## 立即行动计划

### 第一步: 添加索引（预计耗时: 10分钟）

```sql
-- 在数据库中执行
CREATE INDEX idx_registration_competition_id ON registrations(competition_id);
CREATE INDEX idx_registration_group_type ON registrations(group_type);
CREATE INDEX idx_registration_group_code ON registrations(group_code);
CREATE INDEX idx_registration_filter ON registrations(competition_id, group_type, group_code);
```

**预期效果**: 
- 无筛选条件: 4.5秒 → 1.5秒
- 按机构筛选: 4.3秒 → 2.0秒
- 其他场景: 1.8秒 → 0.5秒

---

### 第二步: 检查并优化N+1查询（预计耗时: 30分钟）

1. 在后端代码中搜索 `filterRegistrations` 方法
2. 检查是否使用了 `JOIN FETCH` 或批量查询
3. 如果没有，添加关联查询

**预期效果**:
- 所有场景响应时间再减少30-50%

---

### 第三步: 减少返回字段（预计耗时: 20分钟）

1. 创建专门的列表DTO
2. 只返回列表页需要的字段
3. 材料列表改为材料数量

**预期效果**:
- 所有场景响应时间再减少10-20%

---

## 预期优化效果

### 优化前 vs 优化后

| 场景 | 优化前 | 优化后（预期） | 改善 |
|-----|-------|--------------|------|
| 书审-无筛选 | 4.579秒 | 0.5-0.8秒 | 83-89% ⬇️ |
| 书审-机构筛选 | 4.331秒 | 0.8-1.2秒 | 72-82% ⬇️ |
| 书审-组别筛选 | 1.837秒 | 0.3-0.5秒 | 73-84% ⬇️ |
| 书审-多条件 | 0.858秒 | 0.2-0.3秒 | 65-77% ⬇️ |
| 面谈-无筛选 | 1.809秒 | 0.3-0.5秒 | 72-83% ⬇️ |
| 面谈-多条件 | 0.998秒 | 0.2-0.3秒 | 70-80% ⬇️ |

**总体目标**: 所有场景响应时间控制在1秒以内，大部分场景在0.5秒以内

---

## 监控建议

### 1. 添加性能监控
```java
@Slf4j
@Aspect
@Component
public class PerformanceMonitor {
    @Around("execution(* com.example.controller.*.*(..))")
    public Object monitor(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = pjp.proceed();
        long elapsed = System.currentTimeMillis() - start;
        
        if (elapsed > 1000) {
            log.warn("慢查询: {} 耗时 {}ms", pjp.getSignature(), elapsed);
        }
        
        return result;
    }
}
```

### 2. 数据库慢查询日志
```sql
-- MySQL配置
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- 记录超过1秒的查询
```

### 3. 前端性能监控
```javascript
// 记录API响应时间
const startTime = performance.now()
const res = await filterRegistrations(params)
const elapsed = performance.now() - startTime

if (elapsed > 1000) {
  console.warn(`慢查询: ${elapsed.toFixed(0)}ms`, params)
}
```

---

## 结论

1. **当前问题**: 书审分组和面谈分组页面响应时间普遍较慢，特别是无筛选条件和机构名称筛选场景，响应时间超过4秒，严重影响用户体验。

2. **主要原因**: 
   - 缺少数据库索引
   - 可能存在N+1查询问题
   - 返回字段过多
   - 没有使用缓存

3. **优化方向**: 
   - 立即添加数据库索引（最重要）
   - 优化查询避免N+1问题
   - 减少返回字段
   - 使用Redis缓存

4. **预期效果**: 通过以上优化，可以将响应时间降低70-85%，大部分场景控制在0.5秒以内，显著改善用户体验。

---

**报告生成时间**: 2026-03-01  
**测试人员**: Kiro AI Assistant  
**建议优先级**: 🔴 高优先级，建议立即优化
