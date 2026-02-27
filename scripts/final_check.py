# -*- coding: utf-8 -*-
import sys
import codecs
import requests

# 设置输出编码
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def final_check():
    """最终验证"""
    
    url = "http://81.71.44.180:6039"
    
    print("🔍 最终验证部署结果")
    print("="*80)
    print(f"访问地址: {url}")
    print("")
    
    try:
        # 访问首页
        print("⏳ 正在访问首页...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ HTTP状态码: 200 OK")
            print(f"✅ 页面大小: {len(response.text)} 字节")
            
            content = response.text
            
            # 显示完整HTML
            print(f"\n📄 完整HTML内容:")
            print("-"*80)
            print(content)
            print("-"*80)
            
            # 关键检查
            print(f"\n✅ 关键检查:")
            
            checks = {
                "HTML结构": "<!DOCTYPE html>" in content,
                "Vue应用容器": 'id="app"' in content,
                "引入主JS": "/assets/index-" in content and ".js" in content,
                "引入主CSS": "/assets/index-" in content and ".css" in content,
            }
            
            all_good = True
            for name, result in checks.items():
                status = "✅" if result else "❌"
                print(f"  {status} {name}")
                if not result:
                    all_good = False
            
            if all_good:
                print(f"\n{'='*80}")
                print(f"🎉 部署成功！所有检查通过！")
                print(f"{'='*80}")
                print(f"\n请在浏览器中访问:")
                print(f"  {url}")
                print(f"\n应该能看到:")
                print(f"  ✅ 浙江省品管大赛管理系统 登录页面")
                print(f"  ✅ 手机号输入框")
                print(f"  ✅ 密码输入框")
                print(f"  ✅ 登录按钮")
                print(f"  ❌ 无英文标题")
                print(f"  ❌ 无测试账号按钮")
                print("")
            else:
                print(f"\n⚠️ 有些检查未通过")
            
            return all_good
        else:
            print(f"❌ HTTP状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 访问失败: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    success = final_check()
    sys.exit(0 if success else 1)
