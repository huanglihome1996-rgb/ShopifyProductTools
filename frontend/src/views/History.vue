<template>
  <div class="history-page">
    <el-card>
      <template #header>
        <span>导入历史</span>
      </template>

      <el-table :data="history" stripe v-loading="loading">
        <el-table-column prop="batch_id" label="批次ID" width="180" />
        <el-table-column prop="source_type" label="来源类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.source_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source_name" label="来源名称" />
        <el-table-column label="统计" width="200">
          <template #default="{ row }">
            <span class="stat success">成功 {{ row.success_count }}</span>
            <span class="stat skip">跳过 {{ row.skip_count }}</span>
            <span class="stat fail">失败 {{ row.fail_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          :total="pagination.total"
          :page-size="20"
          layout="total, prev, pager, next"
          @change="loadHistory"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetail" title="导入详情" width="600px">
      <el-descriptions :column="2" border v-if="currentDetail">
        <el-descriptions-item label="批次ID">{{ currentDetail.batch_id }}</el-descriptions-item>
        <el-descriptions-item label="来源类型">{{ currentDetail.source_type }}</el-descriptions-item>
        <el-descriptions-item label="来源名称" :span="2">{{ currentDetail.source_name }}</el-descriptions-item>
        <el-descriptions-item label="成功数量">{{ currentDetail.success_count }}</el-descriptions-item>
        <el-descriptions-item label="跳过数量">{{ currentDetail.skip_count }}</el-descriptions-item>
        <el-descriptions-item label="失败数量">{{ currentDetail.fail_count }}</el-descriptions-item>
        <el-descriptions-item label="总数">{{ currentDetail.total_count }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ formatDate(currentDetail.started_at) }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ formatDate(currentDetail.finished_at) }}</el-descriptions-item>
        <el-descriptions-item label="错误日志" :span="2" v-if="currentDetail.error_log">
          <pre class="error-log">{{ currentDetail.error_log }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { importApi } from '@/api'

const history = ref<any[]>([])
const loading = ref(false)
const showDetail = ref(false)
const currentDetail = ref<any>(null)

const pagination = reactive({
  page: 1,
  total: 0,
})

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status] || status
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const loadHistory = async () => {
  loading.value = true
  try {
    const result = await importApi.listHistory({ page: pagination.page, page_size: 20 })
    history.value = result.items
    pagination.total = result.total
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const viewDetail = (item: any) => {
  currentDetail.value = item
  showDetail.value = true
}

onMounted(loadHistory)
</script>

<style scoped>
.history-page {
  max-width: 1200px;
}

.stat {
  margin-right: 10px;
  font-size: 13px;
}

.stat.success {
  color: #67C23A;
}

.stat.skip {
  color: #E6A23C;
}

.stat.fail {
  color: #F56C6C;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.error-log {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  font-size: 12px;
}
</style>