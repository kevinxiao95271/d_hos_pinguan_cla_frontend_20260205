<template>
  <div class="group-page">
    <stage-progress current-stage="FINAL" :stages="stagesList" />
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>决赛分组</span>
        </div>
      </template>
      
      <el-empty description="决赛分组功能开发中" />
    </el-card>
  </div>
</template>

<script setup>
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'

const { stagesList } = useCompetitionStages()
</script>
