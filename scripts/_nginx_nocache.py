# -*- coding: utf-8 -*-
import paramiko

NEW_CONF = r"""server {
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

    # index.html 不缓存：每次访问都向服务器验证，有更新自动拿新版
    location = /pgds/index.html {
        alias /data/pgds/index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # hashed assets 永久缓存：文件名带 hash，内容变了名字就变，安全
    location ^~ /pgds/assets/ {
        alias /data/pgds/assets/;
        add_header Cache-Control "max-age=31536000, immutable";
        expires 1y;
    }

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

    location / {
        root /data/pinguan_frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', 22, 'root', 'Yiguo9527_', timeout=10)

# 备份原配置
ssh.exec_command('cp /etc/nginx/conf.d/pinguan.conf /etc/nginx/conf.d/pinguan.conf.bak')

# 写入新配置
sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/conf.d/pinguan.conf', 'w') as f:
    f.write(NEW_CONF)
sftp.close()

# 测试配置语法
stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1')
result = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
print('nginx 语法检查:', result.strip())

if 'successful' in result:
    # reload nginx
    stdin2, stdout2, stderr2 = ssh.exec_command('nginx -s reload && echo reload_ok')
    print(stdout2.read().decode('utf-8').strip())
    print('✅ 配置已更新，nginx 已 reload')
else:
    # 回滚
    ssh.exec_command('cp /etc/nginx/conf.d/pinguan.conf.bak /etc/nginx/conf.d/pinguan.conf')
    print('❌ 配置有误，已自动回滚')

ssh.close()
