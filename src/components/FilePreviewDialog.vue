<template>
  <el-dialog
    v-model="visible"
    :title="title"
    fullscreen
    destroy-on-close
    @open="onOpen"
    @close="onClose"
  >
    <!-- 缩放工具栏（PDF / 图片 / DOCX / Excel 显示） -->
    <div
      v-if="!loading && !error && ['pdf','image','docx','excel'].includes(fileType)"
      class="zoom-toolbar"
    >
      <div class="zoom-controls">
        <el-tooltip content="缩小 (-)" placement="bottom">
          <el-button :icon="ZoomOut" circle size="small" @click="zoomOut" :disabled="zoomLevel <= 0.5" />
        </el-tooltip>
        <span class="zoom-label">{{ zoomPercent }}</span>
        <el-tooltip content="放大 (+)" placement="bottom">
          <el-button :icon="ZoomIn" circle size="small" @click="zoomIn" :disabled="zoomLevel >= 4" />
        </el-tooltip>
        <el-button size="small" @click="resetZoom" :disabled="zoomLevel === 1">重置</el-button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="preview-loading">
      <el-icon class="is-loading" :size="36"><Loading /></el-icon>
      <p>文件加载中…</p>
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="preview-error">
      <el-icon :size="40" color="#f56c6c"><WarningFilled /></el-icon>
      <p>{{ error }}</p>
      <el-button v-if="showDownload" type="primary" @click="triggerDownload">下载文件</el-button>
    </div>

    <!-- PDF：iframe + 缩放容器 -->
    <div v-else-if="fileType === 'pdf'" ref="pdfScrollRef" class="preview-pdf" @wheel.prevent="onWheel">
      <!-- 外壳按缩放比例撑大，产生正确的滚动区域 -->
      <div
        class="pdf-zoom-spacer"
        :style="{ width: `${zoomLevel * 100}%`, height: `${zoomLevel * 100}%` }"
      >
        <!-- iframe 保持原始尺寸（1/zoom），transform 放大内容 -->
        <iframe
          :src="showDownload ? blobUrl : blobUrl + '#toolbar=0&navpanes=0'"
          class="pdf-iframe"
          :style="{
            width: `${(1 / zoomLevel) * 100}%`,
            height: `${(1 / zoomLevel) * 100}%`,
            transform: `scale(${zoomLevel})`,
            transformOrigin: 'top left'
          }"
          frameborder="0"
        />
      </div>
    </div>

    <!-- 图片 -->
    <div v-else-if="fileType === 'image'" class="preview-image" @wheel.prevent="onWheel">
      <div class="zoom-scroll-area">
        <img
          :src="blobUrl"
          class="zoomable-img"
          :style="{ transform: `scale(${zoomLevel})` }"
        />
      </div>
    </div>

    <!-- DOCX：docx-preview 渲染 -->
    <div v-else-if="fileType === 'docx'" class="preview-docx" @wheel.prevent="onWheel">
      <div class="zoom-scroll-area">
        <div
          ref="docxContainer"
          class="docx-container"
          :style="{ transform: `scale(${zoomLevel})`, transformOrigin: 'top center' }"
        />
      </div>
    </div>

    <!-- XLSX / XLS：表格 -->
    <div v-else-if="fileType === 'excel'" class="preview-excel" @wheel.prevent="onWheel">
      <el-tabs v-model="activeSheet" v-if="excelSheets.length > 1">
        <el-tab-pane
          v-for="sheet in excelSheets"
          :key="sheet.name"
          :label="sheet.name"
          :name="sheet.name"
        />
      </el-tabs>
      <div class="zoom-scroll-area">
        <div
          class="excel-table-wrap"
          v-html="currentSheetHtml"
          :style="{ transform: `scale(${zoomLevel})`, transformOrigin: 'top left' }"
        />
      </div>
    </div>

    <!-- 不支持预览 -->
    <div v-else-if="fileType === 'unsupported'" class="preview-unsupported">
      <el-icon :size="48" color="#909399"><Document /></el-icon>
      <p style="margin:12px 0 4px; font-weight:600">{{ fileName }}</p>
      <p style="color:#909399; font-size:13px">该格式暂不支持在线预览</p>
      <el-button v-if="showDownload" type="primary" style="margin-top:16px" @click="triggerDownload">下载文件</el-button>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button v-if="showDownload" type="primary" :icon="Download" @click="triggerDownload">下载</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick, watchEffect } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, WarningFilled, Document, Download, ZoomIn, ZoomOut } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import { downloadMaterial } from '@/api/material'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  materialId: { type: [Number, String], default: null },
  fileUrl: { type: String, default: null },
  fileName: { type: String, default: '文件预览' },
  showDownload: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

