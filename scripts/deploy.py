import paramiko
import os
import sys

HOST = '81.71.44.180'
PORT = 22
USER = 'root'
PASS = 'Yiguo9527_'
LOCAL_ZIP = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist.zip')

NGINX_CONF = r"""
server {
    listen 6039;

    # 前端静态文件 /pgds
    location /pgds {
        alias /data/pgds;
        index index.html;
        try_files $uri $uri/ /pgds/index.html;
    }

    # API 反向代理到后端 6031
    location /api/ {
        proxy_pass http://127.0.0.1:6031/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
"""

def run(client, cmd):
    print(f'  $ {cmd}')
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f'    {out}')
    if err:
        print(f'  [stderr] {err}')
    return out, err

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f'[1/4] 连接 {HOST}...')
    client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    print('      连接成功')

    print('[2/4] 上传 dist.zip...')
    sftp = client.open_sftp()
    sftp.put(LOCAL_ZIP, '/data/dist.zip')
    sftp.close()
    print('      上传完成')

    print('[3/4] 解压并部署到 /data/pgds...')
    run(client, 'apt-get install -y unzip 2>/dev/null | tail -1')
    run(client, 'rm -rf /data/pgds_bak && [ -d /data/pgds ] && mv /data/pgds /data/pgds_bak || true')
    run(client, 'unzip -o /data/dist.zip -d /data/tmp_pgds')
    run(client, 'mv /data/tmp_pgds/dist /data/pgds')
    run(client, 'rm -rf /data/tmp_pgds /data/dist.zip')
    run(client, 'ls /data/pgds')

    print('[4/4] Reload Nginx...')
    run(client, 'rm -f /etc/nginx/conf.d/pgds.conf')
    out, err = run(client, 'nginx -t 2>&1')
    if 'successful' in out or 'successful' in err:
        run(client, 'nginx -s reload')
        code, _ = run(client, 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:6039/pgds/')
        print(f'      HTTP: {code}')
        print('      http://81.71.44.180:6039/pgds')
    else:
        print('Nginx config error!')
        sys.exit(1)

    client.close()

if __name__ == '__main__':
    main()
