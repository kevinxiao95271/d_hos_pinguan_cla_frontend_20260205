# -*- coding: utf-8 -*-
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', 22, 'root', 'Yiguo9527_', timeout=10)

cmds = [
    ('文件结构', 'ls -la /data/pgds/'),
    ('HTTP状态', 'curl -s -o /dev/null -w "%{http_code}" http://localhost:6039/pgds/login'),
    ('nginx测试', 'nginx -t 2>&1'),
    ('nginx错误日志', 'tail -30 /var/log/nginx/mirror_error.log'),
    ('备份内容', 'ls /data/pgds_bak_20260515_095658/ 2>/dev/null | head -5'),
]
for label, cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    print(f'\n=== {label} ===')
    print(out or err or '(空)')
ssh.close()
