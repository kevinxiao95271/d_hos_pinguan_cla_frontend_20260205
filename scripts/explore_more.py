# -*- coding: utf-8 -*-
import sys
import codecs
import paramiko

# 设置输出编码
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def explore_more():
    """进一步探测服务器配置"""
    
    host = "81.71.44.180"
    port = 22
    username = "root"
    password = "Yiguo9527_"
    
    print("🔍 进一步探测服务器配置...")
    print("")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password, timeout=10)
        print("✅ 连接成功！")
        print("")
        
        commands = [
            ("查看pinguan_frontend目录结构", "ls -lah /data/pinguan_frontend"),
            ("查看pinguan_frontend/dist目录", "ls -lah /data/pinguan_frontend/dist 2>/dev/null || echo 'dist目录不存在'"),
            ("查看pinguan.conf内容", "cat /etc/nginx/conf.d/pinguan.conf"),
            ("查看当前运行的前端在哪", "ps aux | grep nginx | head -3"),
        ]
        
        for title, cmd in commands:
            print(f"{'='*80}")
            print(f"📋 {title}")
            print(f"{'='*80}")
            
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if output:
                print(output)
            if error and 'echo' not in cmd:
                print(f"⚠️ 错误: {error}")
            print("")
        
        ssh.close()
        print("✅ 探测完成")
        return True
        
    except Exception as e:
        print(f"❌ 失败: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    explore_more()
