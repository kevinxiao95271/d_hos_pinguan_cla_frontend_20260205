import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', 22, 'root', 'Yiguo9527_', timeout=10)

for c in [
    'grep -r "6039" /etc/nginx/ 2>/dev/null',
    'curl -sv http://localhost:6039/pgds/login 2>&1 | tail -20',
    'ls /data/pgds/',
]:
    _, out, err = ssh.exec_command(c)
    o = out.read().decode('utf-8', errors='replace').strip()
    e = err.read().decode('utf-8', errors='replace').strip()
    print(f'\n>> {c}')
    if o: print(o)
    if e: print('ERR:', e)

ssh.close()
