import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', 22, 'root', 'Yiguo9527_', timeout=10)
print('SSH OK')

for c in [
    'systemctl start nginx',
    'systemctl status nginx --no-pager | head -5',
    'curl -s -o /dev/null -w "%{http_code}" http://localhost:6039/pgds/login',
]:
    _, out, err = ssh.exec_command(c)
    o = out.read().decode('utf-8', errors='replace').strip()
    e = err.read().decode('utf-8', errors='replace').strip()
    print(f'\n>> {c}')
    if o: print(o)
    if e: print('ERR:', e)

ssh.close()
