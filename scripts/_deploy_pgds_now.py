# -*- coding: utf-8 -*-
import paramiko, os, sys
from datetime import datetime

host = '81.71.44.180'
username = 'root'
password = 'Yiguo9527_'
local_zip = 'dist.zip'
remote_tmp = '/tmp/dist.zip'
remote_target = '/data/pgds'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, 22, username, password, timeout=10)
print('SSH 连接成功')

sftp = ssh.open_sftp()
print('上传 dist.zip ...')

def progress(transferred, total):
    pct = transferred * 100 // total
    sys.stdout.write(f'\r{pct}%  ')
    sys.stdout.flush()

sftp.put(local_zip, remote_tmp, callback=progress)
sftp.close()
print('\n上传完成')

ts = datetime.now().strftime('%Y%m%d_%H%M%S')
cmd = f"""
set -e
if [ -d "{remote_target}" ]; then
    cp -r {remote_target} {remote_target}_bak_{ts}
    echo "备份完成: {remote_target}_bak_{ts}"
fi
rm -rf {remote_target}/*
unzip -o {remote_tmp} -d {remote_target}/
chown -R nginx:nginx {remote_target} 2>/dev/null || true
chmod -R 755 {remote_target}
rm -f {remote_tmp}
echo "解压完成"
ls {remote_target}/index.html && echo "index.html 存在"
ls {remote_target}/assets | wc -l
"""
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print('STDERR:', err)

stdin2, stdout2, stderr2 = ssh.exec_command('nginx -s reload && echo nginx_reload_ok')
print(stdout2.read().decode('utf-8'))
ssh.close()
print('=' * 50)
print('部署完成 => http://81.71.44.180:6039/pgds/login')
