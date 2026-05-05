<template>
  <div class="interview-only-ranking">
    <StageProgress :current-stage="currentStageKey" :stages="stagesList" />

    <!-- 操作区 -->
    <el-card class="action-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">纯面谈排名</span>
          <el-tag type="info" effect="plain">仅用面谈打分 · 系数调整 · 全组别</el-tag>
        </div>
      </template>

      <el-alert
        title="适用全部组别（基层/综合/进阶），仅使用面谈打分通过系数调整（An / B / Cn / D）排名，与合分路（INTERVIEW）完全隔离，无入围线配置。"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />

      <div class="action-row">
        <el-button type="primary" :loading="computing" @click="handleCompute">
          计算排名
        </el-button>
        <el-text v-if="snapshotTime" type="info" size="small" style="margin-left: 12px">
          最近快照：{{ snapshotTime }}
        </el-text>
        <el-text v-else type="warning" size="small" style="margin-left: 12px">
          暂无快照，请先「计算排名」
        </el-text>
      </div>
    </el-card>

    <!-- 筛选 -->
    <el-card class="filter-card" shadow="never">
      <el-form inline>
        <el-form-item label="组别">
          <el-select v-model="filterGroupType" clearable placeholder="全部组别" style="width: 130px" @change="applyFilter">
            <el-option label="基层组" value="BASIC" />
            <el-option label="综合组" value="COMPREHENSIVE" />
            <el-option label="进阶组" value="ADVANCED" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filterKeyword" clearable placeholder="项目名称" style="width: 180px" @clear="applyFilter" @keyup.enter="applyFilter" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="applyFilter">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 排名列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">纯面谈排名 · 调整分列表</span>
          <el-tag type="info">stage = INTERVIEW_ONLY</el-tag>
        </div>
      </template>

      <el-table
        :data="filteredRows"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <!-- 排名 -->
        <el-table-column width="60" align="center" label="排名">
          <template #default="{ row }">
            <el-tag
              v-if="row.irank && row.irank <= 3"
              :type="rankTagType(row.irank)"
              effect="dark"
              size="large"
            >
              🏅 {{ row.irank }}
            </el-tag>
            <span v-else-if="row.irank != null" style="font-weight: bold; font-size: 15px">{{ row.irank }}</span>
            <span v-else style="color: #909399">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="registrationId" label="项目编号" width="90" align="center" />
        <el-table-column prop="projectName" label="项目名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="institutionName" label="医疗机构" min-width="180" show-overflow-tooltip />

        <el-table-column prop="groupType" label="组别" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="groupTagType(row.groupType)" size="small">{{ groupLabel(row.groupType) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="groupCode" label="分组" width="80" align="center" />

        <!-- 原始均分 / 调整分 -->
        <el-table-column width="120" align="center">
          <template #header>
            <span>原始均分 / 调整分</span>
            <el-tooltip placement="top">
              <template #content>
                <div style="max-width: 260px; line-height: 1.5">
                  <div>原始均分 (avgTotal)：评委打分平均值。</div>
                  <div>调整分 (D)：原始均分 ÷ 系数 Cn，排名依据。</div>
                </div>
              </template>
              <el-icon style="margin-left: 4px; cursor: help"><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
          <template #default="{ row }">
            <div class="score-cell">
              <div class="score-row">
                <span class="score-label">均分</span>
                <span class="score-val" :style="{ color: scoreColor(row.avgTotal) }">
                  {{ fmt1(row.avgTotal) }}
                </span>
              </div>
              <div class="score-row">
                <span class="score-label">调整</span>
                <span class="score-val" :style="{ color: scoreColor(row.adjustedScore) }">
                  {{ fmt1(row.adjustedScore) }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 系数 / 均值 -->
        <el-table-column width="130" align="center">
          <template #header>
            <span>系数 / 均值</span>
            <el-tooltip placement="top">
              <template #content>
                <div style="max-width: 300px; line-height: 1.5">
                  <div>Cn = An ÷ B（小组系数）</div>
                  <div>An：小组均分（去极值）</div>
                  <div>B：全组别均分（去极值）</div>
                </div>
              </template>
              <el-icon style="margin-left: 4px; cursor: help"><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
          <template #default="{ row }">
            <div class="score-cell">
              <div class="score-row">
                <span class="score-label">Cn</span>
                <span class="score-val">{{ row.coefficient != null ? Number(row.coefficient).toFixed(4) : '-' }}</span>
              </div>
              <div class="score-row">
                <span class="score-label">An/B</span>
                <span class="score-val" style="font-size: 12px">{{ fmtAnB(row.groupAvg, row.overallAvg) }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="calculatedAt" label="快照时间" width="160" align="center">
          <template #default="{ row }">
            <span style="font-size: 12px; color: #909399">
              {{ row.calculatedAt ? new Date(row.calculatedAt).toLocaleString('zh-CN') : '-' }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && filteredRows.length === 0" style="padding: 20px 0">
        <el-empty description="暂无数据，请先「计算排名」" />
      </div>
      <div v-if="filteredRows.length > 0" style="padding: 8px 0; color: #909399; font-size: 13px">
        共 {{ filteredRows.length }} 条
      </div>
    </el-card>

    <!-- 算法说明 -->
    <el-collapse v-model="ruleOpen" style="margin-top: 12px">
      <el-collapse-item name="rule">
        <template #title>
          <span style="font-weight: 600">评分调整说明（An / B / Cn / D）</span>
        </template>
        <div style="padding: 8px 16px; line-height: 1.8; color: #606266">
          <ol>
            <li>评分以 <strong>80 分</strong>为基准。</li>
            <li>同组别内：小组均分 <strong>An</strong>，全组均分 <strong>B</strong>，系数 <strong>Cn = An ÷ B</strong>，调整分 <strong>D = 原始均分 ÷ Cn</strong>；按 D 排名。</li>
            <li><strong>去极值</strong>：计算 An、B 时去掉 65 分以下与 95 分以上。</li>
            <li>本路径与合分排名（书审 + 面谈）完全隔离，两路快照互不覆盖。</li>
          </ol>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import { getRankings, computeRanking } from '@/api/shortlist'
import { getCurrentCompetitionIdSync } from '@/utils/competition'

const competitionId = ref(getCurrentCompetitionIdSync())
const { stagesList, currentStageKey } = useCompetitionStages()

const loading = ref(false)
const computing = ref(false)
const rows = ref([])
const filterGroupType = ref('')
const filterKeyword = ref('')
const ruleOpen = ref([])

const snapshotTime = computed(() => {
  const times = rows.value.map(r => r.calculatedAt).filter(Boolean)
  if (!times.length) return ''
  const latest = times.sort().slice(-1)[0]
  try { return new Date(latest).toLocaleString('zh-CN') } catch { return latest }
})

const filteredRows = computed(() => {
  let list = rows.value
  if (filterGroupType.value) list = list.filter(r => r.groupType === filterGroupType.value)
  if (filterKeyword.value.trim()) {
    const kw = filterKeyword.value.trim().toLowerCase()
    list = list.filter(r => (r.projectName || '').toLowerCase().includes(kw))
  }
  return list
})

async function loadData() {
  if (!competitionId.value) { ElMessage.warning('请先选择赛事'); return }
  loading.value = true
  try {
    const params = { competitionId: competitionId.value, stage: 'INTERVIEW_ONLY' }
    if (filterGroupType.value) params.groupType = filterGroupType.value
    const res = await getRankings(params)
    if (res.success && Array.isArray(res.data)) {
      rows.value = res.data
    } else {
      rows.value = []
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function handleCompute() {
  if (!competitionId.value) { ElMessage.warning('请先选择赛事'); return }
  computing.value = true
  try {
    const res = await computeRanking({
      competitionId: competitionId.value,
      stage: 'INTERVIEW',
      interviewOnly: true
    })
    if (res.success) {
      ElMessage.success(
        typeof res.data === 'number' ? `计算完成，已写入 ${res.data} 条快照` : '计算完成'
      )
      await loadData()
    } else {
      ElMessage.error(res.message || '计算失败')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('计算排名失败')
  } finally {
    computing.value = false
  }
}

function applyFilter() { loadData() }
function resetFilter() {
  filterGroupType.value = ''
  filterKeyword.value = ''
  loadData()
}

function fmt1(v) { return v != null ? Number(v).toFixed(1) : '-' }
function fmtAnB(an, b) {
  return `${an != null ? Number(an).toFixed(1) : '-'} / ${b != null ? Number(b).toFixed(1) : '-'}`
}
function scoreColor(v) {
  if (v == null) return ''
  if (v >= 90) return '#67c23a'
  if (v >= 80) return '#409eff'
  if (v >= 70) return '#e6a23c'
  return '#f56c6c'
}
function rankTagType(rank) {
  if (rank === 1) return 'warning'
  if (rank === 2) return 'info'
  return 'success'
}
function groupLabel(gt) {
  return { BASIC: '基层组', COMPREHENSIVE: '综合组', ADVANCED: '进阶组' }[gt] || gt
}
function groupTagType(gt) {
  return { BASIC: '', COMPREHENSIVE: 'success', ADVANCED: 'warning' }[gt] || ''
}

onMounted(loadData)
</script>

<style scoped>
.interview-only-ranking { display: flex; flex-direction: column; gap: 12px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 15px; font-weight: 600; }
.action-row { display: flex; align-items: center; }
.filter-card { padding: 0; }
.filter-card :deep(.el-card__body) { padding: 12px 16px; }
.score-cell { display: flex; flex-direction: column; gap: 4px; }
.score-row { display: flex; justify-content: space-between; align-items: center; gap: 6px; font-size: 13px; }
.score-label { color: #909399; font-size: 11px; white-space: nowrap; }
.score-val { font-weight: 600; }
</style>
