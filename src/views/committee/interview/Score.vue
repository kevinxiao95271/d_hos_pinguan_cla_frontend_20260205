<template>
  <div class="score-page">
    <stage-progress current-stage="INTERVIEW" :stages="stagesList" />
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>面谈得分</span>
        </div>
      </template>
      
      <el-empty description="面谈得分功能开发中" />
    </el-card>
  </div>
</template>

<script setup>
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'

const { stagesList } = useCompetitionStages()
</script>
