#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新服务器上的前端文件
只上传新文件，不修改nginx配置
"""

import paramiko
import sys
import os
from pathlib import Path

# 设置Windows终端编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def upload_directory(sftp, local_dir, remote_dir):
    """递归上传目录"""
    try:
        sftp.stat(remote_dir)
    except IOError:
        sftp.mkdir(remote_dir)
    
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"
        
        if os.path.isfile(local_path):
            print(f"   上传: {item}")
            sftp.put(local_path, remote_path)
        elif os.path.isdir(local_path):
            print(f"   目录: {item}/")
            upload_directory(sftp, local_path, remote_path)


def main():
    HOST = "81.71.44.180"
    USERNAME = "root"
    PASSWORD = "Yiguo9527_"
    PORT = 22
    
    LOCAL_DIST = "dist"
    REMOTE_DIR = "/data/pinguan_frontend"
    
    print("=" * 60)
    print("更新服务器前端文件")
    print("=" * 60)
    print(f"服务器: {HOST}")
    print(f"本地目录: {LOCAL_DIST}")
    print(f"远程目录: {REMOTE_DIR}")
    print("=" * 60)
    print()
    
    # 检查本地dist目录
    if not os.path.exists(LOCAL_DIST):
        print(f"❌ 本地目录不存在: {LOCAL_DIST}")
        print("   请先运行 npm run build")
        sys.exit(1)
    
    try:
        # 连接服务器
        print("🔌 正在连接服务器...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=HOST,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
            timeout=10
        )
        sftp = ssh.open_sftp()
        print("✅ 连接成功\n")
        
        # 清理旧文件
        print("🗑️  清理旧文件...")
        stdin, stdout, stderr = ssh.exec_command(f"rm -rf {REMOTE_DIR}/*")
        stdout.channel.recv_exit_status()
        print("✅ 清理完成\n")
        
        # 上传新文件
        print("📤 上传新文件...")
        upload_directory(sftp, LOCAL_DIST, REMOTE_DIR)
        print("\n✅ 上传完成\n")
        
        # 验证文件
        print("🔍 验证文件...")
        stdin, stdout, stderr = ssh.exec_command(f"ls -lh {REMOTE_DIR}")
        output = stdout.read().decode('utf-8')
        print(output)
        
        # 关闭连接
        sftp.close()
        ssh.close()
        
        print("=" * 60)
        print("🎉 更新完成！")
        print("=" * 60)
        print(f"\n✅ 访问地址: http://{HOST}:6039")
        print("\n💡 建议清除浏览器缓存后访问，快捷键:")
        print("   - Chrome/Edge: Ctrl + Shift + R")
        print("   - Firefox: Ctrl + F5")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
