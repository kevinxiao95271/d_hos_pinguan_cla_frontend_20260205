<template>
  <div class="review-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isViewMode ? '查看评分' : taskInfo.projectName || '' }}</span>
        </div>
      </template>
      
      <div v-loading="loading">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          :label-width="isMobile ? '0px' : '200px'"
          :label-position="isMobile ? 'top' : 'right'"
          :disabled="isViewMode"
        >
          <!-- 项目信息（可折叠，默认展开） -->
          <el-collapse v-model="activeProjectInfo" class="project-info-collapse" style="margin-bottom: 16px;">
            <el-collapse-item title="项目信息" name="projectInfo">
              <el-form-item label="项目编号">
                <span>{{ registrationId || route.query.registrationId || '-' }}</span>
              </el-form-item>
              <el-form-item label="项目名称">
                <span>{{ taskInfo.projectName || route.query.projectName || '-' }}</span>
              </el-form-item>
              <el-form-item label="医疗机构">
                <span>{{ taskInfo.institutionName || '-' }}</span>
              </el-form-item>
              <el-form-item label="机构等级">
                <el-tag v-if="taskInfo.institutionLevel" type="success">{{ taskInfo.institutionLevel }}</el-tag>
                <span v-else>-</span>
              </el-form-item>
              <el-form-item label="竞赛组别">
                <span>{{ getGroupTypeText(taskInfo.groupType) }}</span>
              </el-form-item>
            </el-collapse-item>
          </el-collapse>
          

          <!-- 材料文件（书审阶段显示，面谈阶段隐藏） -->
          <div v-if="taskInfo.stage !== 'INTERVIEW'" class="materials-section">
            <div class="materials-title">
              项目材料{{ projectDetail && projectDetail.materials && projectDetail.materials.length > 0 ? `（${projectDetail.materials.length}个）` : '' }}
            </div>
            <template v-if="projectDetail && projectDetail.materials && projectDetail.materials.length > 0">
              <el-table :data="projectDetail.materials" border size="small">
                <el-table-column label="类型" width="160">
                  <template #default="{ row }">{{ getMaterialTypeLabel(row.type) }}</template>
                </el-table-column>
                <el-table-column prop="fileName" label="文件名" />
                <el-table-column prop="uploadedAt" label="上传时间" width="160">
                  <template #default="{ row }">
                    {{ row.uploadedAt ? row.uploadedAt.replace('T',' ').substring(0,16) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="180">
                  <template #default="{ row }">
                    <el-button v-if="canPreview(row.fileName)" type="success" size="small" @click="previewFile(row)">预览</el-button>
                    <el-button v-else type="primary" size="small" @click="downloadFile(row)">下载</el-button>
                    <el-button v-if="row.type === 'REPORT'" type="primary" size="small" @click="downloadFile(row)">下载</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </template>
            <div v-else class="materials-empty">暂无上传附件</div>
          </div>
          
          <el-divider content-position="left">评分</el-divider>

          <!-- 书审评分 -->
          <template v-if="taskInfo.stage !== 'INTERVIEW'">
            <div class="scoring-header">
              <span>项目评分（100 分）</span>
              <el-button size="small" type="primary" plain :icon="Document" :disabled="false" @click="openScoringStandard('book')">查看评分标准文件</el-button>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">计划 <span class="criteria-max">满分 10 分 / 起评 8 分</span></div>
                <ol class="criteria-list">
                  <li>主题选取适当性、重要性、特殊性的具体明确程度</li>
                  <li>目标设定的理由及适当性</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.planScore" :min="0" :max="10" :step="0.5" :marks="marks10" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.planScore }}</span><span class="score-denom">/ 10</span></div>
              </div>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">问题结构与对策措施探讨 <span class="criteria-max">满分 20 分 / 起评 16 分</span></div>
                <ol class="criteria-list">
                  <li>问题分析、探讨并求证问题形成或影响目标达成之结构</li>
                  <li>引用或采用相关文献与技术</li>
                  <li>以相关数据或实例搜集资料来呈现事实</li>
                  <li>问题分析结果与对策方案间的连贯性或逻辑性，及考量长、短期的效果发展对策</li>
                  <li>对策行动计划的拟订考量时间、人力及费用等资源安排</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.problemAnalysisScore" :min="0" :max="20" :step="0.5" :marks="marks20" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.problemAnalysisScore }}</span><span class="score-denom">/ 20</span></div>
              </div>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">对策实施 <span class="criteria-max">满分 20 分 / 起评 16 分</span></div>
                <ol class="criteria-list">
                  <li>对策行动过程中，考量对策效果、目标达成状态及问题、目标结构的变化等因素，持续进行对策行动（含目标）的调整</li>
                  <li>对策（最适策）的可行性与创意性</li>
                  <li>改善对策（最适策）的实用性、适用性及有效性</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.implementationScore" :min="0" :max="20" :step="0.5" :marks="marks20" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.implementationScore }}</span><span class="score-denom">/ 20</span></div>
              </div>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">成果表现 <span class="criteria-max">满分 15 分 / 起评 12 分</span></div>
                <ol class="criteria-list">
                  <li>对策效果确认和目标的达成程度（如目标达成率、顾客满意度、营业收益、生产力的提升等）及影响程度</li>
                  <li>对于临床及质量改善的效益</li>
                  <li>无形效益（医院形象、质量信誉、士气、环境、劳资关系、社会责任及安全卫生的提升）</li>
                  <li>在行动过程中，制度与标准的改变情形及新版制度与标准的落实程度</li>
                  <li>附加成果如发明、专利等，酌情加分（2 分）</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.resultScore" :min="0" :max="15" :step="0.5" :marks="marks15" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.resultScore }}</span><span class="score-denom">/ 15</span></div>
              </div>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">检讨 <span class="criteria-max">满分 10 分 / 起评 8 分</span></div>
                <ol class="criteria-list">
                  <li>本期活动的检讨（含余留问题的改善）</li>
                  <li>未来重要目标与行动</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.reviewScore" :min="0" :max="10" :step="0.5" :marks="marks10" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.reviewScore }}</span><span class="score-denom">/ 10</span></div>
              </div>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">整体运作 <span class="criteria-max">满分 10 分 / 起评 8 分</span></div>
                <ol class="criteria-list">
                  <li>团队积极投入的情形（促使全员参与的行动方法）</li>
                  <li>机构内的推广交流</li>
                  <li>整体运作与团队精神</li>
                  <li>品管手法新颖、理念创新，酌情加分（2 分）</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.operationScore" :min="0" :max="10" :step="0.5" :marks="marks10" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.operationScore }}</span><span class="score-denom">/ 10</span></div>
              </div>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">资料呈现 <span class="criteria-max">满分 15 分 / 起评 12 分</span></div>
                <ol class="criteria-list">
                  <li>整体周延性</li>
                  <li>文字流畅性</li>
                  <li>内容逻辑性（系统分明、前后连贯程度）</li>
                  <li>图表文字清晰简洁</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.presentationScore" :min="0" :max="15" :step="0.5" :marks="marks15" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.presentationScore }}</span><span class="score-denom">/ 15</span></div>
              </div>
            </div>
          </template>

          <!-- 面谈评分 -->
          <template v-else>
            <div class="scoring-header">
              <span>项目评分（100 分）</span>
              <el-button size="small" type="warning" plain :icon="Document" :disabled="false" @click="openScoringStandard('interview')">查看评分标准文件</el-button>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">选题 <span class="criteria-max">满分 10 分</span></div>
                <ol class="criteria-list">
                  <li>迫切性、实用性、可行性</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.topicScore" :min="0" :max="10" :step="0.5" :marks="marks10" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.topicScore }}</span><span class="score-denom">/ 10</span></div>
              </div>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">改善过程的确实性 <span class="criteria-max">满分 40 分</span></div>
                <ol class="criteria-list">
                  <li>书面资料与面谈结果的一致性</li>
                  <li>改善过程中各阶段原始数据及会议记录等相关资料的确实性</li>
                  <li>团队成员对问题解析、对策实施及目标达成的了解程度</li>
                  <li>项目所用改善工具的适用性、运用的正确及熟练程度</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.processScore" :min="0" :max="40" :step="0.5" :marks="marks40" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.processScore }}</span><span class="score-denom">/ 40</span></div>
              </div>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">整体运作 <span class="criteria-max">满分 20 分</span></div>
                <ol class="criteria-list">
                  <li>团队成员对团队运作模式的了解程度</li>
                  <li>团队组成及成员参与的积极性</li>
                  <li>项目的创新性及团队成员的创造力</li>
                  <li>团队成员的培训教育成长</li>
                  <li>该团队改善活动的经历与经验</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.interviewOperationScore" :min="0" :max="20" :step="0.5" :marks="marks20" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.interviewOperationScore }}</span><span class="score-denom">/ 20</span></div>
              </div>
            </div>

            <div class="score-item-card">
              <div class="score-item-criteria">
                <div class="criteria-title">改善成果 <span class="criteria-max">满分 30 分</span></div>
                <ol class="criteria-list">
                  <li>改善成效的确实性</li>
                  <li>效果维持及标准化落实情况</li>
                  <li>项目成果对医院或患者的贡献（有形及无形效益）</li>
                </ol>
              </div>
              <div class="score-item-right">
                <el-slider v-model="form.resultScore" :min="0" :max="30" :step="0.5" :marks="marks30" :disabled="isViewMode" :format-tooltip="v => v + ' 分'" class="score-slider" />
                <div class="score-display"><span class="score-num">{{ form.resultScore }}</span><span class="score-denom">/ 30</span></div>
              </div>
            </div>
          </template>

          <!-- 总分 / 亮点 / 不足 — 靠左对齐 -->
          <div class="bottom-section">
            <div class="bottom-item total-score-row">
              <span class="bottom-label">总分</span>
              <span class="total-score-value">{{ totalScore.toFixed(1) }}</span>
              <span class="total-score-unit">/ 100 分</span>
            </div>

            <template v-if="!isInterviewStage">
            <div class="bottom-item">
              <div class="bottom-label">亮点</div>
              <el-form-item prop="highlights" label-width="0" style="margin-bottom:0">
                <el-input
                  v-model="form.highlights"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入亮点（选填，不超过1000字）"
                  maxlength="1000"
                  show-word-limit
                  :disabled="isViewMode"
                />
              </el-form-item>
            </div>

            <div class="bottom-item">
              <div class="bottom-label required-label">不足 <span class="required-star">*</span></div>
              <el-form-item prop="shortcomings" label-width="0" style="margin-bottom:0">
                <el-input
                  v-model="form.shortcomings"
                  type="textarea"
                  :rows="5"
                  placeholder="必填，请至少例举三条不足之处，至少60字，不超过1000字"
                  maxlength="1000"
                  show-word-limit
                  :disabled="isViewMode"
                />
              </el-form-item>
              <div v-if="!isViewMode && form.shortcomings && form.shortcomings.length < 60" style="color:#f56c6c; font-size:12px; margin-top:4px">
                还需补充 {{ 60 - form.shortcomings.length }} 字
              </div>
            </div>
            </template>
          </div>

          <el-form-item v-if="!isViewMode">
            <el-button type="primary" plain :loading="draftSaving" @click="saveDraft">
              保存
            </el-button>
            <span style="display:inline-block; min-width:150px; margin-left:10px; vertical-align:middle;">
              <transition name="el-fade-in">
                <el-tag v-if="draftSavedAt" type="success">
                  草稿已保存 {{ draftSavedAt }}
                </el-tag>
              </transition>
            </span>
            <el-button
              v-if="canRecuse"
              type="warning"
              plain
              style="margin-left: 10px"
              @click="openRecuseDialog"
            >
              申请规避
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 返回按钮移到表单外，避免被表单的 disabled 影响 -->
        <div style="margin-top: 20px; text-align: left; padding-left: 200px;">
          <el-button @click="goBack">返回任务列表</el-button>
        </div>
        </div>
    </el-card>

    <!-- 文件预览 -->
    <FilePreviewDialog
      v-model="filePreviewVisible"
      :material-id="previewMaterialId"
      :file-url="previewFileUrl"
      :file-name="previewFileName"
      :show-download="false"
    />

    <!-- 规避弹窗 -->
    <el-dialog v-model="recuseDialogVisible" title="申请规避评审任务" width="440px" :close-on-click-modal="false">
      <div style="margin-bottom:12px; color:#606266">
        项目：<strong>{{ taskInfo.projectName }}</strong>
      </div>
      <el-form ref="recuseFormRef" :model="recuseForm" :rules="recuseRules" label-width="90px">
        <el-form-item label="规避原因" prop="reasonCode">
          <el-select v-model="recuseForm.reasonCode" placeholder="请选择规避原因" style="width:100%">
            <el-option
              v-for="item in recuseReasons"
              :key="item.code"
              :label="item.label || item.name || item.code"
              :value="item.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="recuseForm.reasonCode === 'OTHER'" label="补充说明" prop="reasonOther">
          <el-input
            v-model="recuseForm.reasonOther"
            type="textarea"
            :rows="3"
            placeholder="请填写具体原因"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="recuseDialogVisible = false">取消</el-button>
        <el-button type="warning" :loading="recusing" @click="confirmRecuse">确认规避</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { getReviewScore, getInterviewScore, saveBookReviewDraft, saveInterviewDraft } from '@/api/review'
import { recuseReviewTask } from '@/api/review'
import { getRecuseReasons } from '@/api/dictionary'
import { getRegistrationDetail } from '@/api/registration'
import { downloadMaterial } from '@/api/material'
import FilePreviewDialog from '@/components/FilePreviewDialog.vue'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const isMobile = ref(window.innerWidth <= 768)
const onResize = () => { isMobile.value = window.innerWidth <= 768 }
window.addEventListener('resize', onResize)

const taskId = computed(() => route.params.taskId)
const registrationId = computed(() => route.query.registrationId)
const taskStatus = computed(() => route.query.status || '')
// RETURNED 状态允许重新编辑，不算只读
const isViewMode = computed(() => route.query.view === 'score' || route.query.isViewMode === 'true')
// PENDING / CONFIRMED / DRAFT / RETURNED 均可申请规避（SCORED、RECUSED 不可）
const canRecuse = computed(() => !isViewMode.value && ['PENDING', 'CONFIRMED', 'DRAFT', 'RETURNED'].includes(taskStatus.value))
const formRef = ref(null)
const loading = ref(false)

const taskInfo = reactive({
  projectName: '',
  institutionName: '',
  institutionLevel: '',
  stage: '',
  groupType: ''
})

const projectDetail = ref(null)
const activeCollapse = ref([]) // 活动说明/项目摘要 默认全部折叠
const activeProjectInfo = ref(['projectInfo']) // 项目信息默认展开

const BOOK_MAX = { planScore: 10, problemAnalysisScore: 20, implementationScore: 20, resultScore: 15, reviewScore: 10, operationScore: 10, presentationScore: 15 }
const INTERVIEW_MAX = { topicScore: 10, processScore: 40, interviewOperationScore: 20, resultScore: 30 }

// 每5分一个刻度
const makeMarks = (max) => {
  const m = {}
  for (let i = 0; i <= max; i += 5) {
    m[i] = String(i)
  }
  return m
}
const marks10 = makeMarks(10)
const marks15 = makeMarks(15)
const marks20 = makeMarks(20)
const marks30 = makeMarks(30)
const marks40 = makeMarks(40)

const form = reactive({
  // 书审字段（默认满分）
  planScore: 10,
  problemAnalysisScore: 20,
  implementationScore: 20,
  resultScore: 15,
  reviewScore: 10,
  operationScore: 10,
  presentationScore: 15,
  // 面谈字段（默认满分）
  topicScore: 10,
  processScore: 40,
  interviewOperationScore: 20,
  // 公共字段
  highlights: '',
  shortcomings: ''
})

const isInterviewStage = computed(() => taskInfo.stage === 'INTERVIEW')

const totalScore = computed(() => {
  if (isInterviewStage.value) {
    return form.topicScore + form.processScore + form.interviewOperationScore + form.resultScore
  }
  return form.planScore +
         form.problemAnalysisScore +
         form.implementationScore +
         form.resultScore +
         form.reviewScore +
         form.operationScore +
         form.presentationScore
})

// 草稿保存状态
const draftSaving = ref(false)
const draftSavedAt = ref('')
let draftTimer = null

const rules = {
  // 书审分值规则
  planScore: [{ type: 'number', min: 0, max: 10, message: '计划得分范围为0-10分', trigger: 'blur' }],
  problemAnalysisScore: [{ type: 'number', min: 0, max: 20, message: '问题分析得分范围为0-20分', trigger: 'blur' }],
  implementationScore: [{ type: 'number', min: 0, max: 20, message: '实施得分范围为0-20分', trigger: 'blur' }],
  resultScore: [{ type: 'number', min: 0, max: 30, message: '成果得分超出范围', trigger: 'blur' }],
  reviewScore: [{ type: 'number', min: 0, max: 10, message: '检讨得分范围为0-10分', trigger: 'blur' }],
  operationScore: [{ type: 'number', min: 0, max: 10, message: '整体运作得分范围为0-10分', trigger: 'blur' }],
  presentationScore: [{ type: 'number', min: 0, max: 15, message: '资料呈现得分范围为0-15分', trigger: 'blur' }],
  // 面谈分值规则
  topicScore: [{ type: 'number', min: 0, max: 10, message: '选题得分范围为0-10分', trigger: 'blur' }],
  processScore: [{ type: 'number', min: 0, max: 40, message: '改善过程得分范围为0-40分', trigger: 'blur' }],
  interviewOperationScore: [{ type: 'number', min: 0, max: 20, message: '整体运作得分范围为0-20分', trigger: 'blur' }],
  // 评价字段
  highlights: [{ max: 1000, message: '亮点不能超过1000字', trigger: 'blur' }],
  shortcomings: [
    {
      validator: (rule, value, callback) => {
        if (isInterviewStage.value) { callback(); return }
        if (!value || value.trim().length === 0) {
          callback(new Error('不足之处为必填项，请至少例举三条'))
        } else if (value.length < 60) {
          callback(new Error('不足之处至少填写60字'))
        } else if (value.length > 1000) {
          callback(new Error('不足之处不能超过1000字'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const loadData = async () => {
  loading.value = true
  try {
    // 先从 query 中获取基本信息
    taskInfo.projectName = route.query.projectName || ''
    taskInfo.institutionName = route.query.institutionName || ''
    taskInfo.institutionLevel = route.query.institutionLevel || ''
    taskInfo.stage = route.query.stage || 'BOOK'
    
    // 加载项目详情
    if (registrationId.value) {
      try {
        const detailRes = await getRegistrationDetail(registrationId.value)
        if (detailRes.success && detailRes.data) {
          const data = detailRes.data
          
          // 保存完整项目详情
          projectDetail.value = {
            registration: data.registration,
            members: data.members || [],
            activityInfo: data.activityInfo,
            summary: data.projectSummary,  // 注意：后端返回的是 projectSummary
            materials: data.materials || []
          }
          
          // 更新任务基本信息（从 registration 对象中提取，优先使用详情接口返回的数据）
          const reg = data.registration || {}
          if (reg.projectName) {
            taskInfo.projectName = reg.projectName
          }
          if (reg.groupType) {
            taskInfo.groupType = reg.groupType
          }
          if (reg.status) {
            taskInfo.status = reg.status
          }
          
          console.log('项目详情加载成功:', {
            projectName: taskInfo.projectName,
            institutionName: taskInfo.institutionName,
            groupType: reg.groupType,
            members: data.members?.length,
            hasActivity: !!data.activityInfo,
            hasSummary: !!data.projectSummary
          })
        }
      } catch (error) {
        console.error('加载项目详情失败:', error)
        ElMessage.error('加载项目详情失败')
      }
    } else {
      console.warn('缺少 registrationId，无法加载项目详情')
      ElMessage.warning('缺少项目ID，无法加载详情')
    }
    
    // 加载已有评分数据（查看模式 / 草稿 / 已提交均尝试加载）
    if (taskId.value) {
      try {
        const fetchFn = taskInfo.stage === 'INTERVIEW' ? getInterviewScore : getReviewScore
        const scoreRes = await fetchFn(taskId.value)
        if (scoreRes.success && scoreRes.data) {
          const data = scoreRes.data
          if (taskInfo.stage === 'INTERVIEW') {
            form.topicScore = data.topic || 0
            form.processScore = data.process || 0
            form.interviewOperationScore = data.operation || data.interviewOperation || 0
            form.resultScore = data.result || 0
          } else {
            form.planScore = data.plan || 0
            form.problemAnalysisScore = data.problem || 0
            form.implementationScore = data.action || 0
            form.resultScore = data.success || 0
            form.reviewScore = data.review || 0
            form.operationScore = data.operation || 0
            form.presentationScore = data.presentation || 0
          }
          form.highlights = data.highlight || ''
          form.shortcomings = data.weakness || ''
          if (!data.submittedAt) {
            draftSavedAt.value = data.updatedAt ? dayjs(data.updatedAt).format('HH:mm:ss') : '已保存'
            setTimeout(() => { draftSavedAt.value = '' }, 2000)
          }
        }
      } catch (error) {
        // 无已有评分，默认满分
        if (taskInfo.stage === 'INTERVIEW') {
          Object.assign(form, INTERVIEW_MAX)
        } else {
          Object.assign(form, BOOK_MAX)
        }
        console.log('未找到已有评分数据，默认满分')
      }
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const getStageText = (stage) => {
  const map = {
    'BOOK': '书审',
    'INTERVIEW': '面谈',
    'FINAL': '决赛'
  }
  return map[stage] || stage || '-'
}

const getGroupTypeText = (type) => {
  const map = {
    'BASIC': '基层组',
    'COMPREHENSIVE': '综合组',
    'ADVANCED': '进阶组'
  }
  return map[type] || type || '-'
}

// 处理"其他"选项 - 改善就医环境
const getExperienceImproveDisplay = (activityInfo) => {
  if (!activityInfo) {
    return '未填写'
  }
  
  // 如果选择了"其他"，显示自定义内容
  if (activityInfo.experienceImproveCode === 'other') {
    return activityInfo.experienceImproveOther || '其他'
  }
  
  // 直接显示Label，不回退到Code
  return activityInfo.experienceImproveLabel || '未填写'
}

// 处理"其他"选项 - 医疗质量相关主题
const getQualityTopicDisplay = (activityInfo) => {
  if (!activityInfo) {
    return '未填写'
  }
  
  // 如果选择了"其他"，显示自定义内容
  if (activityInfo.qualityTopicCode === 'other') {
    return activityInfo.qualityTopicOther || '其他'
  }
  
  // 直接显示Label，不回退到Code
  return activityInfo.qualityTopicLabel || '未填写'
}

const buildSubmitData = () => {
  const base = {
    reviewTaskId: parseInt(taskId.value),
    highlight: form.highlights || undefined,
    weakness: form.shortcomings || undefined
  }
  if (isInterviewStage.value) {
    return {
      ...base,
      topic: form.topicScore,
      process: form.processScore,
      operation: form.interviewOperationScore,   // API 字段名是 operation，不是 interviewOperation
      result: form.resultScore
    }
  }
  return {
    ...base,
    plan: form.planScore,
    problem: form.problemAnalysisScore,
    action: form.implementationScore,
    success: form.resultScore,
    review: form.reviewScore,
    operation: form.operationScore,
    presentation: form.presentationScore
  }
}

const saveDraft = async () => {
  if (draftSaving.value) return
  draftSaving.value = true
  try {
    const data = buildSubmitData()
    const res = isInterviewStage.value
      ? await saveInterviewDraft(data)
      : await saveBookReviewDraft(data)
    if (res && res.success !== false) {
      draftSavedAt.value = dayjs().format('HH:mm:ss')
      setTimeout(() => { draftSavedAt.value = '' }, 2000)
    }
  } catch (e) {
    // 草稿接口未实现时静默失败，不打扰用户
    console.warn('草稿保存失败（后端未实现）:', e?.response?.status)
  } finally {
    draftSaving.value = false
  }
}

// 规避
const recuseDialogVisible = ref(false)
const recusing = ref(false)
const recuseFormRef = ref(null)
const recuseReasons = ref([])
const recuseForm = reactive({ reasonCode: '', reasonOther: '' })
const recuseRules = {
  reasonCode: [{ required: true, message: '请选择规避原因', trigger: 'change' }],
  reasonOther: [
    {
      validator: (rule, value, callback) => {
        if (recuseForm.reasonCode === 'OTHER' && !value) callback(new Error('请填写补充说明'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

const openRecuseDialog = async () => {
  recuseForm.reasonCode = ''
  recuseForm.reasonOther = ''
  if (recuseReasons.value.length === 0) {
    try {
      const res = await getRecuseReasons()
      recuseReasons.value = res.success ? (res.data || []).filter(r => r.code !== 'KNOW_LEADER') : []
    } catch { recuseReasons.value = [] }
  }
  recuseDialogVisible.value = true
}

const confirmRecuse = async () => {
  try {
    await recuseFormRef.value.validate()
    recusing.value = true
    const res = await recuseReviewTask(parseInt(taskId.value), {
      reasonCode: recuseForm.reasonCode,
      reasonOther: recuseForm.reasonOther || undefined
    })
    if (res.success) {
      ElMessage.success('规避申请已提交')
      recuseDialogVisible.value = false
      router.push('/reviewer/dashboard')
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    if (e !== false) ElMessage.error(e?.response?.data?.message || '操作失败')
  } finally {
    recusing.value = false
  }
}

const goBack = () => {
  router.push('/reviewer/dashboard')
}

const getMaterialTypeLabel = (type) => {
  const map = {
    'REGISTRATION_FORM_DOC': '报名表 Word',
    'REGISTRATION_FORM_PDF': '报名表 PDF',
    'REGISTRATION_FORM': '报名表',
    'REPORT': '成果报告书',
    'EVIDENCE': '佐证材料'
  }
  return map[type] || type
}

const filePreviewVisible = ref(false)
const previewMaterialId = ref(null)
const previewFileName = ref('')
const previewFileUrl = ref(null)

const canPreview = (fileName) => {
  if (!fileName) return false
  const ext = fileName.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'docx', 'xlsx', 'xls'].includes(ext)
}

const previewFile = (material) => {
  previewMaterialId.value = material.id
  previewFileName.value = material.fileName || '文件预览'
  previewFileUrl.value = null
  filePreviewVisible.value = true
}

// 打开评分标准文件预览弹窗
const openScoringStandard = (type) => {
  const base = import.meta.env.BASE_URL
  const fileMap = {
    book: { url: `${base}scoring_standard_book.docx`, name: '书审评分标准.docx' },
    interview: { url: `${base}scoring_standard_interview.docx`, name: '面谈评分标准.docx' }
  }
  const file = fileMap[type]
  if (file) {
    previewMaterialId.value = null
    previewFileUrl.value = file.url
    previewFileName.value = file.name
    filePreviewVisible.value = true
  }
}

const downloadFile = async (material) => {
  try {
    const blob = await downloadMaterial(material.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = material.fileName || '材料文件'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载文件失败:', error)
    ElMessage.error('下载失败')
  }
}

onMounted(() => {
  loadData()
})

// 非查看模式时启动草稿自动保存（30s/次）
watch(isViewMode, (viewMode) => {
  if (!viewMode) {
    if (draftTimer) clearInterval(draftTimer)
    draftTimer = setInterval(() => {
      if (!isViewMode.value) saveDraft()
    }, 30000)
  } else {
    if (draftTimer) { clearInterval(draftTimer); draftTimer = null }
  }
}, { immediate: true })

onUnmounted(() => {
  if (draftTimer) clearInterval(draftTimer)
  window.removeEventListener('resize', onResize)
})

// 监听路由变化，重新加载数据
watch(() => route.query.registrationId, (newId, oldId) => {
  if (newId && newId !== oldId) {
    console.log('路由变化，重新加载数据:', newId)
    loadData()
  }
})
</script>

<style scoped lang="scss">
.review-page {
  padding: 20px;
  
  .card-header {
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
  }
  
  /* ── Slider ── */
  .materials-section {
    margin: 0 0 20px 0;
    padding: 14px 16px;
    background: #fafafa;
    border: 1px solid #e4e7ed;
    border-radius: 6px;

    .materials-title {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 10px;
      padding-left: 8px;
      border-left: 3px solid #409EFF;
    }

    .materials-empty {
      color: #909399;
      font-size: 13px;
      text-align: center;
      padding: 20px 0;
    }

    .no-preview-tip {
      font-size: 12px;
      color: #c0c4cc;
    }
  }

  // ── 评分区顶栏 ────────────────────────────────────────────────────
  .scoring-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #f5f7fa;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    padding: 10px 16px;
    margin-bottom: 12px;
    font-size: 13px;
    font-weight: 600;
    color: #303133;
  }

  // ── 评分条目卡片（左细则 + 右滑条）────────────────────────────────
  .score-item-card {
    display: flex;
    gap: 20px;
    align-items: flex-start;
    background: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: box-shadow 0.2s;

    &:hover {
      box-shadow: 0 2px 8px rgba(0,0,0,.08);
    }

    .score-item-criteria {
      flex: 1;
      min-width: 0;

      .criteria-title {
        font-size: 14px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 8px;
        display: flex;
        align-items: baseline;
        gap: 8px;
        flex-wrap: wrap;
      }

      .criteria-max {
        font-size: 12px;
        font-weight: normal;
        color: #909399;
        background: #f0f2f5;
        padding: 1px 7px;
        border-radius: 10px;
      }

      .criteria-list {
        margin: 0;
        padding-left: 18px;
        color: #606266;
        font-size: 12.5px;
        line-height: 1.9;

        li {
          margin-bottom: 2px;
        }
      }
    }

    .score-item-right {
      flex-shrink: 0;
      width: 360px;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding-top: 4px;

      .score-slider {
        width: 100%;
      }

      .score-display {
        margin-top: 28px;
      }
    }
  }

  .score-slider-wrap {
    display: flex;
    align-items: center;
    gap: 20px;
    width: 100%;
    padding-bottom: 22px; // 留出刻度标签空间
  }

  .score-slider {
    flex: 1;

    // 轨道更细
    :deep(.el-slider__runway) {
      height: 4px;
      border-radius: 2px;
      background: #e4e7ed;
    }

    :deep(.el-slider__bar) {
      height: 4px;
      border-radius: 2px;
      background: linear-gradient(90deg, #a0cfff, #409EFF);
    }

    // 滑块更小更精致
    :deep(.el-slider__button-wrapper) {
      top: -14px;
      cursor: ew-resize;
    }

    :deep(.el-slider__button) {
      width: 16px;
      height: 16px;
      border: 2px solid #409EFF;
      box-shadow: 0 2px 6px rgba(64, 158, 255, 0.35);
      transition: transform 0.15s;
      cursor: ew-resize;

      &:hover { transform: scale(1.25); }
    }

    // 刻度点
    :deep(.el-slider__stop) {
      width: 4px;
      height: 4px;
      background: #c0c4cc;
      border-radius: 50%;
      top: 0;
    }

    // 刻度标签
    :deep(.el-slider__marks-text) {
      font-size: 11px;
      color: #c0c4cc;
      margin-top: 6px;
      white-space: nowrap;
    }
  }

  .score-display {
    display: flex;
    align-items: baseline;
    gap: 3px;
    min-width: 68px;
    flex-shrink: 0;

    .score-num {
      font-size: 20px;
      font-weight: 700;
      color: #409EFF;
      line-height: 1;
    }

    .score-denom {
      font-size: 12px;
      color: #c0c4cc;
    }
  }

  /* ── 折叠区域视觉增强 ── */
  :deep(.el-collapse) {
    border: none;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  }

  :deep(.el-collapse-item) {
    margin-bottom: 4px;

    &:last-child { margin-bottom: 0; }
  }

  :deep(.el-collapse-item__header) {
    background: #f5f7fa;
    padding: 0 16px;
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    border-left: 3px solid #409EFF;
    border-bottom: 1px solid #ebeef5;
    height: 46px;
    transition: background 0.2s, color 0.2s;

    &:hover {
      background: #ecf5ff;
      color: #409EFF;
    }

    &.is-active {
      color: #409EFF;
      background: #ecf5ff;
      border-left-color: #409EFF;
    }
  }

  :deep(.el-collapse-item__wrap) {
    background: #fff;
    border-left: 3px solid #e0edff;
    padding: 16px 16px 8px;
  }

  :deep(.el-collapse-item__content) {
    padding-bottom: 0;
  }
}

// 项目信息折叠区（与评分区保持一致样式）
.project-info-collapse {
  :deep(.el-collapse-item__header) {
    background: #f5f7fa;
    padding: 0 16px;
    font-weight: 600;
    font-size: 13px;
    color: #303133;
    border-radius: 6px;
  }
  :deep(.el-collapse-item__wrap) {
    border-left: 3px solid #e0edff;
    background: #fff;
    padding: 12px 16px 4px;
  }
  :deep(.el-collapse-item__content) { padding-bottom: 0; }
  :deep(.el-collapse) { border: none; border-radius: 6px; overflow: hidden; }
  :deep(.el-form-item) { margin-bottom: 10px; }
}

// 总分 / 亮点 / 不足 左对齐区域
.bottom-section {
  padding: 12px 0 0;
  border-top: 1px solid #ebeef5;
  margin-top: 8px;
}

.bottom-item {
  margin-bottom: 16px;
}

.bottom-label {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.required-star {
  color: #f56c6c;
  font-size: 14px;
}

.total-score-row {
  display: flex;
  align-items: baseline;
  gap: 6px;

  .total-score-value {
    font-size: 36px;
    font-weight: 700;
    color: #409EFF;
    line-height: 1;
  }

  .total-score-unit {
    font-size: 14px;
    color: #909399;
  }
}

/* ── 移动端评分页适配 ── */
@media (max-width: 768px) {
  .review-page {
    :deep(.el-card__body) {
      padding: 12px 10px;
    }

    // 评分卡片：改为上下布局
    .score-item-card {
      flex-direction: column;
      gap: 12px;
      padding: 12px 10px;
    }

    // 右侧打分区：宽度撑满，不再固定360px
    .score-item-right {
      width: 100% !important;
      padding: 0 4px 0 0;
    }

    // 滑块容器
    .score-slider-wrap {
      gap: 10px;
      padding-bottom: 28px;
    }

    // 刻度标签字体更小防溢出
    :deep(.el-slider__marks-text) {
      font-size: 10px !important;
    }

    // 评分标准文件按钮在小屏换行
    .scoring-header {
      flex-wrap: wrap;
      gap: 6px;
    }

    // 表格横向可滚动
    :deep(.el-table) {
      font-size: 12px;
    }

    // 底部操作按钮堆叠
    .action-bar {
      flex-direction: column;
      gap: 8px;

      .el-button {
        width: 100%;
      }
    }

    // 总分展示放大
    .total-score-row .total-score-value {
      font-size: 28px;
    }

    // 描述列表手机单列
    :deep(.el-descriptions__body .el-descriptions__table) {
      display: block;
      width: 100%;

      tr {
        display: flex;
        flex-direction: column;
      }

      td {
        width: 100% !important;
      }
    }
  }
}
</style>
