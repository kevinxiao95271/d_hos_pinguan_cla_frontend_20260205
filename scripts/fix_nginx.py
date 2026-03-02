import paramiko

NEW_CONF = """server {
    listen 6039;
    server_name _;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/javascript application/json;

    location /pgds {
        alias /data/pgds;
        index index.html;
        try_files $uri $uri/ /pgds/index.html;
    }

    location /api/ {
        proxy_pass http://localhost:6031/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('81.71.44.180', username='root', password='Yiguo9527_', timeout=15)

def run(cmd):
    _, out, err = client.exec_command(cmd)
    o = out.read().decode().strip()
    e = err.read().decode().strip()
    print(f'  $ {cmd}')
    if o:
        print(f'    {o}')
    if e:
        print(f'  [stderr] {e}')
    return o

# 覆盖 pinguan.conf 为新的 /pgds 子路径版本
sftp = client.open_sftp()
with sftp.open('/etc/nginx/conf.d/pinguan.conf', 'w') as f:
    f.write(NEW_CONF)
sftp.close()
print('[1] pinguan.conf 已更新')

# 删除冲突的 pgds.conf
run('rm -f /etc/nginx/conf.d/pgds.conf')
print('[2] pgds.conf 已删除')

# 校验配置
out = run('nginx -t 2>&1')
if 'successful' in out:
    run('nginx -s reload')
    print('[3] Nginx reload 成功')
else:
    print('[3] Nginx 配置有误！')

# 本机 curl 验证
code = run('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:6039/pgds/')
print(f'[4] HTTP 状态码: {code}')

client.close()
print('完成')
