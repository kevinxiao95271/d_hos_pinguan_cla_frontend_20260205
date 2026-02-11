#!/bin/bash

echo "=========================================="
echo "浙江省品管大赛前端部署"
echo "=========================================="
echo ""

# 第1步：检查文件上传情况
echo "【第1步】检查文件上传情况..."
echo ""
echo "文件列表："
ls -lh /data/pinguan_frontend/ | head -20
echo ""

echo "文件总数："
ls -1 /data/pinguan_frontend/ | wc -l
echo ""

echo "检查关键文件："
if [ -f "/data/pinguan_frontend/index.html" ]; then
    echo "✅ index.html 存在"
else
    echo "❌ index.html 不存在"
fi

if [ -d "/data/pinguan_frontend/assets" ]; then
    echo "✅ assets 目录存在"
    echo "   assets 文件数: $(ls -1 /data/pinguan_frontend/assets/ | wc -l)"
else
    echo "❌ assets 目录不存在"
fi
echo ""

# 第2步：配置nginx
echo "【第2步】配置nginx..."
cat > /etc/nginx/conf.d/pinguan.conf << 'EOF'
server {
    listen 6039;
    server_name _;

    root /data/pinguan_frontend;
    index index.html;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json;

    # 前端静态文件
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理到后端（端口6031）
    location /api/ {
        proxy_pass http://localhost:6031/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

if [ $? -eq 0 ]; then
    echo "✅ nginx配置文件创建成功"
else
    echo "❌ nginx配置文件创建失败"
    exit 1
fi
echo ""

# 第3步：测试nginx配置
echo "【第3步】测试nginx配置..."
nginx -t
if [ $? -eq 0 ]; then
    echo "✅ nginx配置测试通过"
else
    echo "❌ nginx配置测试失败"
    exit 1
fi
echo ""

# 第4步：重启nginx
echo "【第4步】重启nginx..."
systemctl restart nginx
if [ $? -eq 0 ]; then
    echo "✅ nginx重启成功"
else
    echo "❌ nginx重启失败"
    exit 1
fi
echo ""

# 第5步：检查服务状态
echo "【第5步】检查服务状态..."
echo ""

echo "nginx运行状态："
systemctl is-active nginx
echo ""

echo "前端端口 6039："
netstat -tuln | grep 6039
if [ $? -eq 0 ]; then
    echo "✅ 端口 6039 正在监听"
else
    echo "❌ 端口 6039 未监听"
fi
echo ""

echo "后端端口 6031："
netstat -tuln | grep 6031
if [ $? -eq 0 ]; then
    echo "✅ 后端端口 6031 正在监听"
else
    echo "⚠️  后端端口 6031 未监听（请检查后端服务是否启动）"
fi
echo ""

# 第6步：测试访问
echo "【第6步】测试本地访问..."
echo ""

echo "测试静态文件："
curl -I http://localhost:6039 2>&1 | head -5
echo ""

echo "测试API代理："
curl -I http://localhost:6039/api/dictionary 2>&1 | head -5
echo ""

echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "请在浏览器访问："
echo "  http://81.71.44.180:6039"
echo ""
echo "如果无法访问，请检查："
echo "  1. 防火墙是否开放 6039 端口"
echo "  2. 后端服务是否运行在 6031 端口"
echo "  3. nginx错误日志: tail -f /var/log/nginx/error.log"
echo "=========================================="
