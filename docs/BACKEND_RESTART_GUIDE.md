# 后端服务重启指南

## 问题症状

- 前端登录请求超时 (`timeout of 30000ms exceeded`)
- 后端健康检查超时
- 后端响应非常慢或不响应

## 原因分析

可能的原因：
1. 后端服务卡住或死锁
2. 数据库连接池耗尽
3. 内存不足导致频繁 GC
4. 某个长时间运行的查询阻塞了线程池

## 解决步骤

### 步骤 1: 找到后端进程并停止

#### Windows 方式

```powershell
# 查找占用 6031 端口的进程
netstat -ano | findstr :6031

# 假设找到 PID 为 12345，强制结束进程
taskkill /F /PID 12345
```

#### 或者使用任务管理器
1. 打开任务管理器 (Ctrl+Shift+Esc)
2. 找到 `java.exe` 或 `javaw.exe` 进程
3. 查看命令行参数，确认是后端服务
4. 右键 → 结束任务

### 步骤 2: 重新启动后端服务

```bash
# 进入后端目录
cd D:\AiCode\traegj\d_hos_pinguan_traegj_backend_20260205

# 启动后端服务
mvn spring-boot:run
```

或者使用 IDE：
- 如果使用 IntelliJ IDEA，停止运行配置，然后重新运行
- 如果使用 Eclipse，停止服务器，清理项目，重新运行

### 步骤 3: 等待启动完成

后端启动需要 10-30 秒，请等待看到类似日志：
```
Started Application in X seconds
Tomcat started on port(s): 6031 (http)
```

### 步骤 4: 验证后端状态

#### 方式 1: 使用 Python 脚本
```bash
python check_backend.py
```

#### 方式 2: 浏览器访问
打开浏览器访问: http://localhost:6031/actuator/health

应该看到: `{"status":"UP"}`

#### 方式 3: Swagger UI
打开浏览器访问: http://localhost:6031/swagger-ui/index.html

### 步骤 5: 重试前端登录

1. 刷新前端页面 (Ctrl+F5 或 Cmd+Shift+R)
2. 重新登录

## 快速命令脚本

创建一个 `restart_backend.bat` 文件：

```batch
@echo off
echo 正在停止后端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :6031') do (
    echo 找到进程 PID: %%a
    taskkill /F /PID %%a
)

echo 等待 3 秒...
timeout /t 3 /nobreak

echo 启动后端服务...
cd /d D:\AiCode\traegj\d_hos_pinguan_traegj_backend_20260205
start mvn spring-boot:run

echo 后端服务正在启动，请等待 30 秒...
timeout /t 30 /nobreak

echo 检查后端状态...
python D:\AiCode\cursor\d_hos_pinguan_cla_frontend_20260205\check_backend.py

pause
```

## 预防措施

### 1. 增加数据库连接池配置

在 `application.yml` 或 `application.properties` 中：

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
```

### 2. 增加日志级别查看问题

```yaml
logging:
  level:
    root: INFO
    com.yourpackage: DEBUG
    org.springframework.web: DEBUG
```

### 3. 监控内存使用

启动时添加 JVM 参数：
```bash
mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Xmx2g -Xms1g"
```

## 常见问题

### Q1: 找不到 6031 端口的进程
**A:** 后端可能已经停止，直接启动即可

### Q2: 后端启动失败，提示端口被占用
**A:** 说明有残留进程，使用 `netstat` 和 `taskkill` 强制结束

### Q3: 后端启动后还是超时
**A:** 
1. 检查数据库是否正常运行
2. 检查防火墙是否阻止了连接
3. 查看后端日志文件，寻找错误信息

### Q4: 数据库连接失败
**A:**
1. 确认 MySQL 服务已启动
2. 检查数据库配置文件中的连接信息
3. 测试数据库连接: `mysql -u root -p`

## 联系后端开发

如果问题持续存在，请提供：
1. 后端日志最后 100 行
2. 数据库状态
3. 系统资源使用情况（内存、CPU）
4. 错误复现步骤
