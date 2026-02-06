<template>
  <div class="ranking-page">
    <stage-progress current-stage="FINAL" :stages="stagesList" />
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>最终排名</span>
        </div>
      </template>
      
      <el-empty description="最终排名功能开发中" />
    </el-card>
  </div>
</template>

<script setup>
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'

const { stagesList } = useCompetitionStages()
</script>
