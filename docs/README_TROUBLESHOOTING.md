# 浙江省品管大赛前端系统 - 问题排查总索引

## 📚 文档导航

### 🚀 快速开始

**遇到"暂无报名数据"？** → 查看 [`QUICK_CHECKLIST.md`](./QUICK_CHECKLIST.md)
- 5 分钟快速诊断
- 一键修复命令
- 常见问题速查表

---

### 📖 详细指南

#### 1. 前端完整流程指引
**文件**: [`FRONTEND_COMPLETE_FLOW_GUIDE.md`](./FRONTEND_COMPLETE_FLOW_GUIDE.md)

**适用场景**:
- 理解整个数据流程（从登录到列表、详情、筛选）
- 排查"暂无报名数据"的根本原因
- 学习如何正确调用 API

**包含内容**:
- ✅ 完整的 5 步流程（登录 → 列表 → 排查 → 详情 → 筛选）
- ✅ 每个步骤的 API 文档和示例
- ✅ 前端代码检查清单
- ✅ 常见问题排查步骤

---

#### 2. API 修复总结
**文件**: [`API_FIX_SUMMARY.md`](./API_FIX_SUMMARY.md)

**适用场景**:
- 了解为什么修改了 API 调用
- 查看已修复的问题
- 理解当前使用的 API 端点

**核心信息**:
- ❌ `/api/admin/registrations/filter` 返回 401（不可用）
- ✅ `/api/registrations` 正常工作（当前使用）
- 已修改的文件清单
- API 测试结果汇总

---

#### 3. 登录问题排查

##### 3.1 登录超时
**文件**: [`LOGIN_TIMEOUT_FIX.md`](./LOGIN_TIMEOUT_FIX.md)

**适用场景**:
- 登录时提示"请求超时"
- 登录缓慢或需要很长时间

**已实施的优化**:
- ✅ 增加代理超时到 60 秒
- ✅ 实现自动重试机制（最多重试 2 次）
- ✅ 增强错误提示

##### 3.2 登录过期
**文件**: [`LOGIN_EXPIRY_TROUBLESHOOTING.md`](./LOGIN_EXPIRY_TROUBLESHOOTING.md)

**适用场景**:
- 使用过程中突然提示"登录已过期"
- 想了解 Token 管理机制

**包含工具**:
- Token 调试器（开发环境，页面右下角 ℹ️ 按钮）
- 详细的错误日志
- 排查步骤指南

---

#### 4. 后端服务管理
**文件**: [`BACKEND_RESTART_GUIDE.md`](./BACKEND_RESTART_GUIDE.md)

**适用场景**:
- 后端服务无响应或卡住
- 需要重启后端服务
- 端口被占用

**包含内容**:
- 停止后端进程的方法
- 启动后端服务的步骤
- 验证后端状态的方法
- 常见问题解决方案

---

### 🔧 测试工具

#### Python 测试脚本

| 脚本 | 用途 | 执行命令 |
|------|------|----------|
| `test_login_simple.py` | 快速登录测试 | `python test_login_simple.py` |
| `test_complete_flow.py` | 完整流程测试 | `python test_complete_flow.py` |
| `test_api_bookstage.py` | 书审阶段 API 测试 | `python test_api_bookstage.py` |
| `test_registrations_api.py` | 报名 API 全面测试 | `python test_registrations_api.py` |
| `diagnose_login.py` | 登录诊断工具 | `python diagnose_login.py 1` |
| `check_backend.py` | 后端状态检查 | `python check_backend.py` |

#### 批处理脚本

| 脚本 | 用途 | 执行方法 |
|------|------|----------|
| `stop_backend.bat` | 停止后端服务 | 双击运行或 `./stop_backend.bat` |

---

### 📊 系统架构

#### 前端架构
```
src/
├── api/
│   ├── registration.js    ✅ 报名相关 API（使用中）
│   ├── admin.js           ⚠️  部分接口返回 401
│   ├── dictionary.js      ✅ 字典 API
│   └── ...
├── views/
│   └── committee/
│       ├── Statistics.vue      📊 报名统计（已修复）
│       ├── BookStage.vue       📋 书审阶段（已修复）
│       ├── InterviewStage.vue  🎤 面谈阶段
│       └── FinalStage.vue      🏆 决赛阶段
└── utils/
    └── request.js         🔧 请求拦截器（已增强）
```

#### API 端点状态

| 端点 | 状态 | 用途 | 说明 |
|------|------|------|------|
| `POST /api/auth/login` | ✅ | 登录 | 正常 |
| `GET /api/registrations` | ✅ | 报名列表 | **当前使用** |
| `GET /api/registrations/{id}` | ✅ | 报名详情 | 正常 |
| `GET /api/dictionaries/*` | ✅ | 字典数据 | 正常 |
| `GET /api/competitions` | ✅ | 赛事列表 | 正常 |
| `GET /api/admin/registrations/filter` | ❌ | 报名筛选 | 401，已弃用 |

---

### 🎯 问题决策树

