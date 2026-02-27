#!/bin/bash

# 部署脚本
# 服务器: 81.71.44.180
# 用户: root
# 目标路径: /data

SERVER="81.71.44.180"
USER="root"
TARGET_PATH="/data/frontend"

echo "📦 开始部署到服务器..."
echo "服务器: $SERVER"
echo "目标路径: $TARGET_PATH"
echo ""

# 1. 打包dist目录
echo "📦 打包dist目录..."
cd dist
tar -czf ../dist.tar.gz .
cd ..
echo "✅ 打包完成: dist.tar.gz"
echo ""

# 2. 上传到服务器
echo "📤 上传到服务器..."
scp dist.tar.gz $USER@$SERVER:/tmp/
echo "✅ 上传完成"
echo ""

# 3. 在服务器上解压
echo "📂 在服务器上部署..."
ssh $USER@$SERVER << 'ENDSSH'
# 创建目标目录
mkdir -p /data/frontend

# 备份旧版本
if [ -d "/data/frontend/dist" ]; then
    echo "📦 备份旧版本..."
    mv /data/frontend/dist /data/frontend/dist.backup.$(date +%Y%m%d_%H%M%S)
fi

# 解压新版本
echo "📂 解压新版本..."
mkdir -p /data/frontend/dist
tar -xzf /tmp/dist.tar.gz -C /data/frontend/dist

# 清理临时文件
rm -f /tmp/dist.tar.gz

echo "✅ 部署完成！"
echo "访问路径: /data/frontend/dist"
ENDSSH

# 4. 清理本地临时文件
echo ""
echo "🧹 清理本地临时文件..."
rm -f dist.tar.gz

echo ""
echo "🎉 部署完成！"
echo "服务器路径: /data/frontend/dist"
