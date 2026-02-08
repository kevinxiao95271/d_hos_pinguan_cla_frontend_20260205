// 在浏览器控制台中运行此脚本来测试 API
// 1. 打开浏览器开发者工具 (F12)
// 2. 切换到 Console 标签
// 3. 复制并粘贴下面的代码，按回车执行

(async function testMyRegistrationsAPI() {
  console.log('🧪 测试"我的报名"API');
  console.log('='.repeat(80));
  
  try {
    // 获取 token
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('❌ 未找到 token，请先登录');
      return;
    }
    
    console.log('✅ Token:', token.substring(0, 20) + '...');
    
    // 调用 API
    console.log('\n📊 调用: GET /api/registrations/my');
    console.log('='.repeat(80));
    
    const response = await fetch('/api/registrations/my', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('状态码:', response.status);
    
    const result = await response.json();
    
    // 打印完整响应
    console.log('\n📦 完整响应:');
    console.log(JSON.stringify(result, null, 2));
    
    if (result.success) {
      const data = result.data || [];
      console.log(`\n✅ 获取成功: ${data.length} 条报名记录`);
      
      if (data.length > 0) {
        const first = data[0];
        
        console.log('\n📝 第一条数据的字段:');
        console.log('='.repeat(80));
        
        // 列出所有字段
        Object.keys(first).forEach(key => {
          const value = first[key];
          const type = typeof value;
          console.log(`  ${key}: ${type}`);
        });
        
        console.log('\n🔍 关键字段检查:');
        console.log('='.repeat(80));
        
        const checkField = (field, label) => {
          const exists = field in first;
          const value = first[field];
          const status = exists ? '✅' : '❌';
          
          if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            console.log(`${status} ${label} (${field}): 对象`);
            Object.keys(value).forEach(k => {
              console.log(`     - ${k}: ${value[k]}`);
            });
          } else {
            console.log(`${status} ${label} (${field}): ${value}`);
          }
        };
        
        checkField('id', 'ID');
        checkField('projectName', '项目名称');
        checkField('institutionId', '机构ID');
        checkField('institutionName', '机构名称（平铺）');
        checkField('institutionLevel', '机构等级（平铺）');
        checkField('institution', '机构对象（嵌套）');
        checkField('groupType', '竞赛组别');
        checkField('status', '状态');
        
        console.log('\n📄 完整的第一条数据:');
        console.log('='.repeat(80));
        console.log(first);
        
      } else {
        console.warn('⚠️  没有报名记录');
      }
    } else {
      console.error('❌ 请求失败:', result.message);
    }
    
  } catch (error) {
    console.error('❌ 发生错误:', error);
  }
})();
