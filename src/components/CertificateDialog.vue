<template>
  <el-dialog
    v-model="visible"
    title="奖状预览"
    width="860px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div class="cert-toolbar">
      <el-radio-group v-model="layout" size="small" style="margin-right: 12px">
        <el-radio-button value="landscape">横版 A4</el-radio-button>
        <el-radio-button value="portrait">竖版 A4</el-radio-button>
      </el-radio-group>
      <el-button type="primary" :icon="Printer" @click="printCert">打印 / 保存为 PDF</el-button>
      <span style="color:#909399;font-size:12px;margin-left:8px">打印时选择"另存为PDF"即可下载</span>
    </div>

    <!-- 证书预览区 -->
    <div class="cert-preview-wrap" :class="layout">
      <div id="cert-print-area" class="cert-paper" :class="[layout, awardClass]">
        <!-- 四角装饰 -->
        <div class="corner tl"></div>
        <div class="corner tr"></div>
        <div class="corner bl"></div>
        <div class="corner br"></div>

        <!-- 边框内容 -->
        <div class="cert-inner">
          <!-- 顶部赛事标题 -->
          <div class="cert-event">{{ competitionName }}</div>

          <!-- 主标题 -->
          <div class="cert-title">荣&nbsp;&nbsp;誉&nbsp;&nbsp;证&nbsp;&nbsp;书</div>

          <!-- 副标题装饰线 -->
          <div class="cert-divider">
            <span class="line"></span>
            <span class="diamond">◆</span>
            <span class="line"></span>
          </div>

          <!-- 颁奖正文 -->
          <div class="cert-body">
            <span class="cert-institution">{{ data.institutionName }}</span>
            <span class="cert-plain">参赛项目</span>
          </div>
          <div class="cert-project">「{{ data.projectName }}」</div>
          <div class="cert-body">
            <span class="cert-plain">在本届大赛</span>
            <span class="cert-group">{{ groupLabel }}</span>
            <span class="cert-plain">中荣获</span>
          </div>
          <div class="cert-award" :class="awardClass">{{ awardLabel }}</div>

          <!-- 落款 -->
          <div class="cert-footer">
            <div class="cert-org">浙江省品管大赛组委会</div>
            <div class="cert-date">{{ certYear }} 年</div>
          </div>

          <!-- 印章 -->
          <div class="cert-seal" :class="awardClass">
            <span class="seal-text">大赛组委会</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量模式：奖项列表 -->
    <div v-if="batch && awardedList.length > 1" class="batch-list">
      <div class="batch-hint">共 {{ awardedList.length }} 张奖状，点击切换预览</div>
      <div class="batch-items">
        <el-tag
          v-for="(item, i) in awardedList"
          :key="i"
          :type="i === currentIndex ? 'primary' : ''"
          class="batch-tag"
          style="cursor:pointer;margin:4px"
          @click="currentIndex = i"
        >
          {{ awardLabelMap[item.awardLevel] }} · {{ item.institutionName?.slice(0, 8) }}
        </el-tag>
      </div>
      <div style="margin-top:8px">
        <el-button size="small" :disabled="currentIndex === 0" @click="currentIndex--">上一张</el-button>
        <el-button size="small" :disabled="currentIndex >= awardedList.length - 1" @click="currentIndex++">下一张</el-button>
        <el-button type="warning" size="small" style="margin-left:12px" @click="printAll">逐一打印全部（{{ awardedList.length }}张）</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Printer } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  // 单张模式传 row，批量传 list
  row: { type: Object, default: null },
  list: { type: Array, default: () => [] },
  competitionName: { type: String, default: '浙江省医院品管大赛' }
})
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})

const layout = ref('landscape')
const currentIndex = ref(0)

const batch = computed(() => props.list && props.list.length > 0)
const awardedList = computed(() => {
  if (batch.value) return props.list.filter(r => r.awardLevel)
  return props.row ? [props.row] : []
})

const data = computed(() => awardedList.value[currentIndex.value] || {})

watch(() => props.modelValue, v => { if (v) currentIndex.value = 0 })

const awardLabelMap = {
  GOLD: '金奖',
  SILVER: '银奖',
  BRONZE: '铜奖'
}
const awardLabel = computed(() => awardLabelMap[data.value.awardLevel] || '佳作奖')
const awardClass = computed(() => {
  const m = { GOLD: 'gold', SILVER: 'silver', BRONZE: 'bronze', MERIT: 'merit' }
  return m[data.value.awardLevel] || 'merit'
})

