<template>
  <div class="shortlist-management">
    <!-- 赛事进度条 -->
    <StageProgress :stages="stagesList" />

    <!-- 书审/面谈重叠时：切换入围操作场景（快照维度） -->
    <el-card class="shortlist-context-card" shadow="hover">
      <div class="context-switch-wrap">
        <div class="context-switch-head">
          <span class="context-switch-title">入围操作场景</span>
          <el-tag type="info" effect="plain" size="small">书审与面谈阶段切换</el-tag>
        </div>
        <el-radio-group
          v-model="rankStage"
          size="large"
          class="context-radio-group"
          @change="onRankStageChange"
        >
          <el-radio-button value="BOOK">书审入围</el-radio-button>
          <el-radio-button value="INTERVIEW">面谈入围</el-radio-button>
          <!-- 决赛入围暂不上线 -->
        </el-radio-group>
        <p class="context-hint">
          下方列表、统计、「计算排名」及增补/取消均针对<strong>当前场景</strong>的排名快照；
          书审入围与面谈入围数据相互独立，请分别计算、分别维护。
        </p>
      </div>
    </el-card>

    <!-- 入围规则与快照 -->
    <el-card class="config-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">入围规则与排名快照（{{ stageShortlistTitle }}）</span>
          <el-tag type="warning">coefficient 调整需先「计算排名」</el-tag>
        </div>
      </template>

      <el-form label-width="120px">
        <el-form-item label="当前场景">
          <span class="scene-current-value">{{ stageShortlistTitle }}</span>
          <el-button
            type="primary"
            :loading="computing"
            style="margin-left: 16px"
            @click="handleComputeRanking"
          >
            计算当前场景排名
          </el-button>
          <el-text type="info" style="margin-left: 12px" size="small">
            仅写入「{{ stageLabel }}」阶段快照，不影响其他阶段
          </el-text>
        </el-form-item>

        <el-form-item label="入围配置">
          <el-table v-loading="configLoading" :data="serverConfig" border size="small" style="width: 100%; max-width: 800px">
            <el-table-column label="组别" width="100">
              <template #default="{ row }">
                {{ getGroupTypeLabel(row.groupType) }}
              </template>
            </el-table-column>
            <el-table-column label="模式" width="150">
              <template #default="{ row }">
                <el-select v-model="row.mode" size="small" style="width: 130px">
                  <el-option label="按比例 (RATIO)" value="RATIO" />
                  <el-option label="取前N名 (COUNT)" value="COUNT" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="值" min-width="220">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.value"
                  :min="0"
                  :max="row.mode === 'RATIO' ? 1 : 9999"
                  :step="row.mode === 'RATIO' ? 0.01 : 1"
                  :precision="row.mode === 'RATIO' ? 2 : 0"
                  size="small"
                  style="width: 140px"
                />
                <span v-if="row.mode === 'RATIO'" style="margin-left: 8px; color: #909399; font-size: 12px">
                  如 0.55 表示 55%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="saveGroupConfig(row)">保存</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-text type="info" size="small" style="display: block; margin-top: 8px; line-height: 1.6">
            「取前 N 名」需对<strong>基层组、综合组、进阶组</strong>分别选 COUNT 并保存（例如基层前 3 名保存一行，综合前 3 名再保存一行）。
            保存后点<strong>刷新数据</strong>即可按新规则看到入围线；一般<strong>不必</strong>再点「计算排名」——除非尚未生成过调整分快照。
            「计算排名」会一次性计算当前阶段下<strong>各组别</strong>的调整分与排名快照（不传单组参数）。
          </el-text>
        </el-form-item>

        <el-form-item label="进阶组合分">
          <div v-loading="advancedConfigLoading" class="advanced-ranking-box">
            <p class="advanced-ranking-lead">
              面谈阶段<strong>进阶组</strong>合分：书审调整分与面谈调整分按权重合并。请先在此保存权重与模式，再按顺序计算书审快照 → 面谈快照。
            </p>
            <el-row :gutter="16" align="middle">
              <el-col :xs="24" :sm="8">
                <span class="inline-label">书审权重</span>
                <el-input-number
                  v-model="advancedRankingForm.bookWeight"
                  :min="0"
                  :max="1"
                  :step="0.05"
                  :precision="2"
                  style="width: 140px"
                />
              </el-col>
              <el-col :xs="24" :sm="8">
                <span class="inline-label">面谈权重</span>
                <el-input-number
                  v-model="advancedRankingForm.interviewWeight"
                  :min="0"
                  :max="1"
                  :step="0.05"
                  :precision="2"
                  style="width: 140px"
                />
              </el-col>
              <el-col :xs="24" :sm="8">
                <span class="inline-label">合分模式</span>
                <el-select v-model="advancedRankingForm.rankingMode" style="width: 100%; min-width: 200px">
                  <el-option
                    label="先调整后加权 ADJUST_THEN_WEIGHT（推荐）"
                    value="ADJUST_THEN_WEIGHT"
                  />
                  <el-option
                    label="先加权后整体调整 WEIGHT_THEN_ADJUST"
                    value="WEIGHT_THEN_ADJUST"
                  />
                </el-select>
              </el-col>
            </el-row>
            <div class="advanced-ranking-actions">
              <el-button
                type="primary"
                :loading="advancedConfigSaving"
                @click="handleSaveAdvancedRankingConfig"
              >
                保存进阶组合分配置
              </el-button>
              <el-text v-if="advancedWeightSumOk" type="success" size="small" style="margin-left: 12px">
                权重合计 = 1
              </el-text>
              <el-text v-else type="warning" size="small" style="margin-left: 12px">
                书审 + 面谈权重应等于 1
              </el-text>
            </div>
            <ol class="advanced-flow-ol">
              <li>保存本配置（PUT advanced-ranking-config）</li>
              <li>「书审入围」场景下「计算排名」stage=BOOK（先有书审调整分快照）</li>
              <li>切换到「面谈入围」并「计算排名」stage=INTERVIEW（进阶组合权分写入快照）</li>
              <li>在入围配置中为进阶组设 COUNT/RATIO 并保存</li>
              <li>GET shortlist stage=INTERVIEW 查看 withinLine / shortlisted</li>
            </ol>
            <el-text type="info" size="small" class="advanced-flow-note">
              若未先完成书审快照就算面谈，合分可能缺少书审调整分（后台可能回退，以日志为准）。
            </el-text>
          </div>
        </el-form-item>

        <el-alert
          title="基层/综合组可主要使用「书审入围」；进阶组在面谈进行时可切换到「面谈入围」单独操作。阶段重叠时请用顶部场景切换，避免误改另一阶段数据。"
          type="info"
          :closable="false"
          style="margin-bottom: 16px"
        />

        <el-form-item>
          <el-button type="primary" :loading="loading" icon="Refresh" @click="loadData">刷新数据</el-button>
          <el-button :disabled="projects.length === 0" icon="Download" @click="exportList">导出入围名单</el-button>
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
            @change="loadData"
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

    <!-- 统计信息：按组别分框 -->
    <el-card class="stats-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">入围统计（按组别）</span>
          <el-text v-if="snapshotTimeText" type="info" size="small">
            最近快照：{{ snapshotTimeText }}
          </el-text>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :xs="24" :lg="12">
          <div class="stats-segment-box stats-segment--plain">
            <div class="stats-segment-title">基层组 + 综合组</div>
            <div class="stat-grid">
              <div class="stat-cell">
                <div class="stat-label">总项目数</div>
                <div class="stat-value">{{ statsNonAdvanced.total }}</div>
              </div>
              <div class="stat-cell">
                <div class="stat-label">总入围数 & 比例</div>
                <div class="stat-value">
                  {{ statsNonAdvanced.shortlistedCount }}
                  <span class="stat-sub">({{ statsNonAdvanced.ratio }}%)</span>
                </div>
              </div>
              <div class="stat-cell">
                <div class="stat-label">增补入围</div>
                <div class="stat-value accent">{{ statsNonAdvanced.includeShortlistedCount }}</div>
                <div class="stat-hint">线内且曾强制增补</div>
              </div>
              <div class="stat-cell">
                <div class="stat-label">手动增补</div>
                <div class="stat-value warn">{{ statsNonAdvanced.manualAddCount }}</div>
                <div class="stat-hint">INCLUDE</div>
              </div>
              <div class="stat-cell">
                <div class="stat-label">手动取消</div>
                <div class="stat-value danger">{{ statsNonAdvanced.manualRemoveCount }}</div>
                <div class="stat-hint">EXCLUDE</div>
              </div>
            </div>
            <div class="stats-segment-foot">
              书审完成参考：{{ statsNonAdvanced.bookDone }} / {{ statsNonAdvanced.total }}
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :lg="12">
          <div class="stats-segment-box stats-segment--advanced">
            <div class="stats-segment-title">进阶组</div>
            <div class="stat-grid">
              <div class="stat-cell">
                <div class="stat-label">总项目数</div>
                <div class="stat-value">{{ statsAdvanced.total }}</div>
              </div>
              <div class="stat-cell">
                <div class="stat-label">总入围数 & 比例</div>
                <div class="stat-value">
                  {{ statsAdvanced.shortlistedCount }}
                  <span class="stat-sub">({{ statsAdvanced.ratio }}%)</span>
                </div>
              </div>
              <div class="stat-cell">
                <div class="stat-label">增补入围</div>
                <div class="stat-value accent">{{ statsAdvanced.includeShortlistedCount }}</div>
                <div class="stat-hint">线内且曾强制增补</div>
              </div>
              <div class="stat-cell">
                <div class="stat-label">手动增补</div>
                <div class="stat-value warn">{{ statsAdvanced.manualAddCount }}</div>
                <div class="stat-hint">INCLUDE</div>
              </div>
              <div class="stat-cell">
                <div class="stat-label">手动取消</div>
                <div class="stat-value danger">{{ statsAdvanced.manualRemoveCount }}</div>
                <div class="stat-hint">EXCLUDE</div>
              </div>
            </div>
            <div class="stats-segment-foot">
              书审 / 面谈完成参考：{{ statsAdvanced.bookDone }} / {{ statsAdvanced.interviewDone }} /
              {{ statsAdvanced.total }}
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 算法与业务规则（页内可见，不必仅依赖导出文件） -->
    <el-collapse v-model="ruleCollapseActive" class="rule-collapse-card">
      <el-collapse-item name="rules">
        <template #title>
          <span class="rule-collapse-title">评分调整与入围规则说明（An / B / Cn / D）</span>
          <el-tag size="small" type="success" effect="plain" style="margin-left: 8px">与下列列表列对应</el-tag>
        </template>
        <div class="rule-doc">
          <p class="rule-lead">
            为减少专家间差异、使不同小组项目可公平比较，大赛对<strong>专家打分后的项目平均分</strong>做系数调整后再排名、定入围。您可在<strong>本页列表</strong>直接看到原始分、系数与调整分；导出文件便于留档，并非唯一查看途径。
          </p>
          <ol class="rule-ol">
            <li>评分要求：专家以 <strong>80 分</strong>为基准，按标准上下加减分。</li>
            <li>
              以综合组为例：项目按约 25～30 个一组分为 N 个小组，每组由 2 位专家打分。在<strong>同一组别内</strong>：
              <ul class="rule-ul">
                <li>（1）<strong>An</strong>：该小组内各项目专家打分的平均分（小组均分）。</li>
                <li>（2）<strong>B</strong>：该<strong>组别内全部项目</strong>专家打分的平均分（全组均分）。</li>
                <li>（3）<strong>Cn = An ÷ B</strong>：该小组的系数（本页「系数」列）。</li>
                <li>
                  （4）<strong>D</strong>：某项目两位专家打分后的<strong>平均分</strong>除以该项目所在小组的 <strong>Cn</strong>，得到<strong>调整分</strong>（本页「调整分」）。再按 <strong>D</strong> 在该组别内排名，并结合入围比例确定入围名单。
                </li>
              </ul>
            </li>
            <li>
              <strong>去极值</strong>：计算 An、B 时，会去掉 <strong>65 分以下</strong>与 <strong>95 分以上</strong>的分数，减轻极端分对系数与调整分的影响（由后台在计算快照时执行）。
            </li>
          </ol>
          <p class="rule-map-title">本页列表列与符号对应：</p>
          <ul class="rule-map">
            <li><strong>原始均分</strong>：专家打分后的项目平均（参与调整前的量）。</li>
            <li><strong>调整分（D）</strong>：用于排名与入围线判断的调整后分数。</li>
            <li><strong>Cn</strong>：小组系数；<strong>小组/全组</strong>：An 与 B 的展示（An / B）。</li>
            <li><strong>排名</strong>：按当前阶段快照中调整分排序得到。</li>
            <li><strong>入围配置</strong>：下方各组比例或名额与后台规则共同决定入围范围（如 50%～60% 等，以实际配置为准）。</li>
          </ul>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- 项目列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">{{ stageShortlistTitle }} · 调整分与操作</span>
          <div>
            <el-tag type="info">快照阶段：{{ stageLabel }}</el-tag>
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
        <!-- 排名 irank -->
        <el-table-column width="90" align="center" fixed>
          <template #header>
            <span>排名</span>
            <el-tooltip
              placement="top"
              content="按当前阶段快照中的调整分（D）排序；需先「计算当前场景排名」生成快照。"
            >
              <el-icon class="col-header-tip"><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
          <template #default="{ row }">
            <el-tag
              v-if="row.irank && row.irank <= 3"
              :type="getRankTagType(row.irank)"
              effect="dark"
              size="large"
            >
              🏅 {{ row.irank }}
            </el-tag>
            <span v-else-if="row.irank != null" style="font-weight: bold; font-size: 16px">
              {{ row.irank }}
            </span>
            <span v-else style="color: #909399">-</span>
          </template>
        </el-table-column>

        <el-table-column width="150" align="center">
          <template #header>
            <span>原始/调整分</span>
            <el-tooltip placement="top">
              <template #content>
                <div style="max-width: 280px; line-height: 1.5">
                  <div>原始均分：专家对该项目的打分平均。</div>
                  <div>调整分（D）：原始均分 ÷ 小组系数 Cn，用于公平比较与排名。</div>
                </div>
              </template>
              <el-icon class="col-header-tip"><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
          <template #default="{ row }">
            <div class="score-detail">
              <div class="score-item">
                <span class="score-label">原始均分</span>
                <span class="score-value" :style="{ color: getScoreColor(row.rawAvg) }">
                  {{ row.rawAvg != null ? Number(row.rawAvg).toFixed(1) : '-' }}
                </span>
              </div>
              <div class="score-item">
                <span class="score-label">调整分</span>
                <span class="score-value" :style="{ color: getScoreColor(row.adjustedScore) }">
                  {{ row.adjustedScore != null ? Number(row.adjustedScore).toFixed(1) : '-' }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column width="150" align="center">
          <template #header>
            <span>系数/均值</span>
            <el-tooltip placement="top">
              <template #content>
                <div style="max-width: 300px; line-height: 1.5">
                  <div>Cn：小组系数，Cn = An÷B。</div>
                  <div>An：该小组均分；B：该组别全组均分（计算 An、B 时去掉 65 以下与 95 以上）。</div>
                </div>
              </template>
              <el-icon class="col-header-tip"><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
          <template #default="{ row }">
            <div class="score-detail">
              <div class="score-item">
                <span class="score-label">Cn</span>
                <span class="score-value">{{ row.coefficient != null ? Number(row.coefficient).toFixed(4) : '-' }}</span>
              </div>
              <div class="score-item">
                <span class="score-label">小组/全组</span>
                <span class="score-value" style="font-size: 12px">
                  {{ formatAnB(row.groupAvg, row.overallAvg) }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 书审/面谈参考（跨阶段汇总） -->
        <el-table-column label="书审/面谈" width="130" align="center">
          <template #default="{ row }">
            <div class="score-detail">
              <div class="score-item">
                <span class="score-label">书审</span>
                <span
                  class="score-value"
                  :style="{ color: getScoreColor(row.bookScore) }"
                >
                  {{ row.bookScore != null ? row.bookScore.toFixed(1) : '-' }}
                </span>
              </div>
              <div class="score-item">
                <span class="score-label">面谈</span>
                <span
                  class="score-value"
                  :style="{ color: getScoreColor(row.interviewScore) }"
                >
                  {{ row.interviewScore != null ? row.interviewScore.toFixed(1) : '-' }}
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

        <el-table-column label="入围线内" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.withinLine === true" type="success" size="small">是</el-tag>
            <el-tag v-else-if="row.withinLine === false" type="info" size="small">否</el-tag>
            <span v-else style="color: #909399">-</span>
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
        <el-table-column label="操作" width="260" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)" icon="View">查看详情</el-button>
            <el-button
              v-if="row.shortlistOverride"
              size="small"
              type="info"
              link
              @click="clearOverride(row)"
            >
              撤销人工
            </el-button>
            <el-button
              v-if="row.shortlisted"
              size="small"
              type="warning"
              @click="toggleShortlist(row, false)"
            >
              取消入围
            </el-button>
            <el-button
              v-else
              size="small"
              type="success"
              @click="toggleShortlist(row, true)"
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
          <el-descriptions-item label="排名" label-class-name="detail-label">
            <el-tag
              v-if="displayRank(selectedProject) && displayRank(selectedProject) <= 3"
              :type="getRankTagType(displayRank(selectedProject))"
              size="large"
            >
              第 {{ displayRank(selectedProject) }} 名
            </el-tag>
            <span v-else-if="displayRank(selectedProject)" style="font-size: 16px; font-weight: bold">
              第 {{ displayRank(selectedProject) }} 名
            </span>
            <span v-else style="color: #909399">-</span>
          </el-descriptions-item>
          <el-descriptions-item label="调整分" label-class-name="detail-label">
            <span
              v-if="selectedProject.adjustedScore != null"
              style="color: #409eff; font-size: 20px; font-weight: bold"
            >
              {{ Number(selectedProject.adjustedScore).toFixed(1) }} 分
            </span>
            <span v-else style="color: #909399">暂无快照</span>
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
                    <el-descriptions-item label="计划">{{ (reviewer.scores.plan || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="问题">{{ (reviewer.scores.problem || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="行动">{{ (reviewer.scores.action || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="成效">{{ (reviewer.scores.success || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="回顾">{{ (reviewer.scores.review || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="运作">{{ (reviewer.scores.operation || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="展示">{{ (reviewer.scores.presentation || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="总分">
                      <strong style="color: #409eff; font-size: 16px">{{ (reviewer.scores.total || 0).toFixed(1) }}分</strong>
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
                    <el-descriptions-item label="计划">{{ (reviewer.scores.plan || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="问题">{{ (reviewer.scores.problem || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="行动">{{ (reviewer.scores.action || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="成效">{{ (reviewer.scores.success || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="回顾">{{ (reviewer.scores.review || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="运作">{{ (reviewer.scores.operation || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="展示">{{ (reviewer.scores.presentation || 0).toFixed(1) }}分</el-descriptions-item>
                    <el-descriptions-item label="总分">
                      <strong style="color: #409eff; font-size: 16px">{{ (reviewer.scores.total || 0).toFixed(1) }}分</strong>
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
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, QuestionFilled } from '@element-plus/icons-vue'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import {
  getRankings,
  getAdminShortlist,
  getShortlistConfig,
  getAdvancedRankingConfig,
  saveAdvancedRankingConfig,
  saveShortlistConfig,
  computeRanking,
  setShortlistOverride,
  deleteShortlistOverride
} from '@/api/shortlist'
import { getRegistrationReviewDetails } from '@/api/registration'
import { getAdminReviewTasks } from '@/api/admin'
import { getReviewScore } from '@/api/review'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'

const competitionId = ref(getCurrentCompetitionIdSync())
const { stagesList } = useCompetitionStages()

/** 规则说明折叠面板，默认展开 */
const ruleCollapseActive = ref(['rules'])

/** 排名快照阶段：与后台 stage 一致 */
const rankStage = ref('BOOK')
const computing = ref(false)
const configLoading = ref(false)
const serverConfig = ref([])

/** 进阶组合分：与 GET/PUT advanced-ranking-config 对齐 */
const advancedConfigLoading = ref(false)
const advancedConfigSaving = ref(false)
const advancedRankingForm = reactive({
  bookWeight: 0.4,
  interviewWeight: 0.6,
  rankingMode: 'ADJUST_THEN_WEIGHT'
})

const advancedWeightSumOk = computed(() => {
  const s =
    Number(advancedRankingForm.bookWeight) +
    Number(advancedRankingForm.interviewWeight)
  return Math.abs(s - 1) <= 0.001
})

const filters = ref({
  groupType: '',
  projectName: '',
  shortlistStatus: ''
})

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

const stageLabel = computed(() => {
  const m = { BOOK: '书审', INTERVIEW: '面谈', FINAL: '决赛' }
  return m[rankStage.value] || rankStage.value
})

/** 顶部场景与表头文案：与 rankStage 一致 */
const stageShortlistTitle = computed(() => {
  const m = {
    BOOK: '书审入围',
    INTERVIEW: '面谈入围',
    FINAL: '决赛入围'
  }
  return m[rankStage.value] || '入围'
})

function onRankStageChange() {
  loadData()
}

const snapshotTimeText = computed(() => {
  const t = projects.value.map(p => p.calculatedAt).filter(Boolean)
  if (!t.length) return ''
  const latest = t.sort().slice(-1)[0]
  try {
    return new Date(latest).toLocaleString('zh-CN')
  } catch {
    return String(latest)
  }
})

const filteredProjects = computed(() => {
  let list = projects.value

  if (filters.value.groupType) {
    list = list.filter(p => p.groupType === filters.value.groupType)
  }

  if (filters.value.projectName) {
    const keyword = filters.value.projectName.toLowerCase()
    list = list.filter(p => (p.projectName || '').toLowerCase().includes(keyword))
  }

  if (filters.value.shortlistStatus) {
    if (filters.value.shortlistStatus === 'shortlisted') {
      list = list.filter(p => p.shortlisted)
    } else if (filters.value.shortlistStatus === 'not-shortlisted') {
      list = list.filter(p => !p.shortlisted && p.adjustedScore != null)
    } else if (filters.value.shortlistStatus === 'pending-interview') {
      list = list.filter(p => p.adjustedScore == null && p.rawAvg == null)
    }
  }

  return list
})

function buildSegmentStats(list) {
  const eligible = list.filter(p => p.adjustedScore != null)
  const shortlisted = list.filter(p => p.shortlisted)
  const manualAdd = list.filter(p => p.shortlistOverride === 'INCLUDE')
  const manualRemove = list.filter(p => p.shortlistOverride === 'EXCLUDE')
  const includeShortlisted = list.filter(
    p => p.shortlisted && p.shortlistOverride === 'INCLUDE'
  )
  const ratio =
    eligible.length > 0
      ? ((shortlisted.length / eligible.length) * 100).toFixed(1)
      : '0'
  return {
    total: list.length,
    shortlistedCount: shortlisted.length,
    ratio,
    includeShortlistedCount: includeShortlisted.length,
    manualAddCount: manualAdd.length,
    manualRemoveCount: manualRemove.length,
    bookDone: list.filter(p => p.bookScore != null).length,
    interviewDone: list.filter(p => p.interviewScore != null).length
  }
}

const statsNonAdvanced = computed(() => {
  const list = projects.value.filter(
    p => p.groupType === 'BASIC' || p.groupType === 'COMPREHENSIVE'
  )
  return buildSegmentStats(list)
})

const statsAdvanced = computed(() => {
  const list = projects.value.filter(p => p.groupType === 'ADVANCED')
  return buildSegmentStats(list)
})

function formatAnB(an, b) {
  if (an == null && b == null) return '-'
  const a = an != null ? Number(an).toFixed(1) : '-'
  const bb = b != null ? Number(b).toFixed(1) : '-'
  return `${a} / ${bb}`
}

function displayRank(project) {
  if (!project) return null
  return project.irank != null ? project.irank : project.rank
}

async function loadShortlistConfig() {
  configLoading.value = true
  try {
    const res = await getShortlistConfig()
    if (res.success && Array.isArray(res.data)) {
      serverConfig.value = res.data.map(r => ({ ...r }))
    }
  } catch (e) {
    console.error(e)
  } finally {
    configLoading.value = false
  }
}

async function loadAdvancedRankingConfig() {
  advancedConfigLoading.value = true
  try {
    const res = await getAdvancedRankingConfig()
    if (res.success && res.data) {
      const d = res.data
      if (d.bookWeight != null) {
        advancedRankingForm.bookWeight = Number(d.bookWeight)
      }
      if (d.interviewWeight != null) {
        advancedRankingForm.interviewWeight = Number(d.interviewWeight)
      }
      if (d.rankingMode) {
        advancedRankingForm.rankingMode = d.rankingMode
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    advancedConfigLoading.value = false
  }
}

async function handleSaveAdvancedRankingConfig() {
  const { bookWeight, interviewWeight, rankingMode } = advancedRankingForm
  if (
    bookWeight == null ||
    interviewWeight == null ||
    rankingMode == null ||
    rankingMode === ''
  ) {
    ElMessage.warning('书审权重、面谈权重、合分模式均为必填')
    return
  }
  if (Math.abs(Number(bookWeight) + Number(interviewWeight) - 1) > 0.001) {
    ElMessage.warning('书审权重与面谈权重之和应为 1')
    return
  }
  advancedConfigSaving.value = true
  try {
    const res = await saveAdvancedRankingConfig({
      bookWeight: Number(bookWeight),
      interviewWeight: Number(interviewWeight),
      rankingMode
    })
    if (res.success) {
      ElMessage.success('进阶组合分配置已保存')
      await loadAdvancedRankingConfig()
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    advancedConfigSaving.value = false
  }
}

async function saveGroupConfig(row) {
  try {
    const res = await saveShortlistConfig({
      groupType: row.groupType,
      mode: row.mode,
      value: row.value
    })
    if (res.success) {
      ElMessage.success('入围配置已保存，已刷新列表')
      await loadShortlistConfig()
      await loadData()
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function handleComputeRanking() {
  computing.value = true
  try {
    // 与后台约定：不传 groupType，一次计算当前 stage 下各组（如书审下基层+综合+进阶）的调整分与快照
    const body = {
      competitionId: competitionId.value,
      stage: rankStage.value
    }
    const res = await computeRanking(body)
    if (res.success) {
      ElMessage.success(
        typeof res.data === 'number'
          ? `排名计算完成，已写入 ${res.data} 条快照`
          : '排名计算完成'
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

function normalizeRow(item, bookMap, interviewMap) {
  const bookScore = bookMap.get(item.registrationId)
  const interviewScore = interviewMap.get(item.registrationId)
  let status = 'normal'
  if (bookScore == null && interviewScore == null) status = 'pending_book_review'
  else if (item.groupType === 'ADVANCED' && interviewScore == null) status = 'pending_interview'

  return {
    ...item,
    institutionLevel: item.institutionLevel,
    bookScore: bookScore ?? null,
    interviewScore: interviewScore ?? null,
    shortlistType:
      item.shortlistOverride === 'INCLUDE'
        ? 'manual_add'
        : item.shortlistOverride === 'EXCLUDE'
          ? 'manual_remove'
          : item.shortlisted
            ? 'auto'
            : null,
    status
  }
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      competitionId: competitionId.value,
      stage: rankStage.value
    }
    if (filters.value.groupType) {
      params.groupType = filters.value.groupType
    }

    const [slRes, bookRes, intRes] = await Promise.all([
      getAdminShortlist(params),
      getRankings({ competitionId: competitionId.value, stage: 'BOOK' }),
      getRankings({ competitionId: competitionId.value, stage: 'INTERVIEW' })
    ])

    const bookMap = new Map()
    if (bookRes.success && Array.isArray(bookRes.data)) {
      bookRes.data.forEach(r => {
        bookMap.set(r.registrationId, r.avgTotal != null ? Number(r.avgTotal) : null)
      })
    }
    const interviewMap = new Map()
    if (intRes.success && Array.isArray(intRes.data)) {
      intRes.data.forEach(r => {
        interviewMap.set(r.registrationId, r.avgTotal != null ? Number(r.avgTotal) : null)
      })
    }

    if (!slRes.success) {
      ElMessage.error(slRes.message || '加载入围名单失败')
      projects.value = []
      return
    }

    const rows = Array.isArray(slRes.data) ? slRes.data : []
    projects.value = rows.map(item => normalizeRow(item, bookMap, interviewMap))

    if (rows.length === 0) {
      ElMessage.warning('暂无入围快照数据，请先点击「计算排名」')
    } else {
      ElMessage.success(`加载成功，共 ${projects.value.length} 条`)
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function clearOverride(project) {
  try {
    await ElMessageBox.confirm('撤销后该项目按系统入围规则重新判定，是否继续？', '撤销人工干预', {
      type: 'warning'
    })
    const res = await deleteShortlistOverride(project.registrationId)
    if (res.success) {
      ElMessage.success('已撤销')
      await loadData()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch {
    /* cancel */
  }
}

async function toggleShortlist(project, isAdd) {
  try {
    if (isAdd) {
      await ElMessageBox.confirm(`确认将「${project.projectName}」增补为入围？`, '增补入围', {
        type: 'success'
      })
      const res = await setShortlistOverride({
        registrationId: project.registrationId,
        override: 'INCLUDE',
        note: '组委会增补'
      })
      if (res.success) {
        ElMessage.success('已增补')
        await loadData()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } else {
      await ElMessageBox.confirm(`确认取消「${project.projectName}」的入围资格？`, '取消入围', {
        type: 'warning'
      })
      const res = await setShortlistOverride({
        registrationId: project.registrationId,
        override: 'EXCLUDE',
        note: '组委会取消'
      })
      if (res.success) {
        ElMessage.success('已取消入围')
        await loadData()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    }
  } catch {
    /* cancel */
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

function exportList() {
  const csvContent = [
    [
      '排名',
      '项目名称',
      '医疗机构',
      '组别',
      '原始均分',
      '调整分',
      '书审参考',
      '面谈参考',
      '入围线内',
      '最终入围',
      '状态说明'
    ].join(','),
    ...filteredProjects.value.map(p => {
      return [
        p.irank != null ? p.irank : '-',
        p.projectName,
        p.institutionName,
        getGroupTypeLabel(p.groupType),
        p.rawAvg != null ? Number(p.rawAvg).toFixed(1) : '-',
        p.adjustedScore != null ? Number(p.adjustedScore).toFixed(1) : '-',
        p.bookScore != null ? p.bookScore.toFixed(1) : '-',
        p.interviewScore != null ? p.interviewScore.toFixed(1) : '-',
        p.withinLine === true ? '是' : p.withinLine === false ? '否' : '-',
        p.shortlisted ? '是' : '否',
        getShortlistLabel(p)
      ].join(',')
    })
  ].join('\n')

  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${stageShortlistTitle.value}_${rankStage.value}_${new Date().toISOString().slice(0, 10)}.csv`
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

function getShortlistLabel(project) {
  if (project.shortlisted) {
    if (project.shortlistOverride === 'INCLUDE') return '✅入围（增补）'
    return '✅入围'
  }
  if (project.shortlistOverride === 'EXCLUDE') return '❌未入围（强制）'
  if (project.status === 'pending_book_review') return '⚠️待书审'
  if (project.status === 'pending_interview' && project.groupType === 'ADVANCED') {
    return '⚠️待面谈'
  }
  return '❌未入围'
}

function getShortlistTagType(project) {
  if (project.shortlisted) return 'success'
  if (project.shortlistOverride === 'EXCLUDE') return 'danger'
  if (project.status === 'pending_book_review' || project.status === 'pending_interview') {
    return 'warning'
  }
  return 'info'
}

function getRowClassName({ row }) {
  if (row.shortlisted) {
    if (row.shortlistOverride === 'INCLUDE') return 'manual-add-row'
    return 'shortlisted-row'
  }
  if (row.shortlistOverride === 'EXCLUDE') return 'manual-remove-row'
  if (row.status === 'pending_book_review') return 'pending-book-review-row'
  if (row.status === 'pending_interview') return 'pending-row'
  return ''
}

onMounted(async () => {
  const currentCompetitionId = await getCurrentCompetitionId()
  if (currentCompetitionId) {
    competitionId.value = currentCompetitionId
  }
  await Promise.all([loadShortlistConfig(), loadAdvancedRankingConfig()])
  await loadData()
})
</script>

<style scoped>
.shortlist-management {
  padding: 20px;
}

.shortlist-context-card {
  margin-bottom: 20px;
  border: 1px solid var(--el-color-primary-light-5);
  background: linear-gradient(180deg, var(--el-color-primary-light-9) 0%, var(--el-bg-color) 48%);
}

.context-switch-wrap {
  padding: 4px 4px 0;
}

.context-switch-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.context-switch-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.context-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.context-radio-group :deep(.el-radio-button__inner) {
  min-width: 112px;
}

.context-hint {
  margin: 12px 0 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}

/* 「当前场景」与文案同一视觉层级，避免像按钮 */
.scene-current-value {
  font-size: 14px;
  font-weight: 400;
  color: var(--el-text-color-primary);
  line-height: 22px;
  vertical-align: middle;
}

.rule-collapse-card {
  margin-bottom: 20px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  overflow: hidden;
  --el-collapse-header-height: 48px;
}

.rule-collapse-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.rule-doc {
  font-size: 14px;
  color: var(--el-text-color-regular);
  line-height: 1.65;
  padding: 4px 8px 12px;
}

.rule-lead {
  margin: 0 0 12px;
}

.rule-ol {
  margin: 0 0 12px 1.2em;
  padding: 0;
}

.rule-ul {
  margin: 8px 0 0 1em;
}

.rule-map-title {
  font-weight: 600;
  margin: 12px 0 8px;
  color: var(--el-text-color-primary);
}

.rule-map {
  margin: 0;
  padding-left: 1.2em;
}

.col-header-tip {
  margin-left: 4px;
  vertical-align: -2px;
  cursor: help;
  color: var(--el-text-color-secondary);
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

/* 分组统计框 */
.stats-segment-box {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  padding: 14px 14px 10px;
  background: var(--el-fill-color-blank);
  height: 100%;
}

.stats-segment--plain {
  border-left: 4px solid var(--el-color-primary);
}

.stats-segment--advanced {
  border-left: 4px solid var(--el-color-success);
}

.stats-segment-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--el-text-color-primary);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}

@media (max-width: 1200px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.stat-cell {
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 10px 8px;
  text-align: center;
  min-height: 76px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.3;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1.2;
}

.stat-value.accent {
  color: var(--el-color-primary);
}

.stat-value.warn {
  color: var(--el-color-warning);
}

.stat-value.danger {
  color: var(--el-color-danger);
}

.stat-sub {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-secondary);
  margin-left: 2px;
}

.stat-hint {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
  margin-top: 4px;
  line-height: 1.2;
}

.stats-segment-foot {
  margin-top: 10px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.advanced-ranking-box {
  width: 100%;
  max-width: 960px;
  padding: 12px 14px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: var(--el-fill-color-blank);
}

.advanced-ranking-lead {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.5;
}

.advanced-ranking-box .inline-label {
  display: inline-block;
  margin-right: 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  vertical-align: middle;
}

.advanced-ranking-actions {
  margin-top: 14px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.advanced-flow-ol {
  margin: 12px 0 6px;
  padding-left: 1.25em;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.65;
}

.advanced-flow-note {
  display: block;
  margin-top: 4px;
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
