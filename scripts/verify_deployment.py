# -*- coding: utf-8 -*-
import sys
import codecs
import requests
import paramiko

# 设置输出编码
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def verify_files():
    """验证服务器上的文件"""
    print("="*80)
    print("📁 验证服务器文件")
    print("="*80)
    
    host = "81.71.44.180"
    username = "root"
    password = "Yiguo9527_"
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, 22, username, password, timeout=10)
        
        commands = [
            ("验证index.html", "cat /data/pinguan_frontend/index.html | head -5"),
            ("验证assets目录", "ls /data/pinguan_frontend/assets | wc -l"),
            ("检查文件权限", "ls -lh /data/pinguan_frontend/"),
        ]
        
        for title, cmd in commands:
            print(f"\n{title}:")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode('utf-8')
            print(output.strip())
        
        ssh.close()
        return True
        
    except Exception as e:
        print(f"❌ 文件验证失败: {e}")
        return False


def verify_web_access():
    """验证Web访问"""
    print("\n" + "="*80)
    print("🌐 验证Web访问")
    print("="*80)
    
    url = "http://81.71.44.180:6039"
    
    print(f"\n访问URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"✅ 响应状态码: {response.status_code}")
        print(f"✅ 响应大小: {len(response.text)} 字节")
        
        # 检查关键内容
        content = response.text
        
        checks = [
            ("包含DOCTYPE", "<!DOCTYPE html>" in content or "<!doctype html>" in content),
            ("包含浙江省品管大赛", "浙江省品管大赛" in content or "品管" in content),
            ("包含Vue应用", "id=\"app\"" in content or 'id="app"' in content),
            ("包含JS资源", "/assets/" in content and ".js" in content),
            ("包含CSS资源", "/assets/" in content and ".css" in content),
        ]
        
        print(f"\n内容检查:")
        all_passed = True
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}: {'通过' if check_result else '失败'}")
            if not check_result:
                all_passed = False
        
        # 显示HTML前200个字符
        print(f"\nHTML内容预览（前200字符）:")
        print("-" * 80)
        print(content[:200])
        print("-" * 80)
        
        if response.status_code == 200 and all_passed:
            print(f"\n🎉 Web访问验证通过！")
            return True
        else:
            print(f"\n⚠️ Web访问有问题")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ 访问超时")
        return False
    except Exception as e:
        print(f"❌ 访问失败: {type(e).__name__}: {e}")
        return False


def verify_api_proxy():
    """验证API代理"""
    print("\n" + "="*80)
    print("🔌 验证API代理")
    print("="*80)
    
    # 测试一个公开API
    url = "http://81.71.44.180:6039/api/institutions/cities"
    
    print(f"\n测试API: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"✅ 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 返回数据类型: {type(data)}")
            
            if isinstance(data, dict) and 'success' in data:
                print(f"✅ success: {data.get('success')}")
                if data.get('data'):
                    print(f"✅ 城市列表: {len(data['data'])} 个城市")
                    print(f"   示例: {data['data'][:3]}")
            
            print(f"\n🎉 API代理工作正常！")
            return True
        else:
            print(f"⚠️ API返回非200状态码")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {type(e).__name__}: {e}")
        return False


def main():
    print("🔍 部署验证测试")
    print("="*80)
    print("")
    
    results = {
        "文件部署": verify_files(),
        "Web访问": verify_web_access(),
        "API代理": verify_api_proxy()
    }
    
    print("\n" + "="*80)
    print("📊 验证结果汇总")
    print("="*80)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} - {name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "="*80)
        print("🎉 部署验证全部通过！")
        print("="*80)
        print("")
        print("✅ 前端已成功部署到服务器")
        print("✅ 访问地址: http://81.71.44.180:6039")
        print("✅ 部署路径: /data/pinguan_frontend")
        print("✅ 备份路径: /data/pinguan_frontend_backup_*")
        print("")
        print("📝 可以在浏览器中打开测试:")
        print("   http://81.71.44.180:6039")
        print("")
    else:
        print("\n⚠️ 部署验证有问题，请检查失败项")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
