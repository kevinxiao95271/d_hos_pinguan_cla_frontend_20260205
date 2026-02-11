@echo off
chcp 65001
echo ==========================================
echo 浙江省品管大赛前端部署
echo ==========================================
echo.

echo 步骤1: 上传文件到服务器
echo 提示: 请输入密码 Yiguo9527_
echo.

scp -r dist\* root@81.71.44.180:/data/pinguan_frontend/

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 文件上传成功！
    echo.
    echo 下一步: 登录服务器配置nginx
    echo 命令: ssh root@81.71.44.180
    echo 密码: Yiguo9527_
) else (
    echo.
    echo ❌ 文件上传失败
)

pause
