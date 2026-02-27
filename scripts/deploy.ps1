# PowerShell 部署脚本
# 服务器: 81.71.44.180
# 用户: root
# 密码: Yiguo9527_
# 目标路径: /data/frontend

$SERVER = "81.71.44.180"
$USER = "root"
$PASSWORD = "Yiguo9527_"
$TARGET_PATH = "/data/frontend"

Write-Host "📦 开始部署到服务器..." -ForegroundColor Green
Write-Host "服务器: $SERVER"
Write-Host "目标路径: $TARGET_PATH"
Write-Host ""

# 检查是否安装了pscp (PuTTY工具)
$pscpPath = "pscp"
try {
    & $pscpPath 2>&1 | Out-Null
} catch {
    Write-Host "❌ 未找到pscp命令" -ForegroundColor Red
    Write-Host "请使用以下手动部署方式:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "方式1: 使用WinSCP" -ForegroundColor Cyan
    Write-Host "  1. 下载WinSCP: https://winscp.net/"
    Write-Host "  2. 连接到服务器: 81.71.44.180"
    Write-Host "  3. 用户名: root"
    Write-Host "  4. 密码: Yiguo9527_"
    Write-Host "  5. 上传整个 dist 目录到 /data/frontend/"
    Write-Host ""
    Write-Host "方式2: 使用scp命令 (需要Git Bash)" -ForegroundColor Cyan
    Write-Host "  cd dist"
    Write-Host "  tar -czf ../dist.tar.gz ."
    Write-Host "  cd .."
    Write-Host "  scp dist.tar.gz root@81.71.44.180:/tmp/"
    Write-Host "  ssh root@81.71.44.180"
    Write-Host "  tar -xzf /tmp/dist.tar.gz -C /data/frontend/dist"
    exit 1
}

# 1. 打包dist目录
Write-Host "📦 打包dist目录..." -ForegroundColor Cyan
Push-Location dist
tar -czf ..\dist.tar.gz .
Pop-Location
Write-Host "✅ 打包完成: dist.tar.gz" -ForegroundColor Green
Write-Host ""

# 2. 上传到服务器 (需要输入密码)
Write-Host "📤 上传到服务器..." -ForegroundColor Cyan
Write-Host "请输入密码: $PASSWORD"
& pscp -pw $PASSWORD dist.tar.gz "${USER}@${SERVER}:/tmp/"
Write-Host "✅ 上传完成" -ForegroundColor Green
Write-Host ""

# 3. 在服务器上解压
Write-Host "📂 在服务器上部署..." -ForegroundColor Cyan
$commands = @"
mkdir -p /data/frontend
if [ -d '/data/frontend/dist' ]; then
    mv /data/frontend/dist /data/frontend/dist.backup.`$(date +%Y%m%d_%H%M%S)
fi
mkdir -p /data/frontend/dist
tar -xzf /tmp/dist.tar.gz -C /data/frontend/dist
rm -f /tmp/dist.tar.gz
echo '✅ 部署完成！'
"@

& plink -pw $PASSWORD "${USER}@${SERVER}" $commands
Write-Host "✅ 服务器部署完成" -ForegroundColor Green
Write-Host ""

# 4. 清理本地临时文件
Write-Host "🧹 清理本地临时文件..." -ForegroundColor Cyan
Remove-Item dist.tar.gz -Force
Write-Host "✅ 清理完成" -ForegroundColor Green
Write-Host ""

Write-Host "🎉 部署完成！" -ForegroundColor Green
Write-Host "服务器路径: /data/frontend/dist"
