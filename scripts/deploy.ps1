# 浙江省品管大赛前端部署脚本 (Windows PowerShell)
# 服务器: 81.71.44.180
# 用户: root
# 密码: Yiguo9527_

$SERVER = "81.71.44.180"
$USER = "root"
$REMOTE_DIR = "/data/pinguan_frontend"
$PASSWORD = "Yiguo9527_"

Write-Host "=========================================="
Write-Host "开始部署前端到服务器"
Write-Host "=========================================="

# 1. 检查dist目录
if (-not (Test-Path "dist")) {
    Write-Host "❌ dist目录不存在，请先运行: npm run build" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 找到dist目录" -ForegroundColor Green

# 2. 使用scp上传文件
Write-Host "📤 上传构建文件到服务器..." -ForegroundColor Cyan
Write-Host "提示: 请输入服务器密码: Yiguo9527_"

# 方法1: 使用scp命令（需要手动输入密码）
scp -r dist/* ${USER}@${SERVER}:${REMOTE_DIR}/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 文件上传成功" -ForegroundColor Green
    Write-Host ""
    Write-Host "=========================================="
    Write-Host "🎉 部署完成！" -ForegroundColor Green
    Write-Host "访问地址: http://81.71.44.180:6039"
    Write-Host "=========================================="
} else {
    Write-Host "❌ 文件上传失败，请检查网络连接和服务器信息" -ForegroundColor Red
    exit 1
}
