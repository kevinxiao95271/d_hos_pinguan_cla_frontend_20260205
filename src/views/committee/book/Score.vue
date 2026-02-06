<template>
  <div class="score-page">
    <stage-progress current-stage="BOOK" :stages="stagesList" />
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>书审得分</span>
        </div>
      </template>
      
      <el-empty description="书审得分功能开发中" />
    </el-card>
  </div>
</template>

<script setup>
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'

const { stagesList } = useCompetitionStages()
</script>
