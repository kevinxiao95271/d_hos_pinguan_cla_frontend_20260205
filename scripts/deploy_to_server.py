#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端部署脚本
自动部署到服务器并配置nginx
"""

import paramiko
import sys
import os
import time
from pathlib import Path

# 设置Windows终端编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class DeployManager:
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssh = None
        self.sftp = None
    
    def connect(self):
        """连接服务器"""
        try:
            print(f"🔌 正在连接服务器 {self.host}...")
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            self.sftp = self.ssh.open_sftp()
            print("✅ 连接成功！\n")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def execute_command(self, command, description=None):
        """执行命令"""
        if description:
            print(f"🔧 {description}...")
        
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            if exit_code == 0:
                if output:
                    print(output)
                return True, output
            else:
                if error:
                    print(f"⚠️  警告: {error}")
                return False, error
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            return False, str(e)
    
    def check_files_uploaded(self):
        """检查文件是否上传完毕"""
        print("=" * 60)
        print("【第1步】检查文件上传情况")
        print("=" * 60)
        
        # 检查目录是否存在
        success, output = self.execute_command(
            "test -d /data/pinguan_frontend && echo 'EXISTS' || echo 'NOT_EXISTS'"
        )
        
        if 'NOT_EXISTS' in output:
            print("❌ 目录 /data/pinguan_frontend 不存在")
            print("   请确认您已经上传文件到该目录")
            return False
        
        # 检查文件数量
        success, output = self.execute_command(
            "ls -1 /data/pinguan_frontend/ | wc -l",
            "统计文件数量"
        )
        file_count = int(output.strip()) if success else 0
        print(f"   文件总数: {file_count}")
        
        # 检查关键文件
        success, output = self.execute_command(
            "ls -lh /data/pinguan_frontend/ | head -20",
            "列出文件清单"
        )
        
        # 检查index.html
        success, output = self.execute_command(
            "test -f /data/pinguan_frontend/index.html && echo 'YES' || echo 'NO'"
        )
        has_index = 'YES' in output
        print(f"   index.html: {'✅ 存在' if has_index else '❌ 不存在'}")
        
        # 检查assets目录
        success, output = self.execute_command(
            "test -d /data/pinguan_frontend/assets && echo 'YES' || echo 'NO'"
        )
        has_assets = 'YES' in output
        print(f"   assets目录: {'✅ 存在' if has_assets else '❌ 不存在'}")
        
        if has_assets:
            success, output = self.execute_command(
                "ls -1 /data/pinguan_frontend/assets/ | wc -l"
            )
            assets_count = int(output.strip()) if success else 0
            print(f"   assets文件数: {assets_count}")
        
        print()
        
        if not has_index or not has_assets:
            print("❌ 文件上传不完整，请检查！")
            return False
        
        if has_assets and assets_count < 10:
            print("❌ assets目录文件过少，请检查！")
            return False
        
        print("✅ 文件上传完整\n")
        return True
    
    def check_existing_nginx_config(self):
        """检查现有nginx配置"""
        print("=" * 60)
        print("【第2步】检查现有nginx配置")
        print("=" * 60)
        
        # 列出所有nginx配置文件
        success, output = self.execute_command(
            "ls -lh /etc/nginx/conf.d/",
            "列出现有配置文件"
        )
        
        # 检查是否已存在pinguan.conf
        success, output = self.execute_command(
            "test -f /etc/nginx/conf.d/pinguan.conf && echo 'EXISTS' || echo 'NOT_EXISTS'"
        )
        
        if 'EXISTS' in output:
            print("⚠️  发现现有配置文件 /etc/nginx/conf.d/pinguan.conf")
            print("   将进行备份...")
            
            # 备份现有配置
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.execute_command(
                f"cp /etc/nginx/conf.d/pinguan.conf /etc/nginx/conf.d/pinguan.conf.backup_{timestamp}",
                "备份现有配置"
            )
            print(f"   ✅ 已备份到 pinguan.conf.backup_{timestamp}")
        else:
            print("✅ 未发现冲突配置文件")
        
        print()
        return True
    
    def create_nginx_config(self):
        """创建nginx配置"""
        print("=" * 60)
        print("【第3步】创建nginx配置")
        print("=" * 60)
        
        nginx_config = """server {
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
}"""
        
        # 写入配置文件
        command = f"cat > /etc/nginx/conf.d/pinguan.conf << 'EOF'\n{nginx_config}\nEOF"
        success, output = self.execute_command(command, "写入配置文件")
        
        if not success:
            print("❌ 配置文件创建失败")
            return False
        
        print("✅ 配置文件创建成功")
        
        # 显示配置内容
        print("\n配置内容预览：")
        self.execute_command("cat /etc/nginx/conf.d/pinguan.conf")
        
        print()
        return True
    
    def test_and_reload_nginx(self):
        """测试nginx配置并重启"""
        print("=" * 60)
        print("【第4步】测试并重启nginx")
        print("=" * 60)
        
        # 测试配置
        success, output = self.execute_command(
            "nginx -t",
            "测试nginx配置"
        )
        
        if not success:
            print("❌ nginx配置测试失败！")
            print("   配置文件有错误，不会重启nginx")
            return False
        
        print("✅ nginx配置测试通过")
        
        # 重启nginx
        success, output = self.execute_command(
            "systemctl restart nginx",
            "重启nginx服务"
        )
        
        if not success:
            print("❌ nginx重启失败")
            return False
        
        print("✅ nginx重启成功")
        
        # 检查状态
        time.sleep(2)
        success, output = self.execute_command(
            "systemctl is-active nginx",
            "检查nginx状态"
        )
        
        if 'active' in output:
            print("✅ nginx运行正常")
        else:
            print("⚠️  nginx状态异常")
        
        print()
        return True
    
    def verify_deployment(self):
        """验证部署"""
        print("=" * 60)
        print("【第5步】验证部署")
        print("=" * 60)
        
        # 检查前端端口
        success, output = self.execute_command(
            "netstat -tuln | grep 6039",
            "检查前端端口 6039"
        )
        
        if success and '6039' in output:
            print("✅ 前端端口 6039 正在监听")
        else:
            print("❌ 前端端口 6039 未监听")
        
        # 检查后端端口
        success, output = self.execute_command(
            "netstat -tuln | grep 6031",
            "检查后端端口 6031"
        )
        
        if success and '6031' in output:
            print("✅ 后端端口 6031 正在监听")
        else:
            print("⚠️  后端端口 6031 未监听（请确认后端服务是否运行）")
        
        # 测试静态文件访问
        print("\n测试静态文件访问：")
        success, output = self.execute_command(
            "curl -I http://localhost:6039 2>&1 | head -5"
        )
        
        if '200 OK' in output or '304' in output:
            print("✅ 静态文件访问正常")
        else:
            print("⚠️  静态文件访问异常")
        
        # 测试API代理
        print("\n测试API代理：")
        success, output = self.execute_command(
            "curl -I http://localhost:6039/api/dictionary 2>&1 | head -5"
        )
        
        if '200' in output or '401' in output or '403' in output:
            print("✅ API代理配置正常")
        else:
            print("⚠️  API代理可能有问题")
        
        print()
    
    def show_summary(self):
        """显示部署摘要"""
        print("=" * 60)
        print("🎉 部署完成！")
        print("=" * 60)
        print()
        print(f"✅ 前端访问地址: http://{self.host}:6039")
        print(f"✅ API代理地址: http://{self.host}:6039/api/")
        print()
        print("📝 如果无法访问，请检查：")
        print("   1. 防火墙是否开放 6039 端口")
        print("   2. 后端服务是否运行在 6031 端口")
        print("   3. nginx错误日志: tail -f /var/log/nginx/error.log")
        print()
        print("📋 相关命令：")
        print("   查看nginx状态: systemctl status nginx")
        print("   查看配置文件: cat /etc/nginx/conf.d/pinguan.conf")
        print("   重启nginx: systemctl restart nginx")
        print("=" * 60)
    
    def close(self):
        """关闭连接"""
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()
        print("\n🔌 已断开连接")


def main():
    # 服务器信息
    HOST = "81.71.44.180"
    USERNAME = "root"
    PASSWORD = "Yiguo9527_"
    PORT = 22
    
    print("=" * 60)
    print("浙江省品管大赛前端自动部署脚本")
    print("=" * 60)
    print(f"服务器: {HOST}")
    print(f"前端端口: 6039")
    print(f"后端端口: 6031")
    print("=" * 60)
    print()
    
    deploy = DeployManager(HOST, USERNAME, PASSWORD, PORT)
    
    try:
        # 连接服务器
        if not deploy.connect():
            sys.exit(1)
        
        # 检查文件上传
        if not deploy.check_files_uploaded():
            print("\n❌ 部署中止：文件上传不完整")
            sys.exit(1)
        
        # 检查现有配置
        deploy.check_existing_nginx_config()
        
        # 创建nginx配置
        if not deploy.create_nginx_config():
            print("\n❌ 部署失败：配置文件创建失败")
            sys.exit(1)
        
        # 测试并重启nginx
        if not deploy.test_and_reload_nginx():
            print("\n❌ 部署失败：nginx配置或重启失败")
            sys.exit(1)
        
        # 验证部署
        deploy.verify_deployment()
        
        # 显示摘要
        deploy.show_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断部署")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 部署过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        deploy.close()


if __name__ == "__main__":
    main()
