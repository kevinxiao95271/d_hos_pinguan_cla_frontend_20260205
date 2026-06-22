# -*- coding: utf-8 -*-
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', 22, 'root', 'Yiguo9527_', timeout=10)

cmds = [
    ('6031端口监听', 'ss -tlnp | grep 6031 || echo 无进程监听6031'),
    ('Java进程', 'ps aux | grep java | grep -v grep || echo 无Java进程'),
    ('服务目录', 'ls /data/ | head -20'),
]
for label, cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f'\n=== {label} ===')
    print(stdout.read().decode('utf-8') or stderr.read().decode('utf-8') or '(空)')
ssh.close()
