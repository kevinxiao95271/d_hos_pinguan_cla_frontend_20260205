# 🔧 测试脚本目录

本目录包含所有用于测试、调试和工具的脚本文件。

## 📋 脚本分类

### 🔐 登录相关
- `test_login_simple.py` - 简单登录测试
- `diagnose_login.py` - 登录诊断工具
- `decode_token.py` - Token解码工具
- `test_all_token_formats.py` - 测试所有Token格式

### 📝 报名与筛选
- `test_registrations_api.py` - 测试报名列表API
- `test_registrations_detail.py` - 测试报名详情API
- `test_registrations_filters.py` - 测试报名筛选API
- `test_admin_filter.py` - 测试管理员筛选API
- `test_different_endpoints.py` - 测试不同端点
- `test_fields.py` - 测试字段返回

### 📚 字典与详情
- `test_dictionaries.py` - 测试字典API
- `test_detail_api.py` - 测试详情API
- `test_detail_endpoint.py` - 测试详情端点
- `quick_test_label.py` - 快速测试标签

### 🏥 书审阶段
- `test_api_bookstage.py` - 测试书审阶段API
- `test_list_api_now.py` - 测试当前列表API

### 🔄 完整流程
- `test_complete_flow.py` - 测试完整流程
- `test_api.py` - 基础API测试
- `test_api_enhanced.py` - 增强API测试

### 🔧 后端管理
- `check_backend.py` - 检查后端状态
- `verify_backend_now.py` - 验证后端当前状态
- `test_backend_optimized.py` - 测试后端优化
- `stop_backend.bat` - 停止后端服务（Windows批处理）

## 🚀 使用方法

### Python 脚本
```bash
# 基本用法
python scripts/test_login_simple.py

# 诊断登录问题
python scripts/diagnose_login.py

# 测试完整流程
python scripts/test_complete_flow.py
```

### 批处理脚本 (Windows)
```cmd
# 停止后端服务
scripts\stop_backend.bat
```

## 📝 脚本说明

### 测试脚本命名规范
- `test_*.py` - 测试相关的脚本
- `diagnose_*.py` - 诊断相关的脚本
- `check_*.py` - 检查相关的脚本
- `verify_*.py` - 验证相关的脚本
- `decode_*.py` - 解码相关的脚本
- `*.bat` - Windows批处理脚本

### 脚本依赖
大部分脚本依赖以下Python库：
```bash
pip install requests
```

## ⚠️ 注意事项

1. **后端地址**：大部分脚本默认连接 `http://localhost:6031`
2. **测试账号**：使用预设的测试账号（如 13800000041）
3. **编码问题**：Windows环境下注意UTF-8编码
4. **超时设置**：默认超时为30秒，可根据需要调整

## 🔍 常用脚本

### 快速诊断
```bash
# 1. 检查后端是否运行
python scripts/check_backend.py

# 2. 测试登录
python scripts/test_login_simple.py

# 3. 测试完整流程
python scripts/test_complete_flow.py
```

### 调试工具
```bash
# 查看Token内容
python scripts/decode_token.py

# 诊断登录问题
python scripts/diagnose_login.py
```

## 📝 脚本维护

- 新增测试场景时，应创建对应的测试脚本
- 脚本应包含清晰的注释和输出信息
- 定期更新脚本以适应API变化
- 过期或无用的脚本应及时清理
