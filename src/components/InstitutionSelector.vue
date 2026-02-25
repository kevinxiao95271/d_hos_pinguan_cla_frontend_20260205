<template>
  <div class="institution-selector">
    <!-- 快速选择城市 -->
    <div v-if="cities.length && !filters.city" class="city-selection">
      <div class="section-title">选择城市</div>
      <div class="city-tags">
        <el-tag
          v-for="city in cities"
          :key="city"
          @click="selectCity(city)"
          class="city-tag"
          effect="plain"
          size="large"
        >
          {{ city }}
        </el-tag>
      </div>
    </div>

    <!-- 筛选器 -->
    <el-form :inline="true" class="filter-form">
      <el-form-item label="城市">
        <el-select
          v-model="filters.city"
          placeholder="选择城市"
          clearable
          @change="handleCityChange"
          style="width: 150px"
        >
          <el-option
            v-for="city in cities"
            :key="city"
            :label="city"
            :value="city"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="区县" v-if="filters.city">
        <el-select
          v-model="filters.district"
          placeholder="选择区县（可选）"
          clearable
          @change="handleFilterChange"
          style="width: 150px"
        >
          <el-option
            v-for="district in districts"
            :key="district"
            :label="district"
            :value="district"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="等级">
        <el-select
          v-model="filters.level"
          placeholder="选择等级"
          clearable
          @change="handleFilterChange"
          style="width: 150px"
        >
          <el-option
            v-for="level in allLevels"
            :key="level"
            :label="level"
            :value="level"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="关键词">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索机构名称"
          clearable
          @input="debouncedSearch"
          style="width: 250px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </el-form-item>
    </el-form>

    <!-- 搜索结果列表 -->
    <div v-loading="loading" class="results-container">
      <el-empty v-if="!loading && institutions.length === 0" description="暂无数据" />
      
      <div v-else class="institution-list">
        <div
          v-for="inst in institutions"
          :key="inst.id"
          class="institution-item"
          :class="{ selected: selectedInstitution?.id === inst.id }"
          @click="selectInstitution(inst)"
        >
          <div class="inst-name">{{ inst.name }}</div>
          <div class="inst-meta">
            <el-tag size="small" type="info">{{ inst.region }}</el-tag>
            <el-tag v-if="inst.level" size="small" type="success">{{ inst.level }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        class="pagination"
      />
    </div>

    <!-- 已选择的机构 -->
    <div v-if="selectedInstitution" class="selected-institution">
      <div class="selected-title">已选择机构：</div>
      <el-tag type="success" size="large" closable @close="clearSelection">
        {{ selectedInstitution.displayText || selectedInstitution.name }}
      </el-tag>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { searchInstitutions, getCities, getDistricts, getAllLevels } from '@/api/institution'

const emit = defineEmits(['select'])

// 简单的debounce实现
function debounce(fn, delay) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

// 筛选条件
const filters = reactive({
  city: '',
  district: '',
  level: '',
  keyword: ''
})

// 数据
const cities = ref([])
const districts = ref([])
const allLevels = ref([])
const institutions = ref([])
const selectedInstitution = ref(null)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)

// 选择城市
const selectCity = (city) => {
  filters.city = city
  filters.district = ''
  districts.value = []
  currentPage.value = 1
  loadDistricts(city)
  loadInstitutions()
}

// 城市变更
const handleCityChange = () => {
  filters.district = ''
  districts.value = []
  if (filters.city) {
    loadDistricts(filters.city)
  }
  currentPage.value = 1
  loadInstitutions()
}

// 筛选条件变化
const handleFilterChange = () => {
  currentPage.value = 1
  loadInstitutions()
}

// 防抖搜索
const debouncedSearch = debounce(() => {
  currentPage.value = 1
  loadInstitutions()
}, 500)

// 分页变化
const handlePageChange = () => {
  loadInstitutions()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadInstitutions()
}

// 加载区县列表
const loadDistricts = async (city) => {
  try {
    const res = await getDistricts(city)
    if (res.success) {
      districts.value = res.data
    }
  } catch (error) {
    console.error('加载区县列表失败:', error)
  }
}

// 加载机构列表
const loadInstitutions = async () => {
  loading.value = true
  try {
    // 根据优先级确定region参数：区县 > 城市
    let region = null
    if (filters.district) {
      region = filters.district
    } else if (filters.city) {
      region = filters.city
    }

    const params = {
      keyword: filters.keyword || null,
      region: region,
      level: filters.level || null,
      page: currentPage.value - 1,
      size: pageSize.value
    }

    const res = await searchInstitutions(params)
    if (res.success) {
      institutions.value = res.data.content
      total.value = res.data.totalElements
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 选择机构
const selectInstitution = (inst) => {
  selectedInstitution.value = inst
  emit('select', inst)
}

// 清除选择
const clearSelection = () => {
  selectedInstitution.value = null
  emit('select', null)
}

// 初始化
onMounted(async () => {
  try {
    // 并行加载所有初始数据
    const [citiesRes, levelsRes] = await Promise.all([
      getCities(),
      getAllLevels()
    ])

    if (citiesRes.success) {
      cities.value = citiesRes.data
    }
    if (levelsRes.success) {
      allLevels.value = levelsRes.data
    }

    // 加载初始机构列表
    loadInstitutions()
  } catch (error) {
    console.error('初始化失败:', error)
  }
})
</script>

<style scoped lang="scss">
.institution-selector {
  .city-selection {
    margin-bottom: 20px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;

    .section-title {
      font-size: 14px;
      font-weight: 600;
      color: #333;
      margin-bottom: 12px;
    }

    .city-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;

      .city-tag {
        cursor: pointer;
        transition: all 0.3s;
        font-size: 14px;

        &:hover {
          transform: scale(1.05);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
      }
    }
  }

  .filter-form {
    margin-bottom: 20px;
    padding: 16px;
    background: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
  }

  .results-container {
    min-height: 400px;
    padding: 16px;
    background: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 8px;

    .institution-list {
      margin-bottom: 16px;

      .institution-item {
        padding: 16px;
        border: 1px solid #e4e7ed;
        border-radius: 6px;
        margin-bottom: 12px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
          transform: translateY(-2px);
        }

        &.selected {
          border-color: #67c23a;
          background: #f0f9ff;
        }

        .inst-name {
          font-size: 16px;
          font-weight: 500;
          color: #333;
          margin-bottom: 8px;
        }

        .inst-meta {
          display: flex;
          gap: 8px;
        }
      }
    }

    .pagination {
      margin-top: 16px;
      display: flex;
      justify-content: center;
    }
  }

  .selected-institution {
    margin-top: 20px;
    padding: 16px;
    background: #f0f9ff;
    border: 1px solid #409eff;
    border-radius: 8px;

    .selected-title {
      font-size: 14px;
      font-weight: 600;
      color: #333;
      margin-bottom: 8px;
    }
  }
}
</style>
