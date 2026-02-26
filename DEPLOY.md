# 部署说明

## 📦 已完成

- ✅ 代码已提交到Git
- ✅ 代码已推送到远端分支 `web-20260206`
- ✅ 项目已本地编译完成（dist目录）

## 🚀 部署到服务器

**服务器信息**：
- IP: `81.71.44.180`
- 用户: `root`
- 密码: `Yiguo9527_`
- 目标路径: `/data/frontend`

---

## 方式1：使用WinSCP（推荐，图形界面）

### 步骤：

1. **下载安装WinSCP**
   - 下载地址: https://winscp.net/eng/download.php
   - 选择安装版或便携版

2. **连接服务器**
   - 文件协议: SFTP
   - 主机名: `81.71.44.180`
   - 端口: `22`
   - 用户名: `root`
   - 密码: `Yiguo9527_`
   - 点击"登录"

3. **上传dist目录**
   - 在右侧（服务器端）导航到 `/data/`
   - 如果没有 `frontend` 目录，创建一个
   - 将本地的 `dist` 目录拖拽上传到 `/data/frontend/`
   - 或者将 `dist` 目录重命名后上传

4. **验证部署**
   - 确认文件已上传到 `/data/frontend/dist/`
   - 应该包含 `index.html`、`assets/` 等文件

---

## 方式2：使用命令行SCP

### 在Git Bash或PowerShell中执行：

```bash
# 1. 进入项目目录
cd D:\AiCode\cursor\d_hos_pinguan_cla_frontend_20260205

# 2. 打包dist目录
cd dist
tar -czf ../dist.tar.gz .
cd ..

# 3. 上传到服务器
scp dist.tar.gz root@81.71.44.180:/tmp/

# 4. 连接到服务器
ssh root@81.71.44.180

# 5. 在服务器上执行（连接后）
mkdir -p /data/frontend

# 备份旧版本（如果存在）
if [ -d "/data/frontend/dist" ]; then
    mv /data/frontend/dist /data/frontend/dist.backup.$(date +%Y%m%d_%H%M%S)
fi

# 解压新版本
mkdir -p /data/frontend/dist
tar -xzf /tmp/dist.tar.gz -C /data/frontend/dist

# 清理
rm -f /tmp/dist.tar.gz

# 验证
ls -la /data/frontend/dist/

# 退出SSH
exit
```

**密码**: 执行scp和ssh命令时，输入密码 `Yiguo9527_`

---

## 方式3：使用PowerShell脚本（自动化）

### 前提条件：
需要安装PuTTY工具（包含pscp和plink命令）

### 执行：
```powershell
# 在PowerShell中执行
.\deploy.ps1
```

如果没有PuTTY，请使用方式1或方式2

---

## 🔍 验证部署

### 1. 检查文件结构

连接到服务器：
```bash
ssh root@81.71.44.180
```

查看文件：
```bash
ls -la /data/frontend/dist/
```

应该看到：
```
/data/frontend/dist/
├── index.html
├── assets/
│   ├── index-DlsYKFKp.js
│   ├── index-BhiroXkb.css
│   └── ...
└── ...
```

### 2. 配置Nginx（如果需要）

如果服务器使用Nginx，配置示例：

```nginx
server {
    listen 80;
    server_name 81.71.44.180;

    root /data/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

重启Nginx：
```bash
nginx -t
nginx -s reload
```

### 3. 访问验证

浏览器打开：`http://81.71.44.180`

应该能看到系统登录页面

---

## 📁 本地文件位置

- **源代码**: `D:\AiCode\cursor\d_hos_pinguan_cla_frontend_20260205`
- **编译产物**: `D:\AiCode\cursor\d_hos_pinguan_cla_frontend_20260205\dist`
- **Git分支**: `web-20260206`

---

## 🔄 后续更新部署

当需要再次部署时：

```bash
# 1. 拉取最新代码
git pull origin web-20260206

# 2. 重新编译
npm run build

# 3. 重复上述部署步骤
```

---

## ⚠️ 注意事项

1. **备份**：每次部署会自动备份旧版本到 `dist.backup.时间戳`
2. **权限**：确保 `/data/frontend` 目录有正确的权限
3. **防火墙**：确保服务器80端口（或其他HTTP端口）已开放
4. **域名**：如果使用域名访问，需要配置域名解析和Nginx

---

**部署完成后请确认访问是否正常！**