// ── 状态 ──────────────────────────────────────────────────────────
const loading = ref(false)
const error = ref('')
const blobUrl = ref('')
const fileBlob = ref(null)
const docxContainer = ref(null)
const pdfScrollRef = ref(null)
const excelSheets = ref([])
const activeSheet = ref('')

// ── 缩放 ──────────────────────────────────────────────────────────
const zoomLevel = ref(1)
const zoomPercent = computed(() => `${Math.round(zoomLevel.value * 100)}%`)
const ZOOM_STEP = 0.25
const ZOOM_MIN = 0.5
const ZOOM_MAX = 4

function zoomIn() {
  zoomLevel.value = Math.min(ZOOM_MAX, +(zoomLevel.value + ZOOM_STEP).toFixed(2))
}
function zoomOut() {
  zoomLevel.value = Math.max(ZOOM_MIN, +(zoomLevel.value - ZOOM_STEP).toFixed(2))
}
function resetZoom() {
  zoomLevel.value = 1
}

function onWheel(e) {
  if (!e.ctrlKey && !e.metaKey) return
  e.preventDefault()
  if (e.deltaY < 0) zoomIn()
  else zoomOut()
}

// PDF 缩放后将水平滚动居中，确保可视区对准内容中央
watch(zoomLevel, async () => {
  if (fileType.value !== 'pdf') return
  await nextTick()
  if (pdfScrollRef.value) {
    const el = pdfScrollRef.value
    el.scrollLeft = (el.scrollWidth - el.clientWidth) / 2
  }
})

// ── 计算属性 ──────────────────────────────────────────────────────
const ext = computed(() => {
  if (!props.fileName) return ''
  return props.fileName.split('.').pop().toLowerCase()
})

const fileType = computed(() => {
  const e = ext.value
  if (e === 'pdf') return 'pdf'
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(e)) return 'image'
  if (e === 'docx') return 'docx'
  if (['xlsx', 'xls'].includes(e)) return 'excel'
  return 'unsupported'
})

const title = computed(() => props.fileName || '文件预览')

const dialogWidth = computed(() => {
  if (fileType.value === 'excel') return '90%'
  if (fileType.value === 'docx') return '860px'
  if (fileType.value === 'pdf') return '90%'
  return '640px'
})

const currentSheetHtml = computed(() => {
  const sheet = excelSheets.value.find(s => s.name === activeSheet.value)
  return sheet ? sheet.html : ''
})

// ── 加载文件 ──────────────────────────────────────────────────────
async function onOpen() {
  if (!props.materialId && !props.fileUrl) return
  loading.value = true
  error.value = ''
  blobUrl.value = ''
  fileBlob.value = null
  excelSheets.value = []
  zoomLevel.value = 1

  try {
    let blob
    if (props.fileUrl) {
      const resp = await fetch(props.fileUrl)
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      blob = await resp.blob()
    } else {
      blob = await downloadMaterial(props.materialId)
    }
    fileBlob.value = blob

    const mimeMap = {
      pdf: 'application/pdf',
      jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png',
      gif: 'image/gif', webp: 'image/webp', bmp: 'image/bmp', svg: 'image/svg+xml',
      docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      xls: 'application/vnd.ms-excel'
    }
    const mime = mimeMap[ext.value] || blob.type || 'application/octet-stream'
    const typedBlob = new Blob([blob], { type: mime })

    if (fileType.value === 'excel') {
      // Excel 数据解析不依赖 DOM，可以在 loading 关闭前完成
      await renderExcel(typedBlob)
      loading.value = false
    } else if (fileType.value === 'docx') {
      // 必须先关 loading，让 docxContainer div 进入 DOM，再调 renderAsync
      loading.value = false
      await nextTick()
      await renderDocx(typedBlob)
    } else {
      // PDF / 图片：先设 blobUrl，关 loading 后 iframe/img 自然渲染
      blobUrl.value = URL.createObjectURL(typedBlob)
      loading.value = false
    }
  } catch (e) {
    console.error('文件预览失败:', e)
    error.value = '文件加载失败，请稍后重试'
    loading.value = false
  }
}

