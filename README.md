# 浙江省品管大赛管理系统 - 前端

Vue 3 + Element Plus 实现的品管大赛管理系统前端。

## 📁 项目结构

```
d_hos_pinguan_cla_frontend_20260205/
├── src/                    # 源代码
│   ├── api/               # API 接口
│   ├── assets/            # 静态资源
│   ├── components/        # 公共组件
│   ├── composables/       # 组合式函数
│   ├── layouts/           # 布局组件
│   ├── router/            # 路由配置
│   ├── stores/            # Pinia 状态管理
│   ├── utils/             # 工具函数
│   └── views/             # 页面组件
├── public/                 # 公共静态资源
├── docs/                   # 📚 项目文档
│   ├── README.md          # 文档索引
│   ├── QUICK_START.md     # 快速开始
│   └── ...                # 其他文档
├── scripts/                # 🔧 测试脚本
│   ├── README.md          # 脚本说明
│   └── test_*.py          # 测试脚本
├── index.html             # HTML 入口
├── package.json           # 项目配置
├── vite.config.js         # Vite 配置
└── README.md              # 本文件
```

## 🚀 快速开始

### 1. 安装依赖
```bash
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```
访问：http://localhost:6039

### 3. 测试账号
- 组委会：13800000041 / CommitteeAdmin A
- 参赛者：13800000011 / Contestant A
- 评审专家：13800000021 / Reviewer A
- 运维：13800000051 / Ops A

## 📚 文档

详细文档请查看 [docs/](./docs/) 目录：
- [快速开始](./docs/QUICK_START.md)
- [部署清单](./docs/DEPLOYMENT_CHECKLIST.md)
- [功能文档](./docs/)
- [故障排查](./docs/README_TROUBLESHOOTING.md)

## 🔧 测试脚本

测试脚本位于 [scripts/](./scripts/) 目录：
```bash
# 测试登录
python scripts/test_login_simple.py

# 测试完整流程
python scripts/test_complete_flow.py

# 诊断问题
python scripts/diagnose_login.py
```

## 🛠️ 技术栈

- **框架**：Vue 3
- **UI库**：Element Plus
- **状态管理**：Pinia
- **路由**：Vue Router
- **HTTP**：Axios
- **图表**：ECharts
- **构建工具**：Vite

## 📝 开发规范

- 组件命名采用 PascalCase
- 文件命名采用 kebab-case
- API 调用统一使用 `src/api/` 中的方法
- 样式使用 SCSS，采用 BEM 命名规范

## 🌐 后端对接

后端服务地址：http://localhost:6031
- Swagger UI: http://localhost:6031/swagger-ui/index.html
- API Docs: http://localhost:6031/v3/api-docs

## 📦 构建部署

```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 📄 License

Private Project
