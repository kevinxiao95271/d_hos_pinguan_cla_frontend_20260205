# ✅ 已修复：使用正确的 API 接口

## 📋 问题总结

之前前端使用了 `/api/registrations` 接口，该接口**缺少关键字段**：
- ❌ registrationId (项目编号)
- ❌ institutionName (医疗机构名称)
- ❌ methodLabel (品管工具)
- ❌ applicantName (报名人)

**正确的接口**是 `/api/admin/registrations/filter`，该接口包含所有需要的字段。

---

## ✅ 已完成的修改

### 1. BookStage.vue（书审阶段）

**改动**：
```javascript
// 之前（错误）
import { getRegistrations } from '@/api/registration'
const res = await getRegistrations(params)

// 现在（正确）
import { filterRegistrations } from '@/api/admin'
const res = await filterRegistrations(registrationFilters)
```

**表格列已恢复**：
- ✅ 项目名称
- ✅ 项目编号 (registrationId)
- ✅ 医疗机构名称 (institutionName)
- ✅ 竞赛组别
- ✅ 分组
- ✅ 品管工具 (methodLabel)
- ✅ 报名人 (applicantName)
- ✅ 报名时间

---

### 2. Statistics.vue（报名统计）

**改动**：
```javascript
// 之前（错误）
import { getRegistrations } from '@/api/registration'
const res = await getRegistrations({ competitionId })

// 现在（正确）
import { filterRegistrations } from '@/api/admin'
const res = await filterRegistrations({ competitionId })
```

---

## 🔄 需要执行的操作

### ⚠️ 重要：必须重启后端服务

根据您提供的信息，`/api/admin/registrations/filter` 接口已经有这些字段了。

**如果后端最近有更新，需要重启后端进程才能生效！**

#### 重启步骤：

1. **停止后端**：
   ```bash
   # 方式1: 使用批处理脚本
   ./stop_backend.bat
   
   # 方式2: 手动查找并结束进程
   netstat -ano | findstr :6031
   taskkill /F /PID <进程ID>
   ```

2. **启动后端**：
   ```bash
   cd D:\AiCode\traegj\d_hos_pinguan_traegj_backend_20260205
   mvn spring-boot:run
   ```

3. **等待启动完成**（10-30秒），看到：
   ```
   Started Application in X seconds
   ```

---

### 🌐 刷新前端页面

1. **硬刷新浏览器**：
   - Windows: `Ctrl + Shift + R` 或 `Ctrl + F5`
   - Mac: `Cmd + Shift + R`

2. **重新登录**

3. **进入"书审阶段 > 报名与分组"**

---

## ✅ 预期结果

### 控制台日志

应该看到：

```javascript
📥 正在加载报名列表...
📥 使用接口: /api/admin/registrations/filter
📥 报名列表响应: {success: true, data: Array(33)}
✅ 报名列表加载成功: 33 条
```

### 列表显示

应该能看到**完整的表格**，包含：

| 项目名称 | 项目编号 | 医疗机构名称 | 竞赛组别 | 分组 | 品管工具 | 报名人 | 报名时间 |
|---------|---------|-------------|---------|------|---------|--------|---------|
| 改善就医体验... | BM20260106 | 浙江省人民医院 | 基层组 | A1 | 品管圈-课题达成 | 张三 | 2026-02-04 |

---

## 🧪 验证接口

后端重启后，可以运行测试脚本验证：

```bash
python test_admin_filter.py
```

**预期输出**：
```
[OK] 所有关键字段都存在！
  registrationId = BM20260106
  institutionName = 浙江省人民医院
  methodLabel = 品管圈-课题达成
  applicantName = 张三
```

---

## 📊 接口对比

### `/api/registrations` (旧接口，字段不全)

```json
{
  "id": 106,
  "projectName": "...",
  "groupType": "BASIC",
  "groupCode": "A1",
  "status": "APPROVED",
  "submittedAt": "...",
  "createdAt": "..."
}
```

### `/api/admin/registrations/filter` (新接口，字段完整) ⭐

```json
{
  "id": 106,
  "registrationId": "BM20260106",        // ✓
  "projectName": "...",
  "institutionName": "浙江省人民医院",    // ✓
  "methodLabel": "品管圈-课题达成",        // ✓
  "applicantName": "张三",                // ✓
  "subjectTypeLabel": "教育训练",         // ✓
  "groupType": "BASIC",
  "groupCode": "A1",
  "status": "APPROVED",
  "submittedAt": "...",
  "createdAt": "..."
}
```

---

## 🔧 故障排查

### 问题1: 仍然返回 401

**原因**：后端未重启，或权限配置未生效

**解决**：
1. 确认后端已完全停止
2. 重新启动后端
3. 等待启动完成（看到 "Started Application"）
4. 清除浏览器缓存并重新登录

---

### 问题2: 仍然缺少字段

**原因**：前端代码未更新或浏览器缓存

**解决**：
1. 确认 `BookStage.vue` 使用 `filterRegistrations`
2. 硬刷新浏览器 (Ctrl+Shift+R)
3. 查看 Network 标签，确认调用的是 `/admin/registrations/filter`

---

### 问题3: 控制台显示 "暂无数据"

**原因**：competitionId 可能不对

**解决**：
```javascript
// 在浏览器控制台执行
localStorage.setItem('currentCompetitionId', '21')
location.reload()
```

---

## 📝 修改文件列表

- ✅ `src/views/committee/BookStage.vue` - 改用 filterRegistrations
- ✅ `src/views/committee/Statistics.vue` - 改用 filterRegistrations
- ✅ `src/api/admin.js` - filterRegistrations 已存在

---

## 🎯 总结

1. ✅ 前端已修改为使用正确的 API
2. ⏳ **需要重启后端服务**
3. ⏳ 重启后刷新前端页面
4. ✅ 应该能看到完整的 33 条数据和所有列

---

**创建时间**: 2026-02-06  
**状态**: 等待后端重启验证
