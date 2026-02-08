// 在浏览器控制台运行此脚本，查看报名详情API返回的完整数据
// 请将 REGISTRATION_ID 替换为实际的报名ID

const REGISTRATION_ID = 164; // 替换为实际的报名ID

(async function testRegistrationDetailAPI() {
  console.log('🧪 测试报名详情API');
  console.log('='.repeat(80));
  
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('❌ 未找到 token');
      return;
    }
    
    console.log(`📊 调用: GET /api/registrations/${REGISTRATION_ID}`);
    
    const response = await fetch(`/api/registrations/${REGISTRATION_ID}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('状态码:', response.status);
    
    const result = await response.json();
    
    if (result.success) {
      console.log('✅ 获取成功');
      
      const data = result.data;
      
      console.log('\n📦 顶层结构:');
      console.log('='.repeat(80));
      Object.keys(data).forEach(key => {
        console.log(`  - ${key}: ${typeof data[key]}`);
      });
      
      if (data.registration) {
        console.log('\n📝 registration 对象的字段:');
        console.log('='.repeat(80));
        Object.keys(data.registration).forEach(key => {
          const value = data.registration[key];
          console.log(`  - ${key}: ${value}`);
        });
      }
      
      console.log('\n📄 完整数据:');
      console.log('='.repeat(80));
      console.log(data);
      
      console.log('\n🔍 关键字段检查:');
      console.log('='.repeat(80));
      console.log('subjectType (主题类型):', data.registration?.subjectType);
      console.log('qualityTools (品管工具):', data.registration?.qualityTools);
      console.log('activityInfo (活动说明):', data.activityInfo ? '有数据' : '无');
      console.log('projectSummary (项目摘要):', data.projectSummary ? '有数据' : '无');
      console.log('materials (材料):', data.materials ? `${data.materials.length} 个` : '无');
      
    } else {
      console.error('❌ 请求失败:', result.message);
    }
    
  } catch (error) {
    console.error('❌ 发生错误:', error);
  }
})();
