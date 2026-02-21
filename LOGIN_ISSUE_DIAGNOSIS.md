# 登录问题诊断报告

## 问题描述
前端登录失败，登录API请求超时

## 诊断结果

### ✅ 检查通过的项目
1. ✓ 后端服务运行正常（端口 6031）
2. ✓ Swagger UI 可访问
3. ✓ 数据库连接正常 (119.167.165.27:5432)
4. ✓ 前端代理配置正确
5. ✓ 其他API接口响应正常

### ❌ 存在的问题
**登录 API (`POST /api/auth/login`) 请求超时**
- 测试30秒超时仍无响应
- 可能原因：
  1. 数据库查询阻塞或死锁
  2. 后端代码存在无限循环或其他阻塞
  3. 数据库表锁定

## 解决方案

### 方案1：重启后端服务（推荐）

1. 停止当前后端服务：
```powershell
# 找到Java进程并停止
taskkill /F /PID 6140
```

2. 进入后端目录：
```powershell
cd D:\AiCode\kiro\d_hos_pinguan_traegj_backend_20260205
```

3. 重新启动后端：
```powershell
# 使用Maven运行
mvn spring-boot:run

# 或者直接运行JAR
java -jar target\pinguan-backend-0.0.1-SNAPSHOT.jar
```

### 方案2：通过Swagger UI测试

1. 访问: http://localhost:6031/swagger-ui/index.html
2. 找到"认证"分组的 `POST /api/auth/login` 接口
3. 点击 "Try it out"
4. 填入测试数据：
```json
{
  "phone": "13800000127",
  "name": "CommitteeAdmin A",
  "role": "COMMITTEE_ADMIN"
}
```
5. 点击 "Execute" 测试登录

### 方案3：检查后端日志

如果重启后问题仍存在，检查后端控制台日志，查找以下信息：
- SQL查询是否有死锁
- 是否有异常堆栈
- 数据库连接池是否耗尽

## 测试账号

前端已配置的测试账号（Login.vue:100-117）：

### 组委会管理员
- 手机：13800000127 / 姓名：CommitteeAdmin A
- 手机：13799999971 / 姓名：CommitteeAdmin B

### 运维人员
- 手机：13800000005 / 姓名：OPS User 1
- 手机：13800000027 / 姓名：OPS User 2

### 评委
- 手机：13800002569 / 姓名：孙丽娟
- 手机：13900000001 / 姓名：王建国
- 手机：13800000084 / 姓名：李明华

### 参赛者
- 手机：13799999112 / 姓名：王建国
- 手机：13966000890 / 姓名：参赛者1

## 后续建议

1. **立即操作**：重启后端服务
2. **验证**：重启后使用测试脚本验证登录
3. **监控**：观察后端日志输出
4. **优化**：如果问题反复出现，考虑优化登录逻辑或数据库查询

## 测试脚本

已创建测试脚本：`test-backend-login.ps1`
重启后端后可运行此脚本验证：
```powershell
powershell -ExecutionPolicy Bypass -File test-backend-login.ps1
```
