# -*- coding: utf-8 -*-
import sys
import codecs
import paramiko
import os
from datetime import datetime

# 设置输出编码
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def deploy():
    """部署前端到服务器"""
    
    host = "81.71.44.180"
    port = 22
    username = "root"
    password = "Yiguo9527_"
    
    # 本地文件
    local_zip = "dist.zip"
    # 服务器目标路径
    remote_tmp = "/tmp/dist.zip"
    remote_target = "/data/pinguan_frontend"
    
    print("🚀 开始部署前端到服务器")
    print(f"服务器: {host}")
    print(f"目标目录: {remote_target}")
    print("")
    
    try:
        # 检查本地文件
        if not os.path.exists(local_zip):
            print(f"❌ 本地文件不存在: {local_zip}")
            return False
        
        file_size = os.path.getsize(local_zip) / (1024 * 1024)
        print(f"📦 本地文件: {local_zip} ({file_size:.2f} MB)")
        print("")
        
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print("⏳ 正在连接服务器...")
        ssh.connect(host, port, username, password, timeout=10)
        print("✅ SSH连接成功！")
        print("")
        
        # 创建SFTP客户端
        sftp = ssh.open_sftp()
        
        # 上传文件
        print("📤 正在上传文件到服务器...")
        print(f"本地: {local_zip}")
        print(f"服务器: {remote_tmp}")
        
        def progress_callback(transferred, total):
            percent = (transferred / total) * 100
            bar_length = 40
            filled = int(bar_length * transferred / total)
            bar = '=' * filled + '-' * (bar_length - filled)
            sys.stdout.write(f'\r上传进度: [{bar}] {percent:.1f}% ({transferred}/{total} bytes)')
            sys.stdout.flush()
        
        sftp.put(local_zip, remote_tmp, callback=progress_callback)
        print("\n✅ 上传完成！")
        print("")
        
        sftp.close()
        
        # 在服务器上执行部署命令
        print("📂 在服务器上部署...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        deploy_commands = f"""
# 创建备份
if [ -d "{remote_target}" ]; then
    echo "📦 备份当前版本..."
    backup_dir="{remote_target}_backup_{timestamp}"
    cp -r {remote_target} $backup_dir
    echo "✅ 备份完成: $backup_dir"
fi

# 清空目标目录（保留目录本身）
echo "🧹 清理目标目录..."
rm -rf {remote_target}/*

# 安装unzip（如果没有）
if ! command -v unzip &> /dev/null; then
    echo "📥 安装unzip..."
    yum install -y unzip || apt-get install -y unzip
fi

# 解压文件到目标目录
echo "📦 解压文件..."
unzip -o {remote_tmp} -d {remote_target}/

# 设置权限
echo "🔐 设置文件权限..."
chown -R nginx:nginx {remote_target} 2>/dev/null || chown -R root:root {remote_target}
chmod -R 755 {remote_target}

# 清理临时文件
rm -f {remote_tmp}

# 验证部署
echo ""
echo "✅ 部署完成！"
echo "📁 文件列表:"
ls -lh {remote_target}/

echo ""
echo "📄 index.html内容检查:"
if [ -f "{remote_target}/index.html" ]; then
    echo "✅ index.html 存在"
    wc -l {remote_target}/index.html
else
    echo "❌ index.html 不存在"
fi

echo ""
echo "📁 assets目录检查:"
if [ -d "{remote_target}/assets" ]; then
    echo "✅ assets 目录存在"
    ls {remote_target}/assets | wc -l
    echo "个文件"
else
    echo "❌ assets 目录不存在"
fi
"""
        
        stdin, stdout, stderr = ssh.exec_command(deploy_commands)
        
        # 实时输出
        for line in stdout:
            print(line.strip())
        
        error_output = stderr.read().decode('utf-8')
        if error_output:
            print(f"\n⚠️ 错误输出:\n{error_output}")
        
        print("")
        
        # 杀进程重启nginx
        print("🔄 杀进程重启nginx...")
        stdin, stdout, stderr = ssh.exec_command("nginx -s stop; sleep 2; nginx")
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if output:
            print(output)
        if error:
            print(f"⚠️ nginx: {error}")
        
        # 验证nginx是否启动
        stdin2, stdout2, stderr2 = ssh.exec_command("pgrep nginx | head -1 && echo 'nginx running'")
        result = stdout2.read().decode('utf-8').strip()
        if 'nginx running' in result or result:
            print(f"✅ nginx 已重启，PID: {result.split()[0] if result else '?'}")
        
        ssh.close()
        
        print("")
        print("="*80)
        print("🎉 部署完成！")
        print("="*80)
        print(f"访问地址: http://{host}:6039")
        print(f"部署路径: {remote_target}")
        print("")
        
        return True
        
    except Exception as e:
        print(f"❌ 部署失败: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = deploy()
    sys.exit(0 if success else 1)
