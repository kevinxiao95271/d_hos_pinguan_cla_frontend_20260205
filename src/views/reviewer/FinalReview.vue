<template>
  <div class="final-review-page">

    <!-- 顶部信息栏 -->
    <div class="page-header">
      <el-button :icon="ArrowLeft" plain @click="goBack">返回</el-button>
      <div class="project-info">
        <h2 class="project-title">{{ projectName }}</h2>
        <div class="meta-tags">
          <el-tag type="info" size="small">{{ institutionName }}</el-tag>
          <el-tag type="info" size="small" v-if="sessionCode">{{ sessionCode }}</el-tag>
          <el-tag :type="scoreFormTagType" size="small">{{ scoreFormText }}</el-tag>
          <el-tag v-if="isViewMode" type="success" size="small">查看模式</el-tag>
          <el-tag v-if="isScored" type="success" size="small">已提交</el-tag>
        </div>
      </div>
    </div>

    <el-card class="score-card">
      <!-- 总分输入区 -->
      <div class="total-score-block">
        <div class="total-score-row">
          <span class="total-score-label">评分</span>
          <el-input-number
            v-model="form.total"
            :min="0"
            :max="100"
            :step="0.5"
            :precision="1"
            :disabled="isViewMode"
            size="large"
            style="width: 160px"
          />
          <span class="total-score-unit">/ 100 分</span>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div v-if="!isViewMode" class="action-bar">
        <el-button @click="goBack">取消</el-button>
        <el-button type="warning" plain :loading="recusing" @click="openRecuseDialog">申请规避</el-button>
        <el-button :loading="saving" @click="handleSaveDraft">暂存草稿</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">提交评分</el-button>
      </div>
      <div v-else class="action-bar">
        <el-button @click="goBack">返回任务列表</el-button>
      </div>

      <el-divider content-position="left" style="margin-top: 24px">评分标准（供参考）</el-divider>

      <!-- QCC 评分表 -->
      <template v-if="scoreForm === 'QCC'">
        <div class="criteria-card">
          <div class="criteria-title">1. 计划 <span class="criteria-max">满分 10 分</span></div>
          <ol class="criteria-list">
            <li>主题选取有内涵、具有创新性与应用性，且有推广价值</li>
            <li>目标设定科学合理性</li>
            <li>QC STORY判定准确</li>
            <li>团队持续维持改善或创新行动所达成的目标</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">2. 项目结构与对策措施探讨 <span class="criteria-max">满分 15 分</span></div>
          <ol class="criteria-list">
            <li>项目分析全面，探讨并求证问题形成影响因素的过程结构完善，符合逻辑</li>
            <li>以数据或实例来呈现事实现状</li>
            <li>科学引用相关文献，实行创新技术</li>
            <li>问题或攻坚点分析与对策方案间的关联性、逻辑性等，并考虑长、短期的效果发展对策</li>
            <li>对策行动计划拟订具有时间、人力及费用等资源合理安排的考量</li>
            <li>合理应用品管工具</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">3. 对策行动过程 <span class="criteria-max">满分 15 分</span></div>
          <ol class="criteria-list">
            <li>对策（最适策）的可行性与创新性</li>
            <li>对策行动过程中，考虑对策效果、目标达成状态及相关变化因素，客观分析，动态调整对策行动</li>
            <li>改善对策（最适策）评价方法科学合理且符合专业水平</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">4. 成果表现 <span class="criteria-max">满分 20 分</span></div>
          <ol class="criteria-list">
            <li>对策效果确认和目标的达成程度及影响程度（如目标达标率、患者满意度、质量安全指标的正向提升等）</li>
            <li>对于临床及质量改善的效益；无形效益（机构形象、质量安全、员工士气等的提升）</li>
            <li>机构具体实施制度化的情况（如制度建立、标准文件化的管理）</li>
            <li>制度与标准于行动过程中的改变情形及新版制度与标准的实施程度</li>
            <li>附加成果如发明、专利等，酌情加分（2分）</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">5. 查验 <span class="criteria-max">满分 5 分</span></div>
          <ol class="criteria-list">
            <li>本期活动的检查（含效果维持及余留问题的改善）</li>
            <li>未来的主要改善目标与行动</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">6. 整体运作 <span class="criteria-max">满分 15 分</span></div>
          <ol class="criteria-list">
            <li>团队积极投入的情形（促使全员参与的行动方案）</li>
            <li>行业内的推广交流</li>
            <li>整体运作与团队精神</li>
            <li>改善过程特色，创造力的发挥程度</li>
            <li>本活动的组成、运作与成员对于活动的参与程度及团队领导人的积极性及其对问题、目标结构及对策措施的了解程度</li>
            <li>对策措施的落实情形</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">7. 现场表现 <span class="criteria-max">满分 20 分</span></div>
          <ol class="criteria-list">
            <li>报告内容逻辑性（系统分明、前后连贯），文字流畅性</li>
            <li>图表文字清晰简明</li>
            <li>活动说明易于了解</li>
            <li>发表人的仪态与语言表达能力</li>
          </ol>
        </div>
      </template>

      <!-- NON_QCC 评分表 -->
      <template v-else-if="scoreForm === 'NON_QCC'">
        <div class="criteria-card">
          <div class="criteria-title">1. 选题 <span class="criteria-max">满分 15 分</span></div>
          <ol class="criteria-list">
            <li>符合工作实际改善要求，主题定义清晰</li>
            <li>选题依据客观科学，有必要的指南或文献支持</li>
            <li>改进目标具有合理性，有可行性分析</li>
            <li>现状分析清楚，符合逻辑，数据收集充分，选择管理工具运用得当</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">2. 原因分析 <span class="criteria-max">满分 10 分</span></div>
          <ol class="criteria-list">
            <li>对存在问题有客观、真实的分析</li>
            <li>组织人员讨论，能集思广益</li>
            <li>运用科学工具找到正确的主要原因</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">3. 计划 <span class="criteria-max">满分 10 分</span></div>
          <ol class="criteria-list">
            <li>针对问题产生的主要原因，制定改进对策计划</li>
            <li>对策方案拟定5W1H要素明确，具有可操作性，必要时实施之前做风险评估</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">4. 实施 <span class="criteria-max">满分 20 分</span></div>
          <ol class="criteria-list">
            <li>按计划进行PDCA实施</li>
            <li>对策实施结果可衡量，可判断其有效性</li>
            <li>各对策间符合逻辑关系，效果判定样本量适宜</li>
            <li>对策实施有创新性、长期性和稳定性</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">5. 成果表现 <span class="criteria-max">满分 10 分</span></div>
          <ol class="criteria-list">
            <li>对策效果确认和目标的达成程度及影响程度（如目标达成率、顾客满意度、临床质量改善效益等）</li>
            <li>无形效益（医院形象、质量信誉、士气氛围、社会责任及安全卫生的提升）</li>
            <li>在行动过程中，制度与标准的改变情形及新版制度与标准的落实程度</li>
            <li>附加成果如论文、课题、发明专利等，酌情加分（2分）</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">6. 检讨 <span class="criteria-max">满分 10 分</span></div>
          <ol class="criteria-list">
            <li>本期活动的检讨（含效果维持及余留问题的改善）</li>
            <li>未来重要目标与行动</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">7. 整体运作 <span class="criteria-max">满分 15 分</span></div>
          <ol class="criteria-list">
            <li>团队积极投入的情形（促使全员参与的行动方案）</li>
            <li>行业内的推广交流</li>
            <li>整体运作与团队精神</li>
            <li>品管手法新颖、理念创新，酌情加分（2分）</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">8. 现场表现 <span class="criteria-max">满分 10 分</span></div>
          <ol class="criteria-list">
            <li>报告内容逻辑性（系统分明、前后连贯），文字流畅性</li>
            <li>图表文字清晰简明</li>
            <li>活动说明易于了解</li>
            <li>发表人的仪态与语言表达能力</li>
          </ol>
        </div>
      </template>

      <!-- QFD 评分表 -->
      <template v-else-if="scoreForm === 'QFD'">
        <div class="criteria-card">
          <div class="criteria-title">1. 圈活动特征 <span class="criteria-max">满分 15 分</span></div>
          <ol class="criteria-list">
            <li>选题具有创新性、科学性与应用性</li>
            <li>选题具有推广价值</li>
            <li>QC STORY 判定准确</li>
            <li>中外文献全面、深刻</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">2. 课题明确化与项目计划性 <span class="criteria-max">满分 25 分</span></div>
          <ol class="criteria-list">
            <li>提出的课题明确化结构完整、层次分明、符合逻辑</li>
            <li>课题具有高度与深度，创新性较强</li>
            <li>活动计划进度设计合理</li>
            <li>项目掌握分析全面、完整，望差值设定合理</li>
            <li>魅力质量创新点识别准确</li>
            <li>攻坚点发掘评价项目科学合理</li>
            <li>目标值设定合理</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">3. 方策拟定与最适方策探究 <span class="criteria-max">满分 25 分</span></div>
          <ol class="criteria-list">
            <li>方策拟定方法准确</li>
            <li>拟定方策具体可行</li>
            <li>方策评价方法科学合理</li>
            <li>最适方策探究方法准确</li>
            <li>多维质量工具应用（可选）</li>
            <li>图表应用规范</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">4. 执行力及活动成果 <span class="criteria-max">满分 25 分</span></div>
          <ol class="criteria-list">
            <li>方策实施明确、规范有效</li>
            <li>效果确认真实规范</li>
            <li>质量安全风险控制有效</li>
            <li>目标达成率科学合理</li>
            <li>有形成果真实有效，无形成果规范客观</li>
            <li>标准化规范有效</li>
            <li>检讨与改进真实有效</li>
          </ol>
        </div>
        <div class="criteria-card">
          <div class="criteria-title">5. 现场发表 <span class="criteria-max">满分 10 分</span></div>
          <ol class="criteria-list">
            <li>热忱洋溢、明快有力、语言流畅、清晰</li>
            <li>前后连贯、条理清晰、逻辑性较强</li>
            <li>PPT 制作水平较高，具有人文、艺术内涵及创意性</li>
          </ol>
        </div>
      </template>
    </el-card>

    <!-- 规避弹窗 -->
    <el-dialog v-model="recuseDialogVisible" title="申请规避评审任务" width="440px" :close-on-click-modal="false">
      <el-form ref="recuseFormRef" :model="recuseFormData" :rules="recuseRules" label-width="90px">
        <el-form-item label="规避原因" prop="reasonCode">
          <el-select v-model="recuseFormData.reasonCode" placeholder="请选择规避原因" style="width:100%">
            <el-option
              v-for="opt in recuseReasons"
              :key="opt.code"
              :label="opt.label"
              :value="opt.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          v-if="recuseFormData.reasonCode === 'OTHER'"
          label="补充说明"
          prop="reasonOther"
        >
          <el-input
            v-model="recuseFormData.reasonOther"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="请说明规避原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="recuseDialogVisible = false">取消</el-button>
        <el-button type="warning" :loading="recusing" @click="confirmRecuse">确认规避</el-button>
      </template>
    </el-dialog>

    <!-- 提交成功感谢弹窗 -->
    <el-dialog
      v-model="showThankYou"
      :show-close="false"
      :close-on-click-modal="false"
      width="380px"
      align-center
    >
      <div class="thank-you">
        <div class="ty-icon">✅</div>
        <h2>评分已提交</h2>
        <p>感谢您认真完成本次决赛评审！</p>
      </div>
      <template #footer>
        <el-button type="primary" style="width: 100%" size="large" @click="goBack">返回任务列表</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { saveFinalScoreDraft, submitFinalScore, recuseFinalScore } from '@/api/review'