async function renderDocx(blob) {
  // 动态 import，避免影响首屏加载
  const { renderAsync } = await import('docx-preview')
  await nextTick()
  if (!docxContainer.value) return
  docxContainer.value.innerHTML = ''
  await renderAsync(blob, docxContainer.value, null, {
    className: 'docx-render',
    inWrapper: true,
    ignoreWidth: false,
    ignoreHeight: true,
    ignoreFonts: false,
    breakPages: true,
    useBase64URL: true
  })
}

async function renderExcel(blob) {
  const arrayBuffer = await blob.arrayBuffer()
  const workbook = XLSX.read(arrayBuffer, { type: 'array' })
  excelSheets.value = workbook.SheetNames.map(name => ({
    name,
    html: XLSX.utils.sheet_to_html(workbook.Sheets[name], { header: '', footer: '' })
  }))
  activeSheet.value = workbook.SheetNames[0] || ''
}

// ── 下载 ──────────────────────────────────────────────────────────
async function triggerDownload() {
  try {
    const blob = fileBlob.value || await downloadMaterial(props.materialId)
    const url = URL.createObjectURL(new Blob([blob]))
    const a = document.createElement('a')
    a.href = url
    a.download = props.fileName || 'download'
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 3000)
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

// ── 清理 ──────────────────────────────────────────────────────────
function onClose() {
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value)
    blobUrl.value = ''
  }
  fileBlob.value = null
  excelSheets.value = []
  error.value = ''
  zoomLevel.value = 1
}
</script>

<style scoped lang="scss">
// ── 缩放工具栏 ──────────────────────────────────────────────────
.zoom-toolbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(4px);
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);

  .zoom-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .zoom-label {
    min-width: 48px;
    text-align: center;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
    color: #303133;
    user-select: none;
  }
}

// ── 通用可缩放滚动容器 ───────────────────────────────────────────
.zoom-scroll-area {
  overflow: auto;
  display: flex;
  justify-content: center;
}

.preview-loading,
.preview-error,
.preview-unsupported {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #606266;
}

.preview-pdf {
  height: calc(100vh - 160px);
  overflow: auto;

  .pdf-zoom-spacer {
    position: relative;
  }

  .pdf-iframe {
    display: block;
    position: absolute;
    top: 0;
    left: 0;
  }
}

.preview-image {
  height: calc(100vh - 160px);
  background: #f5f5f5;

  .zoom-scroll-area {
    height: 100%;
    align-items: flex-start;
    padding: 16px;
  }

  .zoomable-img {
    display: block;
    transform-origin: top center;
    transition: transform 0.15s ease;
    max-width: 100%;
    cursor: zoom-in;
  }
}

.preview-docx {
  height: calc(100vh - 160px);
  background: #f5f5f5;
  padding: 12px;

  .zoom-scroll-area {
    min-height: 100%;
    align-items: flex-start;
  }

  .docx-container {
    transition: transform 0.15s ease;
  }

  :deep(.docx-render) {
    background: #fff;
    box-shadow: 0 2px 8px rgba(0,0,0,.12);
    margin: 0 auto;
    padding: 40px 60px;
  }
}

.preview-excel {
  height: calc(100vh - 160px);
  overflow: hidden;
  display: flex;
  flex-direction: column;

  .zoom-scroll-area {
    flex: 1;
    overflow: auto;
    justify-content: flex-start;
    align-items: flex-start;
  }

  .excel-table-wrap {
    transition: transform 0.15s ease;
    :deep(table) {
      border-collapse: collapse;
      font-size: 13px;
      width: 100%;
    }
    :deep(td), :deep(th) {
      border: 1px solid #e4e7ed;
      padding: 4px 8px;
      white-space: nowrap;
    }
    :deep(tr:nth-child(even)) {
      background: #fafafa;
    }
  }
}
</style>
