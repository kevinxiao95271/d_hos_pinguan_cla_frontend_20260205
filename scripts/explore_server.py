# -*- coding: utf-8 -*-
import sys
import codecs

# 设置输出编码
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    import paramiko
except ImportError:
    print("❌ 缺少paramiko库，正在安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko

def explore_server():
    """探测服务器/data目录结构"""
    
    host = "81.71.44.180"
    port = 22
    username = "root"
    password = "Yiguo9527_"
    
    print("🔍 正在连接服务器...")
    print(f"服务器: {host}")
    print(f"用户: {username}")
    print("")
    
    try:
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 连接
        print("⏳ 正在连接...")
        ssh.connect(host, port, username, password, timeout=10)
        print("✅ 连接成功！")
        print("")
        
        # 执行命令列表
        commands = [
            ("检查/data目录", "ls -lah /data"),
            ("检查/data目录下的子目录", "ls -lah /data/ 2>/dev/null || echo '/data目录不存在'"),
            ("检查磁盘空间", "df -h /data"),
            ("检查是否有frontend目录", "ls -lah /data/frontend 2>/dev/null || echo 'frontend目录不存在'"),
            ("检查是否有nginx", "which nginx || echo 'nginx未安装'"),
            ("检查nginx状态", "systemctl status nginx 2>/dev/null | head -5 || echo '无法获取nginx状态'"),
            ("检查nginx配置目录", "ls -la /etc/nginx/conf.d/ 2>/dev/null | head -10 || echo 'nginx配置目录不存在'"),
        ]
        
        for title, cmd in commands:
            print(f"{'='*80}")
            print(f"📋 {title}")
            print(f"命令: {cmd}")
            print(f"{'='*80}")
            
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if output:
                print(output)
            if error:
                print(f"⚠️ 错误: {error}")
            print("")
        
        # 关闭连接
        ssh.close()
        print("✅ 探测完成")
        return True
        
    except paramiko.AuthenticationException:
        print("❌ 认证失败：用户名或密码错误")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    explore_server()
