@echo off
chcp 65001 >nul
echo ============================================================
echo 停止后端服务
echo ============================================================

echo.
echo [1] 查找占用 6031 端口的进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :6031') do (
    echo     找到进程 PID: %%a
    echo     正在结束进程...
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo     [ERROR] 无法结束进程 %%a
    ) else (
        echo     [OK] 进程已结束
    )
)

echo.
echo [2] 验证端口是否已释放...
timeout /t 2 /nobreak >nul
netstat -ano | findstr :6031 >nul 2>&1
if errorlevel 1 (
    echo     [OK] 端口 6031 已释放
) else (
    echo     [WARNING] 端口 6031 仍被占用，可能需要手动检查
)

echo.
echo ============================================================
echo 后端服务已停止
echo ============================================================
echo.

pause
