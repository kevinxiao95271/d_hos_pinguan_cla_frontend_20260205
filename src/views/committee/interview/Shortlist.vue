<template>
  <div class="shortlist-page">
    <stage-progress current-stage="INTERVIEW" :stages="stagesList" />
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>入围管理</span>
        </div>
      </template>
      
      <el-empty description="入围管理功能开发中" />
    </el-card>
  </div>
</template>

<script setup>
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'

const { stagesList } = useCompetitionStages()
</script>
