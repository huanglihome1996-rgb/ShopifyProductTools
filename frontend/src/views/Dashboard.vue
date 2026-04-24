<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #409EFF;">
            <el-icon :size="32"><Shop /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.storeCount }}</div>
            <div class="stat-label">店铺数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #67C23A;">
            <el-icon :size="32"><Goods /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.productCount }}</div>
            <div class="stat-label">产品总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #E6A23C;">
            <el-icon :size="32"><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pendingCount }}</div>
            <div class="stat-label">待处理</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #F56C6C;">
            <el-icon :size="32"><Upload /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.uploadedCount }}</div>
            <div class="stat-label">已上传</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card class="section-card" header="快捷操作">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-button type="primary" size="large" @click="$router.push('/import')">
            <el-icon><Upload /></el-icon>
            导入产品
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="success" size="large" @click="$router.push('/optimize')">
            <el-icon><MagicStick /></el-icon>
            AI优化
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="warning" size="large" @click="$router.push('/stores')">
            <el-icon><Shop /></el-icon>
            添加店铺
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button size="large" @click="$router.push('/history')">
            <el-icon><Clock /></el-icon>
            查看历史
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 最近操作 -->
    <el-card class="section-card" header="最近操作">
      <el-table :data="recentOperations" stripe>
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeApi, productApi } from '@/api'

const stats = ref({
  storeCount: 0,
  productCount: 0,
  pendingCount: 0,
  uploadedCount: 0,
})

const recentOperations = ref([
  { type: '导入', description: '导入 50 个产品', time: '2024-04-23 10:30', status: 'success' },
  { type: '优化', description: 'AI 优化 30 个产品标题', time: '2024-04-23 09:15', status: 'success' },
  { type: '上传', description: '上传 20 个产品到 Shopify', time: '2024-04-22 16:45', status: 'success' },
])

onMounted(async () => {
  try {
    const [stores, products] = await Promise.all([
      storeApi.list(),
      productApi.list(),
    ])
    stats.value.storeCount = stores.length
    stats.value.productCount = products.total || 0
  } catch (e) {
    console.error('加载数据失败', e)
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  width: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.section-card {
  margin-top: 20px;
}

.section-card :deep(.el-card__header) {
  font-weight: 500;
  color: #303133;
}
</style>
