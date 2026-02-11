@echo off
chcp 65001 >nul
echo ==========================================
echo 浙江省品管大赛前端部署
echo 服务器: 81.71.44.180
echo 密码: Yiguo9527_
echo 前端端口: 6039  后端端口: 6031
echo ==========================================
echo.

echo 第1步: 上传文件到服务器
echo 提示: 请输入密码 Yiguo9527_
echo.

cd /d "%~dp0"
scp -r dist/* root@81.71.44.180:/data/pinguan_frontend/

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 文件上传成功！
    echo.
    echo ==========================================
    echo 第2步: 配置nginx
    echo ==========================================
    echo.
    echo 现在需要登录服务器配置nginx，请手动执行以下命令：
    echo.
    echo 1. 登录服务器:
    echo    ssh root@81.71.44.180
    echo    密码: Yiguo9527_
    echo.
    echo 2. 复制以下内容到服务器执行:
    echo.
    type nginx_config.txt
    echo.
    echo 3. 重启nginx:
    echo    nginx -t ^&^& systemctl restart nginx
    echo.
    echo 4. 验证:
    echo    访问 http://81.71.44.180:6039
    echo.
) else (
    echo.
    echo ❌ 文件上传失败
    echo.
    echo 请检查:
    echo 1. 是否安装了OpenSSH客户端
    echo 2. 网络连接是否正常
    echo 3. 服务器地址和密码是否正确
)

echo.
pause
