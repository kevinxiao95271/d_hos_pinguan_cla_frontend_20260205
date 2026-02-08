// 在浏览器控制台运行此脚本，检查活动信息的Label字段
// 使用方法：复制粘贴到浏览器Console，按回车执行

const REGISTRATION_ID = 119; // 替换为实际的报名ID

(async function testActivityInfoLabels() {
  console.log('🧪 测试活动信息Label字段');
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
    
    if (result.success && result.data) {
      console.log('✅ 获取成功');
      
      const activityInfo = result.data.activityInfo;
      
      if (activityInfo) {
        console.log('\n📝 activityInfo 完整数据:');
        console.log('='.repeat(80));
        console.log(JSON.stringify(activityInfo, null, 2));
        
        console.log('\n🔍 关键字段检查:');
        console.log('='.repeat(80));
        
        // 主题类型
        console.log('\n【主题类型】');
        console.log('  subjectTypeCode:', activityInfo.subjectTypeCode);
        console.log('  subjectTypeLabel:', activityInfo.subjectTypeLabel);
        
        // 运用手法
        console.log('\n【运用手法】');
        console.log('  methodCode:', activityInfo.methodCode);
        console.log('  methodLabel:', activityInfo.methodLabel);
        
        // 改善就医环境
        console.log('\n【改善就医环境】');
        console.log('  experienceImproveCode:', activityInfo.experienceImproveCode);
        console.log('  experienceImproveLabel:', activityInfo.experienceImproveLabel);
        console.log('  experienceImproveOther:', activityInfo.experienceImproveOther);
        
        // 医疗质量相关主题
        console.log('\n【医疗质量相关主题】');
        console.log('  qualityTopicCode:', activityInfo.qualityTopicCode);
        console.log('  qualityTopicLabel:', activityInfo.qualityTopicLabel);
        console.log('  qualityTopicOther:', activityInfo.qualityTopicOther);
        
        // 其他字段
        console.log('\n【其他字段】');
        console.log('  avgWorkYears:', activityInfo.avgWorkYears);
        console.log('  avgAge:', activityInfo.avgAge);
        console.log('  crossDepartment:', activityInfo.crossDepartment);
        console.log('  relatedToDigitalAi:', activityInfo.relatedToDigitalAi);
        
        console.log('\n📋 总结:');
        console.log('='.repeat(80));
        console.log('如果Label字段有值，应该优先显示Label而不是Code');
        console.log('如果Label字段为空或undefined，则显示Code');
        
      } else {
        console.warn('⚠️  activityInfo 不存在');
      }
      
    } else {
      console.error('❌ 请求失败:', result.message);
    }
    
  } catch (error) {
    console.error('❌ 发生错误:', error);
  }
})();
