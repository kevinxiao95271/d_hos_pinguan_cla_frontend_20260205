import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', 22, 'root', 'Yiguo9527_', timeout=10)

for c in [
    'journalctl -u nginx -n 20 --no-pager 2>&1',
    'ss -tlnp | grep -E "6039|80 "',
    'fuser 6039/tcp 2>&1',
]:
    _, out, err = ssh.exec_command(c)
    o = out.read().decode('utf-8', errors='replace').strip()
    e = err.read().decode('utf-8', errors='replace').strip()
    print(f'\n>> {c}')
    if o: print(o)
    if e: print('ERR:', e)

ssh.close()
