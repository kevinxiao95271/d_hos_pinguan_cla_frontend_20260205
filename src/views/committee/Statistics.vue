<template>
  <div class="statistics-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报名统计</span>
        </div>
      </template>
      
      <el-row :gutter="20" style="margin-bottom: 20px">
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="总报名数" :value="stats.totalRegistrations" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="基层组" :value="stats.basicGroup" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="综合组" :value="stats.comprehensiveGroup" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="进阶组" :value="stats.advancedGroup" />
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <div ref="groupChart" style="height: 350px"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <div ref="regionChart" style="height: 350px"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card>
            <div ref="methodChart" style="height: 400px"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card>
            <div ref="subjectChart" style="height: 400px"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { filterRegistrations } from '@/api/admin'

const groupChart = ref(null)
const methodChart = ref(null)
const subjectChart = ref(null)
const regionChart = ref(null)

const stats = reactive({
  totalRegistrations: 0,
  basicGroup: 0,
  comprehensiveGroup: 0,
  advancedGroup: 0
})

const loadData = async () => {
  try {
    console.log('📊 正在加载统计数据...')
    
    // 获取当前赛事ID，默认使用 21
    const competitionId = localStorage.getItem('currentCompetitionId') || 21
    
    // 使用优化后的 admin 接口
    const res = await filterRegistrations({ competitionId })
    
    if (res.success && res.data) {
      const registrations = res.data
      console.log('✅ 获取到报名数据:', registrations.length, '条')
      
      // 计算统计数据
      stats.totalRegistrations = registrations.length
      stats.basicGroup = registrations.filter(r => r.groupType === 'BASIC').length
      stats.comprehensiveGroup = registrations.filter(r => r.groupType === 'COMPREHENSIVE').length
      stats.advancedGroup = registrations.filter(r => r.groupType === 'ADVANCED').length
      
      console.log('📊 统计结果:', stats)
      
      await nextTick()
      initCharts(registrations)
      
      if (registrations.length > 0) {
        ElMessage.success(`统计数据加载成功，共 ${registrations.length} 条报名`)
      } else {
        ElMessage.info('暂无报名数据')
      }
    } else {
      console.error('❌ 加载统计数据失败:', res.message)
      ElMessage.warning('加载统计数据失败: ' + (res.message || '未知错误'))
    }
  } catch (error) {
    console.error('❌ 加载统计数据失败:', error)
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error('加载统计数据失败，请检查网络或登录状态')
    }
  }
}

const initCharts = (registrations = []) => {
  // 竞赛组别分布
  if (groupChart.value) {
    const chart = echarts.init(groupChart.value)
    chart.setOption({
      title: {
        text: '竞赛组别分布',
        left: 'center',
        top: '5%'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        bottom: '8%',
        left: 'center'
      },
      series: [
        {
          name: '竞赛组别',
          type: 'pie',
          radius: ['30%', '55%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}\n({d}%)',
            fontSize: 12
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            }
          },
          data: [
            { value: stats.basicGroup, name: '基层组' },
            { value: stats.comprehensiveGroup, name: '综合组' },
            { value: stats.advancedGroup, name: '进阶组' }
          ]
        }
      ]
    })
  }
  
  // 品管工具分布（从实际数据计算）
  if (methodChart.value && registrations.length > 0) {
    const chart = echarts.init(methodChart.value)
    
    // 统计各品管工具的使用次数
    const methodStats = {}
    registrations.forEach(r => {
      const method = r.methodLabel || '未知'
      methodStats[method] = (methodStats[method] || 0) + 1
    })
    
    // 按数量排序
    const sortedMethods = Object.entries(methodStats)
      .sort((a, b) => b[1] - a[1])
    
    const methodNames = sortedMethods.map(item => item[0])
    const methodCounts = sortedMethods.map(item => item[1])
    
    chart.setOption({
      title: {
        text: '品管工具分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: '{b}: {c} 个项目'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: methodNames,
        axisLabel: {
          rotate: 45,
          interval: 0,
          fontSize: 11
        }
      },
      yAxis: {
        type: 'value',
        name: '项目数量'
      },
      series: [
        {
          data: methodCounts,
          type: 'bar',
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          },
          emphasis: {
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#2378f7' },
                { offset: 0.7, color: '#2378f7' },
                { offset: 1, color: '#83bff6' }
              ])
            }
          }
        }
      ]
    })
  }
  
  // 主题类型分布（从实际数据计算）
  if (subjectChart.value && registrations.length > 0) {
    const chart = echarts.init(subjectChart.value)
    
    // 统计各主题类型的使用次数
    const subjectStats = {}
    registrations.forEach(r => {
      const subject = r.subjectTypeLabel || '未知'
      subjectStats[subject] = (subjectStats[subject] || 0) + 1
    })
    
    // 按数量排序
    const sortedSubjects = Object.entries(subjectStats)
      .sort((a, b) => b[1] - a[1])
    
    const subjectNames = sortedSubjects.map(item => item[0])
    const subjectCounts = sortedSubjects.map(item => item[1])
    
    chart.setOption({
      title: {
        text: '主题类型分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: '{b}: {c} 个项目'
      },
      grid: {
        left: '20%',
        right: '4%',
        bottom: '3%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '项目数量'
      },
      yAxis: {
        type: 'category',
        data: subjectNames,
        axisLabel: {
          fontSize: 11
        }
      },
      series: [
        {
          name: '项目数',
          type: 'bar',
          data: subjectCounts,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#73c0de' },
              { offset: 0.5, color: '#5470c6' },
              { offset: 1, color: '#5470c6' }
            ])
          }
        }
      ]
    })
  }
  
  // 地区分布（从机构名称提取）
  if (regionChart.value && registrations.length > 0) {
    const chart = echarts.init(regionChart.value)
    
    // 从机构名称中提取地区
    const regionStats = {}
    const cityKeywords = ['杭州', '宁波', '温州', '绍兴', '嘉兴', '湖州', 
                         '金华', '衢州', '台州', '丽水', '舟山']
    
    registrations.forEach(r => {
      const institutionName = r.institutionName || ''
      let cityFound = false
      
      for (const city of cityKeywords) {
        if (institutionName.includes(city)) {
          regionStats[city] = (regionStats[city] || 0) + 1
          cityFound = true
          break
        }
      }
      
      if (!cityFound && institutionName) {
        regionStats['其他'] = (regionStats['其他'] || 0) + 1
      }
    })
    
    // 转换为数组并排序
    const regionData = Object.entries(regionStats)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
    
    chart.setOption({
      title: {
        text: '地区分布',
        left: 'center',
        top: '5%'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} 个项目 ({d}%)'
      },
      legend: {
        bottom: '8%',
        left: 'center',
        orient: 'horizontal',
        type: 'scroll'
      },
      series: [
        {
          name: '地区分布',
          type: 'pie',
          radius: ['30%', '55%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}\n{d}%',
            fontSize: 11
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 13,
              fontWeight: 'bold'
            }
          },
          data: regionData,
          color: [
            '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
            '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#d14a61',
            '#5ab1ef', '#ffb980'
          ]
        }
      ]
    })
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.statistics-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
}
</style>
