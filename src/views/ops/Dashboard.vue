<template>
  <div class="ops-dashboard">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统管理</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" @click="goTo('/ops/institutions')">
            <div class="menu-card">
              <el-icon :size="48" color="#409EFF"><OfficeBuilding /></el-icon>
              <h3>机构管理</h3>
              <p>管理医疗机构信息</p>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" @click="goTo('/ops/dictionaries')">
            <div class="menu-card">
              <el-icon :size="48" color="#67C23A"><Document /></el-icon>
              <h3>字典管理</h3>
              <p>管理系统字典配置</p>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" @click="goTo('/ops/datasource')">
            <div class="menu-card">
              <el-icon :size="48" color="#E6A23C"><Connection /></el-icon>
              <h3>数据源管理</h3>
              <p>切换测试数据库</p>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" @click="goTo('/ops/settings')">
            <div class="menu-card">
              <el-icon :size="48" color="#F56C6C"><Setting /></el-icon>
              <h3>系统设置</h3>
              <p>配置系统参数</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goTo = (path) => {
  router.push(path)
}
</script>

<style scoped lang="scss">
.ops-dashboard {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
  
  .menu-card {
    text-align: center;
    cursor: pointer;
    padding: 20px;
    
    h3 {
      margin: 16px 0 8px 0;
      font-size: 18px;
    }
    
    p {
      margin: 0;
      color: #999;
      font-size: 14px;
    }
  }
}
</style>