const groupLabelMap = {
  BASIC: '基层组',
  COMPREHENSIVE: '综合组',
  ADVANCED: '进阶组'
}
const groupLabel = computed(() => groupLabelMap[data.value.groupType] || data.value.groupType || '')
const certYear = new Date().getFullYear()

// ── 打印 ──────────────────────────────────────────────
function printCert() {
  const area = document.getElementById('cert-print-area')
  if (!area) return
  const win = window.open('', '_blank', 'width=1100,height=820')
  win.document.write(`
    <html><head>
      <title>${data.value.institutionName}—${awardLabel.value}</title>
      <style>
        @page { size: ${layout.value === 'landscape' ? 'A4 landscape' : 'A4 portrait'}; margin: 0; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center; }
        ${getCertStyles()}
      </style>
    </head><body>
      ${area.outerHTML}
    </body></html>
  `)
  win.document.close()
  win.focus()
  setTimeout(() => { win.print(); win.close() }, 400)
}

async function printAll() {
  for (let i = 0; i < awardedList.value.length; i++) {
    currentIndex.value = i
    await new Promise(r => setTimeout(r, 200))
    printCert()
    await new Promise(r => setTimeout(r, 600))
  }
}

function getCertStyles() {
  return `
    .cert-paper {
      position: relative;
      width: ${layout.value === 'landscape' ? '270mm' : '185mm'};
      height: ${layout.value === 'landscape' ? '180mm' : '265mm'};
      background: #fffdf5;
      border: 6px solid #c8a84b;
      display: flex; align-items: stretch;
      font-family: "Noto Serif SC", "SimSun", serif;
    }
    .cert-paper.gold { border-color: #c8a84b; }
    .cert-paper.silver { border-color: #8c9eb0; }
    .cert-paper.bronze { border-color: #b87333; }
    .cert-paper.merit { border-color: #7e9e6a; }
    .corner { position:absolute; width:22px; height:22px; }
    .corner.tl { top:-3px; left:-3px; border-top:5px solid; border-left:5px solid; }
    .corner.tr { top:-3px; right:-3px; border-top:5px solid; border-right:5px solid; }
    .corner.bl { bottom:-3px; left:-3px; border-bottom:5px solid; border-left:5px solid; }
    .corner.br { bottom:-3px; right:-3px; border-bottom:5px solid; border-right:5px solid; }
    .gold .corner { border-color: #f5c842; }
    .silver .corner { border-color: #b0c4de; }
    .bronze .corner { border-color: #cd7f32; }
    .merit .corner { border-color: #7e9e6a; }
    .cert-inner { flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:20px 32px; gap:10px; }
    .cert-event { font-size:13px; color:#888; letter-spacing:3px; }
    .cert-title { font-size:38px; font-weight:700; letter-spacing:8px; color:#8b1a1a; text-shadow:1px 1px 2px rgba(0,0,0,.1); }
    .cert-divider { display:flex; align-items:center; gap:10px; width:60%; }
    .cert-divider .line { flex:1; height:1px; background:currentColor; opacity:.3; }
    .cert-divider .diamond { font-size:10px; color:#c8a84b; }
    .cert-body { font-size:16px; color:#333; line-height:2; }
    .cert-institution { font-size:20px; font-weight:700; color:#1a1a1a; border-bottom:2px solid #c8a84b; padding:0 4px; }
    .cert-plain { font-size:16px; color:#333; }
    .cert-group { font-size:16px; font-weight:600; color:#555; padding:0 4px; }
    .cert-project { font-size:17px; font-weight:600; color:#2c3e50; text-align:center; line-height:1.6; max-width:80%; }
    .cert-award { font-size:42px; font-weight:900; letter-spacing:4px; margin:4px 0; }
    .cert-award.gold { color:#c8a84b; text-shadow:1px 2px 4px rgba(200,168,75,.4); }
    .cert-award.silver { color:#8c9eb0; }
    .cert-award.bronze { color:#b87333; }
    .cert-award.merit { color:#5a7a4a; font-size:30px; }
    .cert-footer { display:flex; justify-content:space-between; width:100%; margin-top:12px; font-size:13px; color:#555; }
    .cert-seal { position:absolute; bottom:20px; right:28px; width:72px; height:72px; border-radius:50%; border:3px solid; display:flex; align-items:center; justify-content:center; opacity:.65; transform:rotate(-8deg); }
    .cert-seal .seal-text { font-size:10px; text-align:center; line-height:1.4; font-weight:600; }
    .cert-seal.gold { border-color:#c8a84b; color:#c8a84b; }
    .cert-seal.silver { border-color:#8c9eb0; color:#8c9eb0; }
    .cert-seal.bronze { border-color:#b87333; color:#b87333; }
    .cert-seal.merit { border-color:#7e9e6a; color:#7e9e6a; }
  `
}
</script>

