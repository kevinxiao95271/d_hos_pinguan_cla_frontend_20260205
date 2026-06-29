import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', 22, 'root', 'Yiguo9527_', timeout=10)

new_conf = """server {
    listen 6039;
    server_name _;

    access_log /var/log/nginx/mirror_access.log combined;
    error_log /var/log/nginx/mirror_error.log;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/javascript application/json;

    location /pgds {
        alias /data/pgds/dist;
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

    location / {
        root /data/pinguan_frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
"""

stdin, stdout, stderr = ssh.exec_command('cat > /etc/nginx/conf.d/pinguan.conf')
stdin.write(new_conf)
stdin.channel.shutdown_write()
stdout.read()

_, out, err = ssh.exec_command('nginx -t 2>&1 && nginx -s reload && echo reload_ok')
print(out.read().decode('utf-8', errors='replace'))
print(err.read().decode('utf-8', errors='replace'))

_, out2, _ = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:6039/pgds/login')
print('HTTP status:', out2.read().decode())

ssh.close()
