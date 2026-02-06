# 快速检查清单 - "暂无报名数据"排查

## 🚀 5 分钟快速诊断

### ✅ Step 1: 检查后端服务

```bash
# 打开浏览器访问
http://localhost:6031/actuator/health

# 应该看到: {"status":"UP"}
```

**如果访问不了** → 后端未启动或端口错误

---

### ✅ Step 2: 检查登录状态

**浏览器控制台（F12）** → Console 标签

```javascript
// 检查 token
localStorage.getItem('token')

// 应该返回类似: "eyJhbGciOiJIUzI1NiJ9..."
```

**如果返回 null** → 重新登录

---

### ✅ Step 3: 检查赛事 ID

```javascript
// 检查赛事 ID
localStorage.getItem('currentCompetitionId')

// 应该返回: "21" 或其他数字
```

**如果返回 null** → 设置正确的 ID

```javascript
localStorage.setItem('currentCompetitionId', '21')
location.reload()
```

---

### ✅ Step 4: 检查 API 请求

**浏览器控制台（F12）** → Network 标签

1. 刷新页面
2. 找到 `registrations` 请求
3. 检查：
   - ✅ Status: 200（正常）
   - ❌ Status: 401（Token 过期，重新登录）
   - ❌ Status: 404（API 不存在，检查 URL）
   - ❌ 超时（后端响应慢，等待或重启后端）

---

### ✅ Step 5: 查看 Console 日志

应该看到类似的日志：

```
📥 正在加载报名列表...
📥 报名列表响应: {success: true, data: Array(33)}
✅ 报名列表加载成功: 33 条
```

**如果看到**:
- ❌ `401 未授权` → 重新登录
- ❌ `请求超时` → 检查后端
- ❌ `暂无报名数据` → 检查 Competition ID 或后端数据

---

## 🎯 一键修复

### 修复 1: 重置前端状态

```javascript
// 在浏览器控制台执行
localStorage.clear()
location.reload()
// 然后重新登录
```

---

### 修复 2: 设置正确的赛事 ID

```javascript
localStorage.setItem('currentCompetitionId', '21')
location.reload()
```

---

### 修复 3: 重启前端服务

```bash
# 在前端终端按 Ctrl+C 停止
# 然后重新运行
npm run dev
```

---

## 🧪 快速测试命令

### 测试后端是否正常

```bash
python test_login_simple.py
```

**预期输出**:
```
[SUCCESS] Login successful!
[OK] Backend is working normally!
```

---

## 📋 当前前端配置

### ✅ 使用的 API 端点

```
GET /api/registrations?competitionId=21
```

**不是**:
```
❌ GET /api/admin/registrations/filter  (会返回 401)
```

### ✅ 文件位置

- `src/views/committee/BookStage.vue` - 书审阶段报名列表
- `src/views/committee/Statistics.vue` - 报名统计
- `src/api/registration.js` - API 函数

### ✅ 关键函数

```javascript
// 获取报名列表
import { getRegistrations } from '@/api/registration'

const res = await getRegistrations({
  competitionId: 21,
  methodCode: 'xxx',  // 可选
  // ... 其他筛选条件
})
```

---

## 🆘 仍然无法解决？

### 1. 查看完整指南

```
FRONTEND_COMPLETE_FLOW_GUIDE.md
```

### 2. 运行完整测试

```bash
python test_complete_flow.py
```

### 3. 检查这些文档

- `API_FIX_SUMMARY.md` - API 问题修复总结
- `LOGIN_TIMEOUT_FIX.md` - 登录超时修复
- `LOGIN_EXPIRY_TROUBLESHOOTING.md` - 登录过期排查

---

## 📞 问题报告模板

如果问题仍然存在，提供以下信息：

```
1. 后端健康检查结果:
   http://localhost:6031/actuator/health
   返回: _______________

2. Token 状态:
   localStorage.getItem('token')
   返回: _______________

3. 赛事 ID:
   localStorage.getItem('currentCompetitionId')
   返回: _______________

4. API 请求状态码:
   Network 标签中 /registrations 请求
   Status: _______________

5. Console 日志:
   (复制粘贴控制台中的错误信息)

6. 测试脚本结果:
   python test_login_simple.py
   输出: _______________
```

---

## ✨ 常见问题速查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 暂无报名数据 | Competition ID 错误 | 设置为 21 |
| 登录已过期 | Token 过期 | 重新登录 |
| 请求超时 | 后端响应慢 | 等待或重启后端 |
| 401 错误 | Token 无效/过期 | 重新登录 |
| 404 错误 | API 路径错误 | 检查是否使用 `/api/registrations` |
| 看不到辅导员 | 后端数据未填充 | 确认后端有测试数据 |
| 筛选不工作 | 字典未加载 | 检查 `/api/dictionaries/*` |

---

**最后更新**: 2026-02-06
**当前版本**: 已修复 API 端点，使用 `/api/registrations`
