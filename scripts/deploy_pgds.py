# -*- coding: utf-8 -*-
import paramiko
import os
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

host = "81.71.44.180"
port = 22
username = "root"
password = "Yiguo9527_"
local_zip = "dist.zip"
remote_tmp = "/tmp/dist.zip"
remote_target = "/data/pgds"

print("🚀 部署到 /data/pgds ...")

if not os.path.exists(local_zip):
    print(f"❌ 找不到 {local_zip}")
    sys.exit(1)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password, timeout=10)
print("✅ SSH 连接成功")

sftp = ssh.open_sftp()
file_size = os.path.getsize(local_zip)

def progress(transferred, total):
    pct = int(transferred / total * 100)
    sys.stdout.write(f"\r📤 上传中 {pct}% ({transferred}/{total})")
    sys.stdout.flush()

sftp.put(local_zip, remote_tmp, callback=progress)
sftp.close()
print("\n✅ 上传完成")

ts = datetime.now().strftime('%Y%m%d_%H%M%S')
deploy_cmd = f"""
set -e
if [ -d "{remote_target}" ] && [ "$(ls -A {remote_target})" ]; then
    echo "📦 备份旧版本..."
    cp -r {remote_target} {remote_target}_backup_{ts}
fi
mkdir -p {remote_target}
rm -rf {remote_target}/*
echo "📦 解压文件..."
unzip -o {remote_tmp} -d {remote_target}/
chown -R nginx:nginx {remote_target} 2>/dev/null || chown -R root:root {remote_target}
chmod -R 755 {remote_target}
rm -f {remote_tmp}
echo "✅ 部署完成"
echo "📁 文件列表:"
ls -lh {remote_target}/ | head -8
"""

_, stdout, stderr = ssh.exec_command(deploy_cmd)
print(stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("⚠️  STDERR:", err[:300])

print("🔄 重载 nginx...")
_, stdout, stderr = ssh.exec_command("nginx -t && nginx -s reload")
out = stdout.read().decode()
err = stderr.read().decode()
if out: print(out)
if 'successful' in err or 'test is successful' in err:
    print("✅ nginx 配置正常")
elif err:
    print("nginx:", err[:200])

ssh.close()
print("\n🎉 完成！访问地址: http://81.71.44.180:6039/pgds/login")