```
遇到问题？
│
├─ 暂无报名数据？
│  └─> 查看 QUICK_CHECKLIST.md（5分钟快速诊断）
│
├─ 登录超时？
│  └─> 查看 LOGIN_TIMEOUT_FIX.md
│
├─ 登录已过期？
│  └─> 查看 LOGIN_EXPIRY_TROUBLESHOOTING.md
│
├─ 后端无响应？
│  └─> 查看 BACKEND_RESTART_GUIDE.md
│
├─ 想了解完整流程？
│  └─> 查看 FRONTEND_COMPLETE_FLOW_GUIDE.md
│
└─ 想了解修复了什么？
   └─> 查看 API_FIX_SUMMARY.md
```

---

### ✅ 已修复的问题

#### 1. API 端点问题 (2026-02-06)
- ❌ 问题: `/api/admin/registrations/filter` 返回 401
- ✅ 解决: 切换到 `/api/registrations`
- 📁 影响文件: `BookStage.vue`, `Statistics.vue`

#### 2. 登录超时问题 (2026-02-06)
- ❌ 问题: 登录请求超时（30秒）
- ✅ 解决: 增加超时时间 + 自动重试
- 📁 影响文件: `vite.config.js`, `request.js`

#### 3. Token 管理问题 (2026-02-06)
- ❌ 问题: Token 过期处理不当，重复弹窗
- ✅ 解决: 防重复机制 + 详细日志
- 📁 影响文件: `request.js`

#### 4. 导航结构优化 (2026-02-06)
- ✅ 改进: 重组赛事管理导航
- ✅ 新增: 报名统计、书审阶段等页面
- 📁 新增文件: `Statistics.vue`, `BookStage.vue` 等

#### 5. 成员数据显示 (2026-02-06)
- ❌ 问题: 辅导员和参与人员未区分显示
- ✅ 解决: 根据 `role` 字段正确过滤
- 📁 影响文件: `MyCompetition.vue`

---

### 🔄 当前系统状态

#### 前端 ✅
- 开发服务器: http://localhost:6039
- 状态: 正常运行
- 最新修改: 2026-02-06

#### 后端 ⚠️
- 服务地址: http://localhost:6031
- 状态: 运行中（偶尔响应慢）
- 建议: 如遇超时，按 BACKEND_RESTART_GUIDE 重启

#### 数据库 ✅
- 测试数据: 33 条报名记录
- 赛事 ID: 21
- 机构: 30+ 家医院

---

### 📞 获取帮助

#### 步骤 1: 快速自查
1. 查看 [`QUICK_CHECKLIST.md`](./QUICK_CHECKLIST.md)
2. 运行 `python test_login_simple.py`
3. 检查浏览器控制台日志

#### 步骤 2: 深入排查
根据具体问题查看对应的详细指南（见上文）

#### 步骤 3: 报告问题
使用 [`QUICK_CHECKLIST.md`](./QUICK_CHECKLIST.md) 中的"问题报告模板"

---

### 📝 相关文档完整列表

**核心指南**:
- ✅ `QUICK_CHECKLIST.md` - 快速检查清单（5分钟）⭐⭐⭐
- ✅ `FRONTEND_COMPLETE_FLOW_GUIDE.md` - 前端完整流程指引 ⭐⭐⭐
- ✅ `API_FIX_SUMMARY.md` - API 修复总结 ⭐⭐

**专项指南**:
- ✅ `LOGIN_TIMEOUT_FIX.md` - 登录超时修复
- ✅ `LOGIN_EXPIRY_TROUBLESHOOTING.md` - 登录过期排查
- ✅ `BACKEND_RESTART_GUIDE.md` - 后端重启指南

**架构文档**:
- ✅ `NAVIGATION_STRUCTURE.md` - 导航结构说明
- ✅ `INTEGRATION_STATUS.md` - 集成状态文档

**测试工具**:
- ✅ `test_*.py` - 各种测试脚本（8个）
- ✅ `stop_backend.bat` - 停止后端服务

**组件文档**:
- ✅ `src/components/TokenDebugger.vue` - Token 调试器

---

### 🎓 最佳实践

#### 开发流程
1. 启动后端服务
2. 启动前端服务 (`npm run dev`)
3. 登录系统
4. 使用 Token 调试器监控状态
5. 查看控制台日志排查问题

#### 遇到问题时
1. 不要慌张 😊
2. 打开 `QUICK_CHECKLIST.md`
3. 按步骤检查
4. 运行测试脚本
5. 查看详细指南

#### 报告问题时
1. 截图错误信息
2. 提供控制台日志
3. 运行测试脚本并提供输出
4. 说明复现步骤

---

### 🌟 版本历史

**v1.2 (2026-02-06)**
- ✅ 修复 API 端点问题
- ✅ 实现登录自动重试
- ✅ 优化导航结构
- ✅ 完善文档体系

**v1.1 (2026-02-05)**
- ✅ 初始功能实现
- ✅ 基础 API 集成

---

**最后更新**: 2026-02-06
**维护者**: AI Assistant
**状态**: 生产就绪 ✅