import { getRecuseReasons } from '@/api/dictionary'

const route = useRoute()
const router = useRouter()

// ── 路由参数 ────────────────────────────────────────────────
const taskId    = computed(() => route.params.taskId)
const projectName    = computed(() => route.query.projectName || '未知项目')
const institutionName = computed(() => route.query.institutionName || '')
const sessionCode    = computed(() => route.query.sessionCode || '')
const scoreForm      = computed(() => (route.query.scoreForm || 'QCC').toUpperCase())
const isViewMode     = computed(() => route.query.view === 'score' || route.query.status === 'SCORED')
const isScored       = computed(() => route.query.status === 'SCORED')

const scoreFormText = computed(() => {
  const map = { QCC: 'QCC 问题解决型', NON_QCC: '非 QCC 课题达成型', QFD: 'QFD 质量功能展开' }
  return map[scoreForm.value] || scoreForm.value
})

const scoreFormTagType = computed(() => {
  if (scoreForm.value === 'QCC') return 'primary'
  if (scoreForm.value === 'QFD') return 'warning'
  return 'success'
})

// ── 表单 ────────────────────────────────────────────────────
const form = ref({ total: 80 })
const saving    = ref(false)
const submitting = ref(false)
const showThankYou = ref(false)

// 从路由 draftScore 恢复
const loadDraftFromRoute = () => {
  const draft = route.query.draftScore
  if (!draft) return
  try {
    const d = typeof draft === 'string' ? JSON.parse(draft) : draft
    if (d.total != null) form.value.total = d.total
  } catch { /* ignore */ }
}

