<template>
  <div class="stage-progress-wrapper" style="display:none">
    <div class="stage-progress">
      <div 
        v-for="(stage, index) in stages" 
        :key="index" 
        class="stage-item"
        :class="{ 
          'is-active': index === activeStep,
          'is-finished': index < activeStep,
          'is-pending': index > activeStep
        }"
      >
        <div class="stage-icon">
          <i v-if="index < activeStep" class="el-icon-check"></i>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="stage-content">
          <div class="stage-title">{{ stage.title }}</div>
          <div class="stage-time">
            {{ formatDateRange(stage.startDate, stage.endDate) }}
          </div>
        </div>
        <div v-if="index < stages.length - 1" class="stage-arrow">
          <i class="el-icon-arrow-right"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { toProgressStageKey } from '@/utils/competitionStage'

const props = defineProps({
  currentStage: {
    type: String,
    default: 'REGISTRATION'
  },
  stages: {
    type: Array,
    default: () => [
      { key: 'REGISTRATION', title: '报名', startDate: '', endDate: '' },
      { key: 'BOOK', title: '书审', startDate: '', endDate: '' },
      { key: 'INTERVIEW', title: '面谈', startDate: '', endDate: '' },
      { key: 'FINAL', title: '决赛', startDate: '', endDate: '' }
    ]
  }
})

const activeStep = computed(() => {
  const key = toProgressStageKey(props.currentStage)
  const index = props.stages.findIndex(s => s.key === key)
  return index >= 0 ? index : 0
})

const formatDateRange = (start, end) => {
  if (!start || !end) return '未设置'
  
  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }
  
  return `${formatDate(start)} - ${formatDate(end)}`
}
</script>

<style scoped lang="scss">
.stage-progress-wrapper {
  margin-bottom: 20px;
  padding: 0 20px;
}

.stage-progress {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px 32px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  max-width: 1000px;
  margin: 0 auto;
  
  .stage-item {
    display: flex;
    align-items: center;
    flex: 1;
    position: relative;
    
    .stage-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      font-weight: 600;
      flex-shrink: 0;
      transition: all 0.3s ease;
      background: rgba(255, 255, 255, 0.2);
      color: rgba(255, 255, 255, 0.6);
      border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .stage-content {
      margin-left: 12px;
      flex: 1;
      
      .stage-title {
        font-size: 15px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 4px;
        transition: all 0.3s ease;
      }
      
      .stage-time {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.6);
        transition: all 0.3s ease;
      }
    }
    
    .stage-arrow {
      margin: 0 16px;
      font-size: 20px;
      color: rgba(255, 255, 255, 0.4);
      flex-shrink: 0;
    }
    
    // 已完成状态
    &.is-finished {
      .stage-icon {
        background: rgba(255, 255, 255, 0.95);
        color: #67c23a;
        border-color: rgba(255, 255, 255, 0.95);
        box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
      }
      
      .stage-content {
        .stage-title {
          color: rgba(255, 255, 255, 0.95);
        }
        
        .stage-time {
          color: rgba(255, 255, 255, 0.7);
        }
      }
    }
    
    // 当前激活状态
    &.is-active {
      .stage-icon {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        color: #8b4513;
        border-color: #ffd700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
        animation: pulse 2s infinite;
      }
      
      .stage-content {
        .stage-title {
          color: #fff;
          font-size: 16px;
        }
        
        .stage-time {
          color: rgba(255, 255, 255, 0.9);
        }
      }
    }
    
    // 待进行状态
    &.is-pending {
      opacity: 0.7;
    }
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(255, 215, 0, 0.8);
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .stage-progress {
    padding: 20px 24px;
    
    .stage-item {
      .stage-icon {
        width: 36px;
        height: 36px;
        font-size: 14px;
      }
      
      .stage-content {
        .stage-title {
          font-size: 14px;
        }
        
        .stage-time {
          font-size: 11px;
        }
      }
      
      .stage-arrow {
        margin: 0 12px;
        font-size: 18px;
      }
    }
  }
}

@media (max-width: 768px) {
  .stage-progress {
    flex-direction: column;
    padding: 20px;
    
    .stage-item {
      width: 100%;
      margin-bottom: 16px;
      
      .stage-arrow {
        display: none;
      }
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}
</style>
