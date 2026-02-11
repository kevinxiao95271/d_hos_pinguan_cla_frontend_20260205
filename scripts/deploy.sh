#!/bin/bash

# 浙江省品管大赛前端部署脚本
# 服务器: 81.71.44.180
# 用户: root
# 密码: Yiguo9527_

echo "=========================================="
echo "开始部署前端到服务器"
echo "=========================================="

# 服务器信息
SERVER="81.71.44.180"
USER="root"
REMOTE_DIR="/data/pinguan_frontend"

# 1. 确保本地已构建
if [ ! -d "dist" ]; then
  echo "❌ dist目录不存在，请先运行: npm run build"
  exit 1
fi

echo "✅ 找到dist目录"

# 2. 在服务器创建目录
echo "📁 在服务器创建部署目录..."
ssh ${USER}@${SERVER} "mkdir -p ${REMOTE_DIR}"

if [ $? -ne 0 ]; then
  echo "❌ 创建目录失败"
  exit 1
fi

echo "✅ 服务器目录创建成功"

# 3. 上传文件
echo "📤 上传构建文件到服务器..."
scp -r dist/* ${USER}@${SERVER}:${REMOTE_DIR}/

if [ $? -ne 0 ]; then
  echo "❌ 文件上传失败"
  exit 1
fi

echo "✅ 文件上传成功"

# 4. 创建nginx配置（如果需要）
echo "📝 创建nginx配置..."
ssh ${USER}@${SERVER} "cat > /etc/nginx/conf.d/pinguan.conf << 'EOF'
server {
    listen 6039;
    server_name _;
    
    root ${REMOTE_DIR};
    index index.html;
    
    # 启用gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # API代理到后端
    location /api/ {
        proxy_pass http://localhost:6031/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF
"

# 5. 重启nginx
echo "🔄 重启nginx服务..."
ssh ${USER}@${SERVER} "nginx -t && systemctl restart nginx"

if [ $? -eq 0 ]; then
  echo "✅ Nginx重启成功"
  echo ""
  echo "=========================================="
  echo "🎉 部署完成！"
  echo "访问地址: http://81.71.44.180:6039"
  echo "=========================================="
else
  echo "❌ Nginx重启失败，请检查配置"
  exit 1
fi