// ── 构建提交载荷（后端仍需 scoreForm 字段） ────────────────
const buildPayload = () => ({
  scoreForm: scoreForm.value,
  total: form.value.total
})

// ── 暂存草稿 ────────────────────────────────────────────────
const handleSaveDraft = async () => {
  saving.value = true
  try {
    const res = await saveFinalScoreDraft(taskId.value, buildPayload())
    if (res.success) ElMessage.success('草稿已保存')
    else ElMessage.error(res.message || '保存失败')
  } catch {
    ElMessage.error('保存失败，请检查网络')
  } finally {
    saving.value = false
  }
}

// ── 提交评分 ────────────────────────────────────────────────
const handleSubmit = async () => {
  try {
    await ElMessageBox.confirm(
      `当前评分 ${form.value.total} 分，提交后不可修改，确认提交？`,
      '提交决赛评分',
      { confirmButtonText: '确认提交', cancelButtonText: '取消', type: 'warning' }
    )
    submitting.value = true
    const res = await submitFinalScore(taskId.value, buildPayload())
    if (res.success) showThankYou.value = true
    else ElMessage.error(res.message || '提交失败')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

// ── 规避 ────────────────────────────────────────────────────
const recuseDialogVisible = ref(false)
const recusing   = ref(false)
const recuseFormRef  = ref(null)
const recuseReasons  = ref([])
const recuseFormData = ref({ reasonCode: '', reasonOther: '' })
const recuseRules = {
  reasonCode: [{ required: true, message: '请选择规避原因', trigger: 'change' }],
  reasonOther: [{ required: true, message: '请填写补充说明', trigger: 'blur' }]
}

const loadRecuseReasons = async () => {
  try {
    const res = await getRecuseReasons()
    recuseReasons.value = res.success ? (res.data || []) : []
  } catch {
    recuseReasons.value = []
  }
}

const openRecuseDialog = () => {
  recuseFormData.value = { reasonCode: '', reasonOther: '' }
  recuseDialogVisible.value = true
  if (!recuseReasons.value.length) loadRecuseReasons()
}

const confirmRecuse = async () => {
  try { await recuseFormRef.value.validate() } catch { return }
  recusing.value = true
  try {
    const payload = { reasonCode: recuseFormData.value.reasonCode }
    if (recuseFormData.value.reasonCode === 'OTHER') payload.reasonOther = recuseFormData.value.reasonOther
    const res = await recuseFinalScore(taskId.value, payload)
    if (res.success) {
      ElMessage.success('规避申请已提交')
      recuseDialogVisible.value = false
      goBack()
    } else {
      ElMessage.error(res.message || '规避失败')
    }
  } catch {
    ElMessage.error('规避失败，请检查网络')
  } finally {
    recusing.value = false
  }
}

const goBack = () => router.push('/reviewer/dashboard')

onMounted(() => { loadDraftFromRoute() })
</script>

<style scoped lang="scss">
.final-review-page {
  padding: 20px;
  max-width: 860px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;

  .project-info {
    flex: 1;
    .project-title {
      font-size: 18px;
      font-weight: 700;
      color: #303133;
      margin: 0 0 8px;
    }
    .meta-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
  }
}

.score-card {
  margin-bottom: 20px;
}

/* 总分输入区（仿面谈样式） */
.total-score-block {
  padding: 20px 24px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 8px;

  .total-score-row {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .total-score-label {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    white-space: nowrap;
  }

  .total-score-unit {
    font-size: 15px;
    color: #606266;
  }
}

/* 操作栏 */
.action-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0 4px;
}

/* 评分标准卡片 */
.criteria-card {
  padding: 14px 18px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 10px;
  background: #fff;

  .criteria-title {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;

    .criteria-max {
      font-size: 12px;
      font-weight: 400;
      color: #909399;
      margin-left: 6px;
    }
  }

  .criteria-list {
    margin: 0;
    padding-left: 20px;
    li {
      font-size: 13px;
      color: #606266;
      line-height: 1.8;
    }
  }
}

.thank-you {
  text-align: center;
  padding: 20px 10px 10px;
  .ty-icon { font-size: 48px; margin-bottom: 12px; }
  h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 10px; }
  p  { font-size: 14px; color: #606266; line-height: 1.8; margin: 0; }
}

@media (max-width: 768px) {
  .final-review-page { padding: 12px; }
  .action-bar { flex-wrap: wrap; .el-button { flex: 1; } }
}
</style>