<style scoped lang="scss">
.cert-toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.cert-preview-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #e8e8e8;
  border-radius: 6px;
  padding: 24px;
  min-height: 340px;

  &.landscape { min-height: 380px; }
  &.portrait { min-height: 480px; }
}

.cert-paper {
  position: relative;
  background: #fffdf5;
  border: 6px solid #c8a84b;
  display: flex;
  align-items: stretch;
  font-family: "Noto Serif SC", "SimSun", serif;
  box-shadow: 0 8px 32px rgba(0,0,0,.18);
  transition: border-color .3s;

  &.landscape { width: 680px; height: 460px; }
  &.portrait  { width: 480px; height: 640px; }

  &.gold   { border-color: #c8a84b; }
  &.silver { border-color: #8c9eb0; }
  &.bronze { border-color: #b87333; }
  &.merit  { border-color: #7e9e6a; }
}

.corner {
  position: absolute;
  width: 22px;
  height: 22px;
  &.tl { top: -3px; left: -3px; border-top: 4px solid; border-left: 4px solid; }
  &.tr { top: -3px; right: -3px; border-top: 4px solid; border-right: 4px solid; }
  &.bl { bottom: -3px; left: -3px; border-bottom: 4px solid; border-left: 4px solid; }
  &.br { bottom: -3px; right: -3px; border-bottom: 4px solid; border-right: 4px solid; }
}
.gold .corner   { border-color: #f5c842; }
.silver .corner { border-color: #b0c4de; }
.bronze .corner { border-color: #cd7f32; }
.merit .corner  { border-color: #7e9e6a; }

.cert-inner {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 36px;
  gap: 8px;
}

.cert-event {
  font-size: 12px;
  color: #888;
  letter-spacing: 3px;
}

.cert-title {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: 8px;
  color: #8b1a1a;
  text-shadow: 1px 1px 2px rgba(0,0,0,.08);
}

.cert-divider {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 60%;
  .line { flex: 1; height: 1px; background: #c8a84b; opacity: .4; }
  .diamond { font-size: 10px; color: #c8a84b; }
}

.cert-body {
  font-size: 15px;
  color: #333;
  line-height: 2;
  display: flex;
  align-items: baseline;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: center;
}
.cert-institution {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  border-bottom: 2px solid #c8a84b;
  padding: 0 4px;
}
.cert-plain { font-size: 15px; color: #333; }
.cert-group { font-size: 15px; font-weight: 600; color: #555; }

.cert-project {
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  text-align: center;
  line-height: 1.6;
  max-width: 90%;
}

.cert-award {
  font-size: 38px;
  font-weight: 900;
  letter-spacing: 4px;
  margin: 2px 0;
  &.gold   { color: #c8a84b; text-shadow: 1px 2px 6px rgba(200,168,75,.35); }
  &.silver { color: #8c9eb0; }
  &.bronze { color: #b87333; }
  &.merit  { color: #5a7a4a; font-size: 26px; }
}

.cert-footer {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 8px;
  font-size: 12px;
  color: #555;
}

.cert-seal {
  position: absolute;
  bottom: 18px;
  right: 24px;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 3px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: .6;
  transform: rotate(-8deg);
  .seal-text { font-size: 9px; text-align: center; line-height: 1.5; font-weight: 600; }
  &.gold   { border-color: #c8a84b; color: #c8a84b; }
  &.silver { border-color: #8c9eb0; color: #8c9eb0; }
  &.bronze { border-color: #b87333; color: #b87333; }
  &.merit  { border-color: #7e9e6a; color: #7e9e6a; }
}

.batch-list {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #eee;
  .batch-hint { font-size: 13px; color: #666; margin-bottom: 6px; }
  .batch-items { display: flex; flex-wrap: wrap; }
}
</style>
