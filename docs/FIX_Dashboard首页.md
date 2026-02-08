# ✅ Dashboard 首页修复完成

## 🔍 问题诊断

用户反馈：
1. ❌ Dashboard 首页"最近任务"列表中，**项目名称和医疗机构都没有数据**
2. ❌ 点击"开始评审"按钮后，**进入空页面**
3. ✅ 但是点击"评审任务"导航进入 Tasks.vue 是正常的

---

## 📊 根本原因

### 问题1: 使用了旧API
```javascript
// ❌ Dashboard.vue 第102行 - 使用旧API
const res = await getReviewTasks(userStore.userId)

// 问题：
// 1. getReviewTasks 需要手动传递 userId
// 2. 但 userStore.userId 可能为空
// 3. 导致 API 调用失败或返回空数据
```

### 问题2: 按钮没有传递完整参数
```javascript
// ❌ Dashboard.vue 第142-147行
const goToReview = (taskId) => {
  router.push(`/reviewer/review/${taskId}`)  // 只传了 taskId！
}

// 问题：
// 1. 只传了 taskId，没有传 registrationId
// 2. 没有传 projectName、institutionName、stage
// 3. Review.vue 收不到 registrationId，显示空页面
```

### 问题3: 模板传参错误
```javascript
// ❌ 模板中传的是 row.id，而不是 row
@click="goToReview(row.id)"  // 只传了ID

// 需要传整个 row 对象，才能提取完整信息
@click="goToReview(row)"
```

---

## 🔧 修复方案

### 修复1: 改用新API

**文件:** `src/views/reviewer/Dashboard.vue`

```javascript
// ✅ 导入新API
import { getMyReviewTasks } from '@/api/review'

// ✅ 使用新API（自动从token获取评委ID）
const loadData = async () => {
  try {
    const res = await getMyReviewTasks()  // ← 不需要传 userId
    if (res.success) {
      tasks.value = res.data || []
      console.log('Dashboard加载任务成功:', tasks.value.length)
    }
  } catch (error) {
    console.error('加载评审任务失败:', error)
  }
}
```

### 修复2: 传递完整参数

```javascript
// ✅ goToReview - 开始评审
const goToReview = (row) => {  // ← 接收完整 row 对象
  router.push({
    path: `/reviewer/review/${row.id}`,
    query: {
      registrationId: row.registrationId,      // ← 必须！
      projectName: row.projectName,            // ← 必须！
      institutionName: row.institutionName,    // ← 必须！
      stage: row.stage                         // ← 必须！
    }
  })
}

// ✅ viewReview - 查看已评审
const viewReview = (row) => {  // ← 接收完整 row 对象
  router.push({
    path: `/reviewer/review/${row.id}`,
    query: {
      registrationId: row.registrationId,
      projectName: row.projectName,
      institutionName: row.institutionName,
      stage: row.stage,
      isViewMode: 'true'  // ← 查看模式，不能编辑
    }
  })
}
```

### 修复3: 模板传递 row 对象

```vue
<!-- ✅ 传递完整 row 对象 -->
<el-button
  v-if="row.status === 'PENDING'"
  type="primary"
  size="small"
  @click="goToReview(row)"
>
  开始评审
</el-button>
<el-button
  v-else
  type="success"
  size="small"
  @click="viewReview(row)"
>
  查看
</el-button>
```

---

## ✅ 修复后的效果

### Dashboard 首页 - 最近任务列表
```
✅ 项目名称列：显示"护理交接班规范化-1"等
✅ 医疗机构列：显示"浙江大学医学院附属第一医院"等
✅ 评审阶段列：显示"书审"、"面谈"等
✅ 状态列：显示"待评审"、"已完成"等
✅ 操作列：
   - 待评审任务 → "开始评审"按钮 ✅
   - 已完成任务 → "查看"按钮 ✅
```

### 点击"开始评审"后
```
✅ 跳转到: /reviewer/review/115?registrationId=106&projectName=...
✅ 页面显示完整的项目信息
✅ 可以填写评分表单
✅ 可以查看项目详情
```

### 点击"查看"后（已完成任务）
```
✅ 跳转到: /reviewer/review/115?registrationId=106&...&isViewMode=true
✅ 页面显示完整的项目信息
✅ 表单为只读模式
✅ 可以查看已提交的评分
```

---

## 📋 完整修复清单

| 文件 | 行号 | 修改内容 | 状态 |
|-----|------|---------|------|
| Dashboard.vue | 80 | `getReviewTasks` → `getMyReviewTasks` | ✅ |
| Dashboard.vue | 102 | 删除 `userStore.userId` 参数 | ✅ |
| Dashboard.vue | 142-148 | `goToReview` 传递完整 row 对象 | ✅ |
| Dashboard.vue | 150-156 | `viewReview` 传递完整 row 对象 | ✅ |
| Dashboard.vue | 57 | `@click="goToReview(row.id)"` → `goToReview(row)` | ✅ |
| Dashboard.vue | 65 | `@click="viewReview(row.id)"` → `viewReview(row)` | ✅ |

---

## 🎯 现在请测试

### 步骤1: 刷新浏览器
```
Ctrl + Shift + R
```

### 步骤2: 重新登录
```
1. 访问: http://localhost:6039/login
2. 点击: "李明华(5任务)"
3. 点击: "登录"
```

### 步骤3: 查看Dashboard首页
```
登录后应该自动跳转到 Dashboard 首页

应该看到:
✅ 4个统计卡片（待评审、已评审、总任务数、完成率）
✅ "最近任务"表格显示数据:
   - 项目名称：有数据 ✅
   - 医疗机构：有数据 ✅
   - 评审阶段：有数据 ✅
   - 状态：有数据 ✅
```

### 步骤4: 点击"开始评审"
```
点击任意一个待评审任务的"开始评审"按钮

应该:
✅ 跳转到评分页面
✅ 显示完整的项目信息
✅ 可以填写评分表单
```

---

## 🔍 调试命令

如果还有问题，在 Dashboard 页面按 F12，粘贴：

```javascript
// 检查任务数据
console.log('='.repeat(60))
console.log('Dashboard 任务数据诊断')
console.log('='.repeat(60))

// 手动调用API
fetch('http://localhost:6031/api/reviews/my-tasks', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
})
.then(r => r.json())
.then(d => {
  console.log('API返回:', d)
  if (d.success && d.data) {
    console.log('任务数量:', d.data.length)
    if (d.data.length > 0) {
      const first = d.data[0]
      console.log('\n第一个任务:')
      console.log('  id:', first.id)
      console.log('  projectName:', first.projectName, first.projectName ? '✅' : '❌')
      console.log('  institutionName:', first.institutionName, first.institutionName ? '✅' : '❌')
      console.log('  registrationId:', first.registrationId, first.registrationId ? '✅' : '❌')
      console.log('  stage:', first.stage)
      console.log('  status:', first.status)
    }
  }
})
```

---

## 🎯 两个页面对比

| 页面 | 路由 | API | 按钮 | 状态 |
|-----|------|-----|------|------|
| **Dashboard** | `/reviewer/dashboard` | `getMyReviewTasks()` | 开始评审 / 查看 | ✅ 已修复 |
| **Tasks列表** | `/reviewer/tasks` | `getMyReviewTasks()` | 查看详情 / 评分 / 查看评分 | ✅ 正常 |

两个页面现在都使用相同的API，并且都正确传递参数了！

---

**现在刷新浏览器重新测试，Dashboard 首页应该能正常显示数据了！** 🚀
