<template>
  <div class="shortlist-management">
    <!-- 赛事进度条 -->
    <StageProgress :stages="stagesList" />

    <!-- 入围策略配置 -->
    <el-card class="config-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">入围策略配置</span>
          <el-tag type="info">综合书审和面谈排名</el-tag>
        </div>
      </template>

      <el-form label-width="120px">
        <!-- 评分权重 -->
        <el-form-item label="评分权重">
          <el-alert
            title="说明：基层组和综合组仅书审评分，进阶组为书审+面谈加权平均"
            type="info"
            :closable="false"
            style="margin-bottom: 15px"
          />
          <div class="weight-config">
            <span style="margin-right: 10px">书审权重:</span>
            <el-input-number
              v-model="config.bookWeight"
              :min="0"
              :max="100"
              :step="5"
              style="width: 120px"
            />
            <span style="margin: 0 20px 0 5px">%</span>
            
            <span style="margin-right: 10px">面谈权重:</span>
            <el-input-number
              v-model="config.interviewWeight"
              :min="0"
              :max="100"
              :step="5"
              style="width: 120px"
            />
            <span style="margin: 0 20px 0 5px">%</span>
            
            <el-button
              type="primary"
              @click="applyWeight"
              :disabled="config.bookWeight + config.interviewWeight !== 100"
            >
              应用权重
            </el-button>
            
            <el-tag
              v-if="config.bookWeight + config.interviewWeight !== 100"
              type="warning"
              style="margin-left: 10px"
            >
              权重总和必须为100%
            </el-tag>
          </div>
        </el-form-item>

        <!-- 入围比例 -->
        <el-form-item label="入围比例">
          <el-radio-group v-model="config.ratioType" @change="handleRatioChange">
            <el-radio value="30">前30%</el-radio>
            <el-radio value="40">前40%</el-radio>
            <el-radio value="50">前50%</el-radio>
            <el-radio value="custom">自定义</el-radio>
          </el-radio-group>
          <el-input-number
            v-if="config.ratioType === 'custom'"
            v-model="config.customRatio"
            :min="1"
            :max="100"
            style="width: 120px; margin-left: 10px"
            @change="handleRatioChange"
          >
            <template #suffix>%</template>
          </el-input-number>
        </el-form-item>

        <!-- 最低分数线 -->
        <el-form-item label="最低分数线">
          <el-input-number
            v-model="config.minScore"
            :min="0"
            :max="100"
            :precision="1"
            style="width: 150px"
          />
          <span style="margin-left: 10px">分</span>
          <el-text type="info" style="margin-left: 20px" size="small">
            低于此分数的项目将自动排除
          </el-text>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="loadData" :loading="loading" icon="Refresh">
            刷新数据
          </el-button>
          <el-button
            type="success"
            @click="batchSetShortlist"
            :disabled="eligibleProjects.length === 0"
            icon="Select"
          >
            批量设置入围（按当前配置）
          </el-button>
          <el-button
            @click="exportList"
            :disabled="projects.length === 0"
            icon="Download"
          >
            导出入围名单
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="hover">
      <el-form inline>
        <el-form-item label="组别">
          <el-select
            v-model="filters.groupType"
            placeholder="全部组别"
            clearable
            style="width: 150px"
          >
            <el-option label="基层组" value="BASIC" />
            <el-option label="进阶组" value="ADVANCED" />
            <el-option label="综合组" value="COMPREHENSIVE" />
          </el-select>
        </el-form-item>

        <el-form-item label="搜索">
          <el-input
            v-model="filters.projectName"
            placeholder="搜索项目名称"
            clearable
            style="width: 250px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="filters.shortlistStatus"
            placeholder="全部状态"
            clearable
            style="width: 180px"
          >
            <el-option label="已入围" value="shortlisted" />
            <el-option label="未入围" value="not-shortlisted" />
            <el-option label="待评分/待面谈" value="pending-interview" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计信息 -->
    <el-card class="stats-card" shadow="hover">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-statistic title="总项目数" :value="projects.length" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="已完成书审" :value="completedBookCount" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="已完成面谈" :value="completedInterviewCount" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="当前入围数" :value="shortlistedCount">
            <template #suffix>
              <span style="font-size: 14px; color: #909399">
                ({{ shortlistRatio }}%)
              </span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="4">
          <el-statistic title="手动增补" :value="manualAddCount" suffix="项" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="手动取消" :value="manualRemoveCount" suffix="项" />
        </el-col>
      </el-row>
    </el-card>

    <!-- 项目列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">综合排名列表</span>
          <div>
            <el-tag type="success" style="margin-right: 10px">
              基层组/综合组：仅书审
            </el-tag>
            <el-tag type="info">
              进阶组：书审{{ config.bookWeight }}% + 面谈{{ config.interviewWeight }}%
            </el-tag>
          </div>
        </div>
      </template>

      <el-table
        :data="filteredProjects"
        border
        stripe
        v-loading="loading"
        :row-class-name="getRowClassName"
        style="width: 100%"
      >
        <!-- 综合排名 -->
        <el-table-column prop="rank" label="综合排名" width="100" align="center" fixed>
          <template #default="{ row }">
            <el-tag
              v-if="row.rank && row.rank <= 3"
              :type="getRankTagType(row.rank)"
              effect="dark"
              size="large"
            >
              🏅 {{ row.rank }}
            </el-tag>
            <span v-else-if="row.rank" style="font-weight: bold; font-size: 16px">
              {{ row.rank }}
            </span>
            <span v-else style="color: #909399">-</span>
          </template>
        </el-table-column>

        <!-- 得分详情 -->
        <el-table-column label="得分详情" width="160" align="center">
          <template #default="{ row }">
            <div class="score-detail">
              <div class="score-item">
                <span class="score-label">书审:</span>
                <span
                  class="score-value"
                  :style="{ color: getScoreColor(row.bookScore) }"
                >
                  {{ row.bookScore !== null ? row.bookScore.toFixed(1) : '-' }}
                </span>
              </div>
              <div class="score-item">
                <span class="score-label">面谈:</span>
                <span
                  class="score-value"
                  :style="{ color: getScoreColor(row.interviewScore) }"
                >
                  {{ row.interviewScore !== null ? row.interviewScore.toFixed(1) : '-' }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 项目名称 -->
        <el-table-column prop="projectName" label="项目名称" min-width="220" show-overflow-tooltip />

        <!-- 医疗机构 -->
        <el-table-column
          prop="institutionName"
          label="医疗机构"
          min-width="200"
          show-overflow-tooltip
        />

        <!-- 机构等级 -->
        <el-table-column
          prop="institutionLevel"
          label="机构等级"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <el-tag v-if="row.institutionLevel" type="success" size="small">
              {{ row.institutionLevel }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <!-- 组别 -->
        <el-table-column prop="groupType" label="组别" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getGroupTypeTagType(row.groupType)">
              {{ getGroupTypeLabel(row.groupType) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 综合得分 -->
        <el-table-column prop="compositeScore" label="综合得分" width="120" align="center">
          <template #default="{ row }">
            <span
              v-if="row.compositeScore !== null"
              :style="{
                color: getScoreColor(row.compositeScore),
                fontWeight: 'bold',
                fontSize: '16px'
              }"
            >
              {{ row.compositeScore.toFixed(1) }}
            </span>
            <el-tag v-else-if="row.groupType === 'ADVANCED'" type="warning">待面谈</el-tag>
            <el-tag v-else type="info">待评分</el-tag>
          </template>
        </el-table-column>

        <!-- 入围状态 -->
        <el-table-column label="入围状态" width="140" align="center">
          <template #default="{ row }">
            <el-tag :type="getShortlistTagType(row)" effect="dark" size="large">
              {{ getShortlistLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 操作 -->
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)" icon="View">
              查看详情
            </el-button>
            <el-button
              v-if="row.isShortlisted"
              size="small"
              type="warning"
              @click="toggleShortlist(row, false)"
              icon="CircleClose"
            >
              取消入围
            </el-button>
            <el-button
              v-else
              size="small"
              type="success"
              @click="toggleShortlist(row, true)"
              icon="CircleCheck"
              :disabled="row.compositeScore === null"
            >
              增补入围
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="项目详细评分"
      width="85%"
      :close-on-click-modal="false"
    >
      <div v-if="selectedProject" v-loading="detailLoading">
        <h3 style="margin-bottom: 20px">{{ selectedProject.projectName }}</h3>
        
        <el-descriptions :column="2" border style="margin-bottom: 30px">
          <el-descriptions-item label="综合排名" label-class-name="detail-label">
            <el-tag
              v-if="selectedProject.rank && selectedProject.rank <= 3"
              :type="getRankTagType(selectedProject.rank)"
              size="large"
            >
              第 {{ selectedProject.rank }} 名
            </el-tag>
            <span v-else-if="selectedProject.rank" style="font-size: 16px; font-weight: bold">
              第 {{ selectedProject.rank }} 名
            </span>
            <span v-else>待面谈</span>
          </el-descriptions-item>
          <el-descriptions-item label="综合得分" label-class-name="detail-label">
            <span
              v-if="selectedProject.compositeScore !== null"
              style="color: #409eff; font-size: 20px; font-weight: bold"
            >
              {{ selectedProject.compositeScore.toFixed(1) }} 分
            </span>
            <span v-else-if="selectedProject.groupType === 'ADVANCED'" style="color: #909399">
              待面谈
            </span>
            <span v-else style="color: #909399">待评分</span>
          </el-descriptions-item>
          <el-descriptions-item label="书审得分" label-class-name="detail-label">
            <span style="font-size: 16px">
              {{ selectedProject.bookScore !== null ? selectedProject.bookScore.toFixed(1) + ' 分' : '-' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="面谈得分" label-class-name="detail-label">
            <span style="font-size: 16px">
              {{ selectedProject.interviewScore !== null ? selectedProject.interviewScore.toFixed(1) + ' 分' : '-' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="组别" label-class-name="detail-label">
            <el-tag :type="getGroupTypeTagType(selectedProject.groupType)" size="large">
              {{ getGroupTypeLabel(selectedProject.groupType) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="医疗机构" label-class-name="detail-label">
            {{ selectedProject.institutionName }}
          </el-descriptions-item>
          <el-descriptions-item label="入围状态" label-class-name="detail-label" :span="2">
            <el-tag :type="getShortlistTagType(selectedProject)" size="large">
              {{ getShortlistLabel(selectedProject) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 详细评分Tab -->
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 书审评分 -->
          <el-tab-pane label="书审评分" name="BOOK">
            <div v-if="bookDetail && bookDetail.avgTotal !== null">
              <h4 style="margin-bottom: 15px">分项得分</h4>
              <el-table :data="[bookDetail]" border style="margin-bottom: 30px">
                <el-table-column prop="avgPlan" label="计划" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgPlan !== null ? row.avgPlan.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgProblem" label="问题" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgProblem !== null ? row.avgProblem.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgAction" label="行动" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgAction !== null ? row.avgAction.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgSuccess" label="成效" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgSuccess !== null ? row.avgSuccess.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgReview" label="回顾" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgReview !== null ? row.avgReview.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgOperation" label="运作" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgOperation !== null ? row.avgOperation.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgPresentation" label="展示" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgPresentation !== null ? row.avgPresentation.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgTotal" label="总分" align="center" width="100">
                  <template #default="{ row }">
                    <strong style="color: #409eff; font-size: 16px">
                      {{ row.avgTotal !== null ? row.avgTotal.toFixed(1) : '-' }}
                    </strong>
                  </template>
                </el-table-column>
              </el-table>

              <h4 style="margin-bottom: 15px">评委意见汇总</h4>
              <el-row :gutter="20" style="margin-bottom: 30px">
                <el-col :span="12">
                  <el-card header="✨ 亮点" shadow="never">
                    <ul v-if="bookDetail.highlights && bookDetail.highlights.length > 0" class="opinion-list">
                      <li v-for="(h, i) in bookDetail.highlights" :key="i">{{ h }}</li>
                    </ul>
                    <el-empty v-else description="暂无亮点" :image-size="80" />
                  </el-card>
                </el-col>
                <el-col :span="12">
                  <el-card header="💡 改进建议" shadow="never">
                    <ul v-if="bookDetail.weaknesses && bookDetail.weaknesses.length > 0" class="opinion-list">
                      <li v-for="(w, i) in bookDetail.weaknesses" :key="i">{{ w }}</li>
                    </ul>
                    <el-empty v-else description="暂无改进建议" :image-size="80" />
                  </el-card>
                </el-col>
              </el-row>

              <!-- 评委详细评分 -->
              <h4 style="margin-bottom: 15px">评委详细评分（共 {{ bookReviewers.length }} 位评委）</h4>
              <div v-if="bookReviewers.length > 0">
                <el-card 
                  v-for="(reviewer, index) in bookReviewers" 
                  :key="reviewer.reviewerId"
                  shadow="hover" 
                  style="margin-bottom: 20px"
                >
                  <template #header>
                    <div style="display: flex; justify-content: space-between; align-items: center">
                      <span style="font-weight: 600; font-size: 16px">
                        评委 {{ index + 1 }}: {{ reviewer.reviewerName }}
                      </span>
                      <div>
                        <el-tag size="small" type="info">{{ reviewer.reviewerTitle }}</el-tag>
                        <el-tag size="small" type="success" style="margin-left: 8px">{{ reviewer.reviewerInstitutionLevel }}</el-tag>
                      </div>
                    </div>
                    <div style="color: #909399; font-size: 13px; margin-top: 5px">
                      {{ reviewer.reviewerInstitutionName }} | 评审时间: {{ reviewer.submittedAt ? new Date(reviewer.submittedAt).toLocaleString('zh-CN') : '-' }}
                    </div>
                  </template>
                  
                  <!-- 分项评分 -->
                  <el-descriptions :column="4" border size="small" style="margin-bottom: 15px">
                    <el-descriptions-item label="计划">{{ reviewer.scores.plan }}分</el-descriptions-item>
                    <el-descriptions-item label="问题">{{ reviewer.scores.problem }}分</el-descriptions-item>
                    <el-descriptions-item label="行动">{{ reviewer.scores.action }}分</el-descriptions-item>
                    <el-descriptions-item label="成效">{{ reviewer.scores.success }}分</el-descriptions-item>
                    <el-descriptions-item label="回顾">{{ reviewer.scores.review }}分</el-descriptions-item>
                    <el-descriptions-item label="运作">{{ reviewer.scores.operation }}分</el-descriptions-item>
                    <el-descriptions-item label="展示">{{ reviewer.scores.presentation }}分</el-descriptions-item>
                    <el-descriptions-item label="总分">
                      <strong style="color: #409eff; font-size: 16px">{{ reviewer.scores.total }}分</strong>
                    </el-descriptions-item>
                  </el-descriptions>
                  
                  <!-- 评语 -->
                  <el-row :gutter="15">
                    <el-col :span="12">
                      <div style="background: #e8f5e9; padding: 12px; border-radius: 4px">
                        <div style="font-weight: 600; margin-bottom: 8px; color: #2e7d32">✨ 亮点</div>
                        <div style="color: #2e7d32; line-height: 1.6">{{ reviewer.highlight || '暂无' }}</div>
                      </div>
                    </el-col>
                    <el-col :span="12">
                      <div style="background: #fff3e0; padding: 12px; border-radius: 4px">
                        <div style="font-weight: 600; margin-bottom: 8px; color: #f57c00">💡 改进建议</div>
                        <div style="color: #f57c00; line-height: 1.6">{{ reviewer.weakness || '暂无' }}</div>
                      </div>
                    </el-col>
                  </el-row>
                </el-card>
              </div>
              <el-empty v-else description="暂无评委评分记录" :image-size="100" />
            </div>
            <el-empty v-else :description="getBookReviewEmptyText()" :image-size="120" />
          </el-tab-pane>

          <!-- 面谈评分 -->
          <el-tab-pane label="面谈评分" name="INTERVIEW">
            <div v-if="interviewDetail && interviewDetail.avgTotal !== null">
              <h4 style="margin-bottom: 15px">分项得分</h4>
              <el-table :data="[interviewDetail]" border style="margin-bottom: 30px">
                <el-table-column prop="avgPlan" label="计划" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgPlan !== null ? row.avgPlan.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgProblem" label="问题" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgProblem !== null ? row.avgProblem.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgAction" label="行动" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgAction !== null ? row.avgAction.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgSuccess" label="成效" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgSuccess !== null ? row.avgSuccess.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgReview" label="回顾" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgReview !== null ? row.avgReview.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgOperation" label="运作" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgOperation !== null ? row.avgOperation.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgPresentation" label="展示" align="center" width="90">
                  <template #default="{ row }">
                    {{ row.avgPresentation !== null ? row.avgPresentation.toFixed(1) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="avgTotal" label="总分" align="center" width="100">
                  <template #default="{ row }">
                    <strong style="color: #409eff; font-size: 16px">
                      {{ row.avgTotal !== null ? row.avgTotal.toFixed(1) : '-' }}
                    </strong>
                  </template>
                </el-table-column>
              </el-table>

              <h4 style="margin-bottom: 15px">评委意见汇总</h4>
              <el-row :gutter="20" style="margin-bottom: 30px">
                <el-col :span="12">
                  <el-card header="✨ 亮点" shadow="never">
                    <ul v-if="interviewDetail.highlights && interviewDetail.highlights.length > 0" class="opinion-list">
                      <li v-for="(h, i) in interviewDetail.highlights" :key="i">{{ h }}</li>
                    </ul>
                    <el-empty v-else description="暂无亮点" :image-size="80" />
                  </el-card>
                </el-col>
                <el-col :span="12">
                  <el-card header="💡 改进建议" shadow="never">
                    <ul v-if="interviewDetail.weaknesses && interviewDetail.weaknesses.length > 0" class="opinion-list">
                      <li v-for="(w, i) in interviewDetail.weaknesses" :key="i">{{ w }}</li>
                    </ul>
                    <el-empty v-else description="暂无改进建议" :image-size="80" />
                  </el-card>
                </el-col>
              </el-row>

              <!-- 评委详细评分 -->
              <h4 style="margin-bottom: 15px">评委详细评分（共 {{ interviewReviewers.length }} 位评委）</h4>
              <div v-if="interviewReviewers.length > 0">
                <el-card 
                  v-for="(reviewer, index) in interviewReviewers" 
                  :key="reviewer.reviewerId"
                  shadow="hover" 
                  style="margin-bottom: 20px"
                >
                  <template #header>
                    <div style="display: flex; justify-content: space-between; align-items: center">
                      <span style="font-weight: 600; font-size: 16px">
                        评委 {{ index + 1 }}: {{ reviewer.reviewerName }}
                      </span>
                      <div>
                        <el-tag size="small" type="info">{{ reviewer.reviewerTitle }}</el-tag>
                        <el-tag size="small" type="success" style="margin-left: 8px">{{ reviewer.reviewerInstitutionLevel }}</el-tag>
                      </div>
                    </div>
                    <div style="color: #909399; font-size: 13px; margin-top: 5px">
                      {{ reviewer.reviewerInstitutionName }} | 评审时间: {{ reviewer.submittedAt ? new Date(reviewer.submittedAt).toLocaleString('zh-CN') : '-' }}
                    </div>
                  </template>
                  
                  <!-- 分项评分 -->
                  <el-descriptions :column="4" border size="small" style="margin-bottom: 15px">
                    <el-descriptions-item label="计划">{{ reviewer.scores.plan }}分</el-descriptions-item>
                    <el-descriptions-item label="问题">{{ reviewer.scores.problem }}分</el-descriptions-item>
                    <el-descriptions-item label="行动">{{ reviewer.scores.action }}分</el-descriptions-item>
                    <el-descriptions-item label="成效">{{ reviewer.scores.success }}分</el-descriptions-item>
                    <el-descriptions-item label="回顾">{{ reviewer.scores.review }}分</el-descriptions-item>
                    <el-descriptions-item label="运作">{{ reviewer.scores.operation }}分</el-descriptions-item>
                    <el-descriptions-item label="展示">{{ reviewer.scores.presentation }}分</el-descriptions-item>
                    <el-descriptions-item label="总分">
                      <strong style="color: #409eff; font-size: 16px">{{ reviewer.scores.total }}分</strong>
                    </el-descriptions-item>
                  </el-descriptions>
                  
                  <!-- 评语 -->
                  <el-row :gutter="15">
                    <el-col :span="12">
                      <div style="background: #e8f5e9; padding: 12px; border-radius: 4px">
                        <div style="font-weight: 600; margin-bottom: 8px; color: #2e7d32">✨ 亮点</div>
                        <div style="color: #2e7d32; line-height: 1.6">{{ reviewer.highlight || '暂无' }}</div>
                      </div>
                    </el-col>
                    <el-col :span="12">
                      <div style="background: #fff3e0; padding: 12px; border-radius: 4px">
                        <div style="font-weight: 600; margin-bottom: 8px; color: #f57c00">💡 改进建议</div>
                        <div style="color: #f57c00; line-height: 1.6">{{ reviewer.weakness || '暂无' }}</div>
                      </div>
                    </el-col>
                  </el-row>
                </el-card>
              </div>
              <el-empty v-else description="暂无评委评分记录" :image-size="100" />
            </div>
            <el-empty v-else :description="getInterviewEmptyText()" :image-size="120" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import { getRankings } from '@/api/shortlist'
import { getRegistrationReviewDetails } from '@/api/registration'
import { getAdminReviewTasks } from '@/api/admin'
import { getReviewScore } from '@/api/review'

// 赛事ID
const getCurrentCompetitionId = () => {
  return parseInt(localStorage.getItem('currentCompetitionId') || '21')
}
const competitionId = ref(getCurrentCompetitionId())

// 赛事阶段信息
const { stagesList } = useCompetitionStages()

// 配置
const config = ref({
  bookWeight: 50,
  interviewWeight: 50,
  ratioType: '30',
  customRatio: 30,
  minScore: null
})

// 筛选
const filters = ref({
  groupType: '',
  projectName: '',
  shortlistStatus: ''
})

// 数据
const projects = ref([])
const loading = ref(false)

// 详情
const detailDialogVisible = ref(false)
const selectedProject = ref(null)
const bookDetail = ref(null)
const interviewDetail = ref(null)
const bookReviewers = ref([])  // 书审评委详细评分
const interviewReviewers = ref([])  // 面谈评委详细评分
const detailLoading = ref(false)
const activeTab = ref('BOOK')

// 计算属性 - 筛选后的项目列表
const filteredProjects = computed(() => {
  let list = projects.value

  if (filters.value.groupType) {
    list = list.filter(p => p.groupType === filters.value.groupType)
  }

  if (filters.value.projectName) {
    const keyword = filters.value.projectName.toLowerCase()
    list = list.filter(p => p.projectName.toLowerCase().includes(keyword))
  }

  if (filters.value.shortlistStatus) {
    if (filters.value.shortlistStatus === 'shortlisted') {
      list = list.filter(p => p.isShortlisted)
    } else if (filters.value.shortlistStatus === 'not-shortlisted') {
      list = list.filter(p => !p.isShortlisted && p.compositeScore !== null)
    } else if (filters.value.shortlistStatus === 'pending-interview') {
      list = list.filter(p => p.compositeScore === null)
    }
  }

  return list
})

// 计算属性 - 有综合得分的项目（已完成书审和面谈）
const eligibleProjects = computed(() => {
  return projects.value.filter(p => p.compositeScore !== null)
})

// 计算属性 - 统计信息
const completedBookCount = computed(() => {
  return projects.value.filter(p => p.bookScore !== null).length
})

const completedInterviewCount = computed(() => {
  return projects.value.filter(p => p.interviewScore !== null).length
})

const shortlistedCount = computed(() => {
  return projects.value.filter(p => p.isShortlisted).length
})

const shortlistRatio = computed(() => {
  if (eligibleProjects.value.length === 0) return 0
  return ((shortlistedCount.value / eligibleProjects.value.length) * 100).toFixed(1)
})

const manualAddCount = computed(() => {
  return projects.value.filter(p => p.shortlistType === 'manual_add').length
})

const manualRemoveCount = computed(() => {
  return projects.value.filter(p => p.shortlistType === 'manual_remove').length
})

// 加载数据
async function loadData() {
  loading.value = true

  try {
    // 1. 获取书审排名
    const bookRes = await getRankings({
      competitionId: competitionId.value,
      stage: 'BOOK'
    })

    // 2. 获取面谈排名
    const interviewRes = await getRankings({
      competitionId: competitionId.value,
      stage: 'INTERVIEW'
    })

    if (bookRes.success && interviewRes.success) {
      // 3. 合并数据
      projects.value = mergeAndRank(bookRes.data || [], interviewRes.data || [])
      ElMessage.success(`加载成功，共 ${projects.value.length} 个项目`)
    } else {
      ElMessage.error('加载数据失败')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 合并书审和面谈数据，计算综合得分和排名
function mergeAndRank(bookData, interviewData) {
  // 创建项目映射
  const projectMap = new Map()

  // 添加书审数据
  bookData.forEach(item => {
    projectMap.set(item.registrationId, {
      registrationId: item.registrationId,
      projectName: item.projectName,
      institutionName: item.institutionName,
      groupType: item.groupType,
      bookScore: item.avgTotal,
      bookRank: item.rank,
      interviewScore: null,
      interviewRank: null,
      compositeScore: null,
      isShortlisted: false,
      shortlistType: null,
      rank: null
    })
  })

  // 添加面谈数据
  interviewData.forEach(item => {
    if (projectMap.has(item.registrationId)) {
      const project = projectMap.get(item.registrationId)
      project.interviewScore = item.avgTotal
      project.interviewRank = item.rank
    } else {
      // 只有面谈没有书审（理论上不应该发生）
      projectMap.set(item.registrationId, {
        registrationId: item.registrationId,
        projectName: item.projectName,
        institutionName: item.institutionName,
        groupType: item.groupType,
        bookScore: null,
        bookRank: null,
        interviewScore: item.avgTotal,
        interviewRank: item.rank,
        compositeScore: null,
        isShortlisted: false,
        shortlistType: null,
        rank: null
      })
    }
  })

  // 计算综合得分和状态
  const projectsList = Array.from(projectMap.values())
  projectsList.forEach(p => {
    // 情况1: 无书审，无面谈 -> 待书审
    if (p.bookScore === null && p.interviewScore === null) {
      p.compositeScore = null
      p.status = 'pending_book_review'
    }
    // 情况2: 有书审，无面谈
    else if (p.bookScore !== null && p.interviewScore === null) {
      // 基层组和综合组：只需书审
      if (p.groupType === 'BASIC' || p.groupType === 'COMPREHENSIVE') {
        p.compositeScore = p.bookScore
        p.status = 'completed'
      }
      // 进阶组：需要面谈
      else {
        p.compositeScore = null
        p.status = 'pending_interview'
      }
    }
    // 情况3: 有书审，有面谈 -> 计算综合得分
    else if (p.bookScore !== null && p.interviewScore !== null) {
      if (p.groupType === 'BASIC' || p.groupType === 'COMPREHENSIVE') {
        p.compositeScore = p.bookScore // 这些组不应该有面谈分
      } else {
        p.compositeScore =
          (p.bookScore * config.value.bookWeight / 100) +
          (p.interviewScore * config.value.interviewWeight / 100)
      }
      p.status = 'completed'
    }
    // 情况4: 无书审，有面谈 -> 待书审（异常情况）
    else if (p.bookScore === null && p.interviewScore !== null) {
      p.compositeScore = null
      p.status = 'pending_book_review'
    }
  })

  // 排序（综合得分降序，待面谈的排在后面）
  projectsList.sort((a, b) => {
    if (a.compositeScore === null && b.compositeScore === null) return 0
    if (a.compositeScore === null) return 1
    if (b.compositeScore === null) return -1
    return b.compositeScore - a.compositeScore
  })

  // 分配排名
  projectsList.forEach((p, index) => {
    if (p.compositeScore !== null) {
      p.rank = index + 1
    }
  })

  return projectsList
}

// 应用权重
function applyWeight() {
  if (config.value.bookWeight + config.value.interviewWeight !== 100) {
    ElMessage.warning('权重总和必须为100%')
    return
  }

  // 重新计算综合得分
  projects.value.forEach(p => {
    // 基层组和综合组：只需书审，不需面谈
    if (p.groupType === 'BASIC' || p.groupType === 'COMPREHENSIVE') {
      if (p.bookScore !== null) {
        p.compositeScore = p.bookScore
      }
    }
    // 进阶组：需要书审+面谈的加权平均
    else if (p.groupType === 'ADVANCED') {
      if (p.bookScore !== null && p.interviewScore !== null) {
        p.compositeScore =
          (p.bookScore * config.value.bookWeight / 100) +
          (p.interviewScore * config.value.interviewWeight / 100)
      }
    }
  })

  // 重新排序
  projects.value.sort((a, b) => {
    if (a.compositeScore === null && b.compositeScore === null) return 0
    if (a.compositeScore === null) return 1
    if (b.compositeScore === null) return -1
    return b.compositeScore - a.compositeScore
  })

  // 重新分配排名
  projects.value.forEach((p, index) => {
    if (p.compositeScore !== null) {
      p.rank = index + 1
    }
  })

  ElMessage.success('权重已应用，排名已更新')
}

// 处理入围比例变化
function handleRatioChange() {
  // 仅触发，不自动设置入围
}

// 批量设置入围
function batchSetShortlist() {
  const ratio = config.value.ratioType === 'custom'
    ? config.value.customRatio
    : parseInt(config.value.ratioType)

  let eligibleList = eligibleProjects.value

  // 应用最低分数线
  if (config.value.minScore !== null) {
    eligibleList = eligibleList.filter(p => p.compositeScore >= config.value.minScore)
  }

  const shortlistCount = Math.ceil(eligibleList.length * ratio / 100)

  ElMessageBox.confirm(
    `将按照${ratio}%的比例设置入围，共${shortlistCount}个项目。${config.value.minScore !== null ? `（最低分数线：${config.value.minScore}分）` : ''}是否继续？`,
    '确认批量设置入围',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 重置所有入围状态
    projects.value.forEach(p => {
      p.isShortlisted = false
      p.shortlistType = null
    })

    // 按排名设置前N名入围
    let count = 0
    for (const project of projects.value) {
      if (project.compositeScore !== null) {
        // 检查是否在eligible列表中
        if (eligibleList.includes(project) && count < shortlistCount) {
          project.isShortlisted = true
          project.shortlistType = 'auto'
          count++
        }
      }
    }

    ElMessage.success(`已设置前${shortlistCount}个项目入围`)
  }).catch(() => {
    ElMessage.info('已取消')
  })
}

// 切换入围状态（个别增补/取消）
function toggleShortlist(project, isAdd) {
  if (isAdd) {
    project.isShortlisted = true
    project.shortlistType = 'manual_add'
    ElMessage.success(`已增补入围：${project.projectName}`)
  } else {
    const originalType = project.shortlistType
    project.isShortlisted = false
    project.shortlistType = originalType === 'auto' ? 'manual_remove' : null
    ElMessage.info(`已取消入围：${project.projectName}`)
  }
}

// 加载评委详细评分（通过任务列表+评分接口）
async function loadReviewerScores(registrationId) {
  try {
    // 1. 获取书审任务列表
    const bookTasksRes = await getAdminReviewTasks({
      competitionId: competitionId.value,
      stage: 'BOOK'
    })
    
    if (bookTasksRes.success && bookTasksRes.data) {
      const allBookTasks = bookTasksRes.data
      // 筛选出当前项目的任务
      const projectBookTasks = allBookTasks.filter(t => t.registrationId === registrationId)
      
      // 2. 对每个已评分的任务，获取详细评分
      const bookScoresPromises = projectBookTasks
        .filter(task => task.status === 'SCORED')
        .map(async (task) => {
          try {
            const scoreRes = await getReviewScore(task.id)
            if (scoreRes.success && scoreRes.data) {
              return {
                reviewerId: task.reviewerId,
                reviewerName: task.reviewerName,
                reviewerTitle: task.reviewerTitle,
                reviewerInstitutionName: task.reviewerInstitutionName,
                reviewerInstitutionLevel: task.institutionLevel || '-',
                scores: {
                  plan: scoreRes.data.plan,
                  problem: scoreRes.data.problem,
                  action: scoreRes.data.action,
                  success: scoreRes.data.success,
                  review: scoreRes.data.review,
                  operation: scoreRes.data.operation,
                  presentation: scoreRes.data.presentation,
                  total: scoreRes.data.total
                },
                highlight: scoreRes.data.highlight,
                weakness: scoreRes.data.weakness,
                submittedAt: scoreRes.data.submittedAt
              }
            }
          } catch (err) {
            console.warn(`获取任务${task.id}的评分失败:`, err)
          }
          return null
        })
      
      const bookScores = await Promise.all(bookScoresPromises)
      bookReviewers.value = bookScores.filter(s => s !== null)
      console.log('✅ 加载书审评委详细评分:', bookReviewers.value.length, '位')
    }
    
    // 3. 获取面谈任务列表
    const interviewTasksRes = await getAdminReviewTasks({
      competitionId: competitionId.value,
      stage: 'INTERVIEW'
    })
    
    if (interviewTasksRes.success && interviewTasksRes.data) {
      const allInterviewTasks = interviewTasksRes.data
      const projectInterviewTasks = allInterviewTasks.filter(t => t.registrationId === registrationId)
      
      // 4. 对每个已评分的任务，获取详细评分
      const interviewScoresPromises = projectInterviewTasks
        .filter(task => task.status === 'SCORED')
        .map(async (task) => {
          try {
            const scoreRes = await getReviewScore(task.id)
            if (scoreRes.success && scoreRes.data) {
              return {
                reviewerId: task.reviewerId,
                reviewerName: task.reviewerName,
                reviewerTitle: task.reviewerTitle,
                reviewerInstitutionName: task.reviewerInstitutionName,
                reviewerInstitutionLevel: task.institutionLevel || '-',
                scores: {
                  plan: scoreRes.data.plan,
                  problem: scoreRes.data.problem,
                  action: scoreRes.data.action,
                  success: scoreRes.data.success,
                  review: scoreRes.data.review,
                  operation: scoreRes.data.operation,
                  presentation: scoreRes.data.presentation,
                  total: scoreRes.data.total
                },
                highlight: scoreRes.data.highlight,
                weakness: scoreRes.data.weakness,
                submittedAt: scoreRes.data.submittedAt
              }
            }
          } catch (err) {
            console.warn(`获取任务${task.id}的评分失败:`, err)
          }
          return null
        })
      
      const interviewScores = await Promise.all(interviewScoresPromises)
      interviewReviewers.value = interviewScores.filter(s => s !== null)
      console.log('✅ 加载面谈评委详细评分:', interviewReviewers.value.length, '位')
    }
    
  } catch (error) {
    console.error('❌ 加载评委详细评分失败:', error)
    bookReviewers.value = []
    interviewReviewers.value = []
  }
}

// 查看项目详情
async function viewDetail(project) {
  selectedProject.value = project
  detailDialogVisible.value = true
  detailLoading.value = true
  activeTab.value = 'BOOK'

  try {
    // 调用评审详情API获取汇总平均分
    const detailsResponse = await getRegistrationReviewDetails(project.registrationId)

    // 处理汇总平均分
    if (detailsResponse.success && detailsResponse.data) {
      const details = detailsResponse.data // data是一个数组
      
      // 查找书审和面谈的详情
      bookDetail.value = details.find(d => d.stage === 'BOOK') || {
        stage: 'BOOK',
        avgTotal: project.bookScore || 0,
        avgPlan: null,
        avgProblem: null,
        avgAction: null,
        avgSuccess: null,
        avgReview: null,
        avgOperation: null,
        avgPresentation: null,
        highlights: [],
        weaknesses: []
      }
      
      interviewDetail.value = details.find(d => d.stage === 'INTERVIEW') || {
        stage: 'INTERVIEW',
        avgTotal: project.interviewScore || 0,
        avgPlan: null,
        avgProblem: null,
        avgAction: null,
        avgSuccess: null,
        avgReview: null,
        avgOperation: null,
        avgPresentation: null,
        highlights: [],
        weaknesses: []
      }
    }

    // 获取评委详细评分（通过任务列表）
    await loadReviewerScores(project.registrationId)

  } catch (error) {
    console.error('加载详情失败:', error)
    ElMessage.error('加载详情失败')
  } finally {
    detailLoading.value = false
  }
}

// 导出入围名单
function exportList() {
  const csvContent = [
    ['综合排名', '项目名称', '医疗机构', '组别', '书审得分', '面谈得分', '综合得分', '入围状态'].join(','),
    ...projects.value.map(p => {
      let compositeScoreText = '-'
      if (p.compositeScore !== null) {
        compositeScoreText = p.compositeScore.toFixed(1)
      } else if (p.groupType === 'ADVANCED') {
        compositeScoreText = '待面谈'
      } else {
        compositeScoreText = '待评分'
      }
      
      return [
        p.rank || '-',
        p.projectName,
        p.institutionName,
        getGroupTypeLabel(p.groupType),
        p.bookScore !== null ? p.bookScore.toFixed(1) : '-',
        p.interviewScore !== null ? p.interviewScore.toFixed(1) : '-',
        compositeScoreText,
        getShortlistLabel(p)
      ].join(',')
    })
  ].join('\n')

  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `综合入围名单_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()

  ElMessage.success('导出成功')
}

// 辅助函数 - 组别标签
function getGroupTypeLabel(groupType) {
  const map = {
    'BASIC': '基层组',
    'ADVANCED': '进阶组',
    'COMPREHENSIVE': '综合组'
  }
  return map[groupType] || groupType
}

// 辅助函数 - 组别Tag类型
function getGroupTypeTagType(groupType) {
  const map = {
    'BASIC': '',
    'ADVANCED': 'success',
    'COMPREHENSIVE': 'warning'
  }
  return map[groupType] || ''
}

// 辅助函数 - 分数颜色
function getScoreColor(score) {
  if (!score) return '#909399'
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
}

// 辅助函数 - 排名Tag类型
function getRankTagType(rank) {
  if (rank === 1) return 'danger'
  if (rank === 2) return 'warning'
  if (rank === 3) return 'success'
  return ''
}

// 辅助函数 - 书审评分空状态提示
function getBookReviewEmptyText() {
  if (!selectedProject.value) return '暂无书审评分数据'
  
  // 检查项目状态
  if (selectedProject.value.status === 'pending_book_review') {
    return '⏳ 待书审评分，请等候'
  }
  
  return '暂无书审评分数据'
}

// 辅助函数 - 面谈评分空状态提示
function getInterviewEmptyText() {
  if (!selectedProject.value) return '暂无面谈评分数据'
  
  const groupType = selectedProject.value.groupType
  const status = selectedProject.value.status
  
  // 基层组和综合组不需要面谈
  if (groupType === 'BASIC' || groupType === 'COMPREHENSIVE') {
    return 'ℹ️ 该组别无需面谈评审'
  }
  
  // 进阶组待面谈
  if (status === 'pending_interview') {
    return '⏳ 待面谈评分，请等候'
  }
  
  return '暂无面谈评分数据'
}

// 辅助函数 - 入围状态标签
function getShortlistLabel(project) {
  if (project.isShortlisted) {
    if (project.shortlistType === 'manual_add') return '✅入围（增补）'
    return '✅入围'
  } else {
    if (project.shortlistType === 'manual_remove') return '❌未入围（取消）'
    
    // 根据状态显示不同标签
    if (project.status === 'pending_book_review') {
      return '⚠️待书审'
    }
    if (project.status === 'pending_interview' && project.groupType === 'ADVANCED') {
      return '⚠️待面谈'
    }
    
    return '❌未入围'
  }
}

// 辅助函数 - 入围状态Tag类型
function getShortlistTagType(project) {
  if (project.isShortlisted) return 'success'
  
  // 根据状态显示不同的标签类型
  if (project.status === 'pending_book_review' || project.status === 'pending_interview') {
    return 'warning'
  }
  
  return 'info'
}

// 辅助函数 - 行样式
function getRowClassName({ row }) {
  if (row.isShortlisted) {
    if (row.shortlistType === 'manual_add') return 'manual-add-row'
    return 'shortlisted-row'
  }
  if (row.shortlistType === 'manual_remove') return 'manual-remove-row'
  
  // 根据状态显示不同的行样式
  if (row.status === 'pending_book_review') return 'pending-book-review-row'
  if (row.status === 'pending_interview') return 'pending-row'
  
  return ''
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.shortlist-management {
  padding: 20px;
}

.config-card,
.filter-card,
.stats-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
}

.weight-config {
  display: flex;
  align-items: center;
}

.score-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
}

.score-label {
  font-size: 12px;
  color: #909399;
  margin-right: 8px;
}

.score-value {
  font-weight: bold;
  font-size: 15px;
}

.opinion-list {
  padding-left: 20px;
  line-height: 1.8;
}

.opinion-list li {
  margin-bottom: 10px;
}

/* 行样式 */
:deep(.shortlisted-row) {
  background-color: #e1f3d8 !important;
}

:deep(.manual-add-row) {
  background-color: #d9ecff !important;
}

:deep(.manual-remove-row) {
  background-color: #fef0f0 !important;
}

:deep(.pending-row) {
  background-color: #fdf6ec !important;
}

:deep(.pending-book-review-row) {
  background-color: #fef0f0 !important;
}

:deep(.detail-label) {
  font-weight: bold;
}
</style>
