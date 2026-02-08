<template>
  <div class="statistics-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报名统计 - {{ stats.competitionName }}</span>
        </div>
      </template>
      
      <el-row :gutter="20" style="margin-bottom: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
            <el-statistic 
              title="总报名数" 
              :value="stats.totalRegistrations" 
              style="text-align: center"
            />
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 第一行：地区分布 + 主题类型分布 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <div ref="regionChart" style="height: 400px"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <div ref="subjectChart" style="height: 400px"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 第二行：评分雷达图 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card>
            <div ref="radarChart" style="height: 450px"></div>
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
import { getStatsSummary } from '@/api/admin'

const subjectChart = ref(null)
const regionChart = ref(null)
const radarChart = ref(null)

const stats = reactive({
  totalRegistrations: 0,
  competitionName: ''
})

const loadData = async () => {
  try {
    console.log('📊 正在加载统计数据...')
    
    // 获取当前赛事ID，默认为21（2026浙江品管大赛）
    const competitionId = localStorage.getItem('currentCompetitionId') || 21
    console.log('   当前赛事ID:', competitionId)
    
    // 调用后端统计接口，传递 competitionId 参数
    const res = await getStatsSummary({ competitionId })
    
    if (res.success && res.data) {
      const summaryData = res.data
      console.log('✅ 后端返回的原始数据:', summaryData)
      
      // 直接使用后端数据，不做任何前端处理
      stats.competitionName = summaryData.competitionName || ''
      stats.totalRegistrations = summaryData.registrationCount || 0
      
      await nextTick()
      initCharts(summaryData)
      
      ElMessage.success(`${summaryData.competitionName} 统计数据加载成功`)
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

const initCharts = (summaryData = {}) => {
  // 1. 地区分布饼图（统一从 regionCounts 读取）
  if (regionChart.value) {
    const chart = echarts.init(regionChart.value)
    
    const regionCounts = summaryData.regionCounts || {}
    
    // 转换为数组并按数量排序
    const regionData = Object.entries(regionCounts)
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
  
  // 2. 主题类型分布饼图（统一从 subjectTypeCounts 读取）
  if (subjectChart.value) {
    const chart = echarts.init(subjectChart.value)
    
    const subjectTypeCounts = summaryData.subjectTypeCounts || {}
    
    // 转换为数组并按数量排序
    const subjectData = Object.entries(subjectTypeCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
    
    chart.setOption({
      title: {
        text: '主题类型分布',
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
          name: '主题类型',
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
          data: subjectData,
          color: [
            '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272',
            '#fc8452', '#9a60b4', '#ea7ccc', '#5470c6', '#d14a61'
          ]
        }
      ]
    })
  }
  
  // 3. 评分雷达图（7个维度的平均分）
  if (radarChart.value) {
    const chart = echarts.init(radarChart.value)
    
    const avgScores = [
      summaryData.avgPlan || 0,
      summaryData.avgProblem || 0,
      summaryData.avgAction || 0,
      summaryData.avgSuccess || 0,
      summaryData.avgReview || 0,
      summaryData.avgOperation || 0,
      summaryData.avgPresentation || 0
    ]
    
    chart.setOption({
      title: {
        text: '平均评分',
        left: 'center',
        top: '5%'
      },
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          const names = ['计划', '问题', '行动', '成功', '回顾', '运作', '展示']
          let html = '<div><strong>平均评分</strong></div>'
          params.value.forEach((val, idx) => {
            html += `<div>${names[idx]}: ${val.toFixed(1)} 分</div>`
          })
          return html
        }
      },
      radar: {
        indicator: [
          { name: '计划', max: 20 },
          { name: '问题', max: 20 },
          { name: '行动', max: 20 },
          { name: '成功', max: 20 },
          { name: '回顾', max: 20 },
          { name: '运作', max: 20 },
          { name: '展示', max: 20 }
        ],
        center: ['50%', '50%'],
        radius: '60%'
      },
      series: [
        {
          name: '平均评分',
          type: 'radar',
          data: [
            {
              value: avgScores,
              name: '平均分',
              areaStyle: {
                color: 'rgba(91, 143, 249, 0.3)'
              },
              lineStyle: {
                color: '#5b8ff9',
                width: 2
              },
              itemStyle: {
                color: '#5b8ff9'
              }
            }
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
